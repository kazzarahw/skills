#!/usr/bin/env bash
#
# Wiki Backup and Restore Script for Cyber Skills Wiki
#
# Provides backup, restore, and list functionality for wiki archives.
# Maintains a rolling window of the last 10 backups.
#
# Usage:
#   ./wiki-backup.sh backup [wiki_dir] [backup_dir]
#   ./wiki-backup.sh restore <backup_file> [wiki_dir]
#   ./wiki-backup.sh list [backup_dir]
#   ./wiki-backup.sh verify <backup_file>
#
# Environment Variables:
#   WIKI_DIR      - Default wiki directory (default: ./wiki)
#   BACKUP_DIR    - Default backup directory (default: ./backups)
#   MAX_BACKUPS   - Maximum backups to keep (default: 10)

set -euo pipefail

# Default configuration
WIKI_DIR="${WIKI_DIR:-./wiki}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
MAX_BACKUPS="${MAX_BACKUPS:-10}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Error handling
error_exit() {
    log_error "$1"
    exit 1
}

# Check dependencies
check_dependencies() {
    local deps=("tar" "gzip" "sha256sum" "date")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            error_exit "Required dependency not found: $dep"
        fi
    done
}

# Validate wiki directory
validate_wiki_dir() {
    local dir="$1"
    if [[ ! -d "$dir" ]]; then
        error_exit "Wiki directory not found: $dir"
    fi

    # Check if directory contains markdown files
    if ! find "$dir" -name "*.md" -print -quit | grep -q .; then
        log_warning "No markdown files found in: $dir"
    fi
}

# Create backup directory if it doesn't exist
ensure_backup_dir() {
    local dir="$1"
    if [[ ! -d "$dir" ]]; then
        log_info "Creating backup directory: $dir"
        mkdir -p "$dir" || error_exit "Failed to create backup directory: $dir"
    fi
}

# Generate backup filename
generate_backup_filename() {
    local wiki_dir="$1"
    local timestamp
    timestamp=$(date +"%Y%m%d_%H%M%S")
    local wiki_name
    wiki_name=$(basename "$wiki_dir")
    echo "${wiki_name}_${timestamp}.tar.gz"
}

# Create backup
cmd_backup() {
    local wiki_dir="${1:-$WIKI_DIR}"
    local backup_dir="${2:-$BACKUP_DIR}"

    log_info "Starting backup..."
    log_info "Wiki directory: $wiki_dir"
    log_info "Backup directory: $backup_dir"

    # Validate inputs
    validate_wiki_dir "$wiki_dir"
    ensure_backup_dir "$backup_dir"

    # Generate backup filename
    local backup_file
    backup_file=$(generate_backup_filename "$wiki_dir")
    local backup_path="${backup_dir}/${backup_file}"

    # Create backup
    log_info "Creating backup archive: $backup_file"

    # Create tar archive with metadata
    local temp_dir
    temp_dir=$(mktemp -d)
    trap "rm -rf '$temp_dir'" EXIT

    # Copy wiki to temp directory
    cp -r "$wiki_dir" "${temp_dir}/wiki"

    # Create metadata file
    cat > "${temp_dir}/metadata.txt" << EOF
Backup created: $(date -Iseconds)
Wiki directory: $(realpath "$wiki_dir")
Wiki name: $(basename "$wiki_dir")
File count: $(find "$wiki_dir" -type f | wc -l)
Total size: $(du -sh "$wiki_dir" | cut -f1)
EOF

    # Create tar archive
    tar -czf "$backup_path" -C "$temp_dir" . || error_exit "Failed to create backup archive"

    # Generate checksum
    local checksum
    checksum=$(sha256sum "$backup_path" | cut -d' ' -f1)
    echo "$checksum  $backup_file" > "${backup_path}.sha256"

    # Cleanup temp directory
    rm -rf "$temp_dir"
    trap - EXIT

    log_success "Backup created: $backup_path"
    log_info "Size: $(du -h "$backup_path" | cut -f1)"
    log_info "SHA256: $checksum"

    # Rotate old backups
    rotate_backups "$backup_dir"

    echo "$backup_path"
}

# Rotate old backups (keep only MAX_BACKUPS)
rotate_backups() {
    local backup_dir="$1"

    log_info "Rotating backups (keeping last $MAX_BACKUPS)..."

    # Get list of backups sorted by time (oldest first)
    local backups
    backups=$(find "$backup_dir" -name "*.tar.gz" -type f -printf '%T@ %p\n' | sort -n | cut -d' ' -f2-)

    local count
    count=$(echo "$backups" | grep -c . || true)

    if [[ $count -gt $MAX_BACKUPS ]]; then
        local to_delete=$((count - MAX_BACKUPS))
        log_info "Deleting $to_delete old backup(s)..."

        echo "$backups" | head -n "$to_delete" | while read -r old_backup; do
            log_info "Removing old backup: $(basename "$old_backup")"
            rm -f "$old_backup"
            rm -f "${old_backup}.sha256"
        done
    else
        log_info "No rotation needed ($count/$MAX_BACKUPS backups)"
    fi
}

# Verify backup integrity
cmd_verify() {
    local backup_file="$1"

    if [[ ! -f "$backup_file" ]]; then
        error_exit "Backup file not found: $backup_file"
    fi

    log_info "Verifying backup: $backup_file"

    # Check if it's a valid tar.gz
    if ! tar -tzf "$backup_file" &> /dev/null; then
        error_exit "Backup file is corrupted or not a valid tar.gz archive"
    fi

    # Verify checksum if available
    local checksum_file="${backup_file}.sha256"
    if [[ -f "$checksum_file" ]]; then
        log_info "Verifying checksum..."
        if sha256sum -c "$checksum_file" &> /dev/null; then
            log_success "Checksum verification passed"
        else
            error_exit "Checksum verification failed - backup may be corrupted"
        fi
    else
        log_warning "No checksum file found, skipping checksum verification"
    fi

    # Show backup contents summary
    log_info "Backup contents:"
    tar -tzf "$backup_file" | head -20
    local total_files
    total_files=$(tar -tzf "$backup_file" | wc -l)
    log_info "Total files in backup: $total_files"

    log_success "Backup verification completed"
}

# Restore backup
cmd_restore() {
    local backup_file="$1"
    local wiki_dir="${2:-$WIKI_DIR}"

    log_info "Starting restore..."
    log_info "Backup file: $backup_file"
    log_info "Target directory: $wiki_dir"

    # Validate backup
    if [[ ! -f "$backup_file" ]]; then
        error_exit "Backup file not found: $backup_file"
    fi

    # Verify backup integrity
    cmd_verify "$backup_file"

    # Create safety backup of current wiki if it exists
    if [[ -d "$wiki_dir" ]]; then
        log_warning "Current wiki directory exists, creating safety backup..."
        local safety_backup="${wiki_dir}.safety.$(date +%Y%m%d_%H%M%S)"
        cp -r "$wiki_dir" "$safety_backup"
        log_info "Safety backup created: $safety_backup"
    fi

    # Create temporary directory for extraction
    local temp_dir
    temp_dir=$(mktemp -d)
    trap "rm -rf '$temp_dir'" EXIT

    # Extract backup
    log_info "Extracting backup..."
    tar -xzf "$backup_file" -C "$temp_dir" || error_exit "Failed to extract backup"

    # Validate extracted content
    if [[ ! -d "${temp_dir}/wiki" ]]; then
        error_exit "Invalid backup structure: wiki directory not found in archive"
    fi

    # Move extracted wiki to target location
    log_info "Restoring wiki to: $wiki_dir"
    rm -rf "$wiki_dir"
    mv "${temp_dir}/wiki" "$wiki_dir"

    # Cleanup
    rm -rf "$temp_dir"
    trap - EXIT

    log_success "Restore completed successfully"
    log_info "Wiki restored to: $wiki_dir"
}

# List available backups
cmd_list() {
    local backup_dir="${1:-$BACKUP_DIR}"

    if [[ ! -d "$backup_dir" ]]; then
        log_warning "Backup directory not found: $backup_dir"
        return
    fi

    log_info "Available backups in: $backup_dir"
    echo ""

    # Header
    printf "%-40s %-15s %-20s %-10s\n" "FILENAME" "SIZE" "DATE" "STATUS"
    printf "%-40s %-15s %-20s %-10s\n" "--------" "----" "----" "------"

    # List backups
    find "$backup_dir" -name "*.tar.gz" -type f -printf '%T@ %p\n' | sort -rn | while read -r line; do
        local timestamp
        timestamp=$(echo "$line" | cut -d' ' -f1)
        local filepath
        filepath=$(echo "$line" | cut -d' ' -f2-)
        local filename
        filename=$(basename "$filepath")
        local size
        size=$(du -h "$filepath" | cut -f1)
        local date_str
        date_str=$(date -d "@$timestamp" +"%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "Unknown")

        # Check integrity
        local status="OK"
        if [[ -f "${filepath}.sha256" ]]; then
            if ! sha256sum -c "${filepath}.sha256" &> /dev/null; then
                status="CORRUPT"
            fi
        else
            status="NO_CHECKSUM"
        fi

        printf "%-40s %-15s %-20s %-10s\n" "$filename" "$size" "$date_str" "$status"
    done

    echo ""
    local count
    count=$(find "$backup_dir" -name "*.tar.gz" -type f | wc -l)
    log_info "Total backups: $count (max: $MAX_BACKUPS)"
}

# Show usage
usage() {
    cat << EOF
Wiki Backup and Restore Script

Usage:
    $0 backup [wiki_dir] [backup_dir]     Create a new backup
    $0 restore <backup_file> [wiki_dir]   Restore from backup
    $0 list [backup_dir]                   List available backups
    $0 verify <backup_file>                Verify backup integrity

Environment Variables:
    WIKI_DIR      - Default wiki directory (default: ./wiki)
    BACKUP_DIR    - Default backup directory (default: ./backups)
    MAX_BACKUPS   - Maximum backups to keep (default: 10)

Examples:
    # Create backup with defaults
    $0 backup

    # Create backup with custom directories
    $0 backup /path/to/wiki /path/to/backups

    # Restore from backup
    $0 restore /path/to/backups/wiki_20240101_120000.tar.gz

    # Restore to custom location
    $0 restore /path/to/backups/wiki_20240101_120000.tar.gz /path/to/wiki

    # List backups
    $0 list

    # Verify backup
    $0 verify /path/to/backups/wiki_20240101_120000.tar.gz
EOF
}

# Main function
main() {
    # Check dependencies
    check_dependencies

    # Parse command
    local command="${1:-}"
    shift || true

    case "$command" in
        backup)
            cmd_backup "$@"
            ;;
        restore)
            if [[ $# -lt 1 ]]; then
                error_exit "Usage: $0 restore <backup_file> [wiki_dir]"
            fi
            cmd_restore "$@"
            ;;
        list)
            cmd_list "$@"
            ;;
        verify)
            if [[ $# -lt 1 ]]; then
                error_exit "Usage: $0 verify <backup_file>"
            fi
            cmd_verify "$@"
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            log_error "Unknown command: $command"
            usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
