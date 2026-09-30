#!/usr/bin/env bash
# wiki-backup.sh — Backup and restore the security wiki.
#
# Supports incremental backups, rotation of old backups, integrity
# verification, and restore operations.
#
# Usage:
#   wiki-backup.sh <wiki_path> <backup_path> [options]
#
# Options:
#   --incremental, -i     Incremental backup (only changed files)
#   --full, -f            Full backup (default)
#   --rotate, -N          Rotate old backups, keep N backups (default: 10)
#   --verify, -V          Verify backup integrity after creation
#   --restore, -R         Restore from backup
#   --restore-date DATE   Restore from specific date (YYYY-MM-DD)
#   --list, -L            List available backups
#   --compress, -c        Compress backup with gzip (default: on)
#   --no-compress         Disable compression
#   --encrypt, -e         Encrypt backup with GPG
#   --recipient KEY       GPG recipient for encryption
#   --dry-run             Show what would be done without executing
#   --verbose, -v         Verbose output
#   --help, -h            Show this help message
#
# Examples:
#   wiki-backup.sh /path/to/wiki /path/to/backups
#   wiki-backup.sh /path/to/wiki /path/to/backups -i -N 20
#   wiki-backup.sh /path/to/wiki /path/to/backups -R --restore-date 2026-09-15
#   wiki-backup.sh /path/to/wiki /path/to/backups -L

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_NAME=$(basename "$0")
VERSION="1.0.0"
DEFAULT_KEEP=10
DEFAULT_COMPRESS=true
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE_PREFIX=$(date +%Y-%m-%d)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# Helper Functions
# ============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_verbose() {
    if [[ "${VERBOSE:-false}" == "true" ]]; then
        echo -e "[VERBOSE] $1"
    fi
}

usage() {
    cat <<EOF
wiki-backup.sh v${VERSION} — Backup and restore the security wiki.

Usage:
    ${SCRIPT_NAME} <wiki_path> <backup_path> [options]

Arguments:
    wiki_path       Path to the wiki directory
    backup_path     Path to the backup storage directory

Options:
    --incremental, -i     Incremental backup (only changed files)
    --full, -f            Full backup (default)
    --rotate, -N          Rotate old backups, keep N backups (default: ${DEFAULT_KEEP})
    --verify, -V          Verify backup integrity after creation
    --restore, -R         Restore from backup
    --restore-date DATE   Restore from specific date (YYYY-MM-DD)
    --list, -L            List available backups
    --compress, -c        Compress backup with gzip (default: on)
    --no-compress         Disable compression
    --encrypt, -e         Encrypt backup with GPG
    --recipient KEY       GPG recipient for encryption
    --dry-run             Show what would be done without executing
    --verbose, -v         Verbose output
    --help, -h            Show this help message

Examples:
    # Full backup with verification
    ${SCRIPT_NAME} /path/to/wiki /path/to/backups -V

    # Incremental backup, keep 20 backups
    ${SCRIPT_NAME} /path/to/wiki /path/to/backups -i -N 20

    # Restore from specific date
    ${SCRIPT_NAME} /path/to/wiki /path/to/backups -R --restore-date 2026-09-15

    # List available backups
    ${SCRIPT_NAME} /path/to/wiki /path/to/backups -L

    # Encrypted backup
    ${SCRIPT_NAME} /path/to/wiki /path/to/backups -e --recipient security@example.com
EOF
}

# ============================================================================
# Validation Functions
# ============================================================================

validate_paths() {
    if [[ -z "${WIKI_PATH:-}" ]]; then
        log_error "Wiki path not specified"
        usage
        exit 1
    fi
    
    if [[ -z "${BACKUP_PATH:-}" ]]; then
        log_error "Backup path not specified"
        usage
        exit 1
    fi
    
    if [[ ! -d "$WIKI_PATH" ]]; then
        log_error "Wiki path does not exist: $WIKI_PATH"
        exit 1
    fi
    
    # Create backup directory if it doesn't exist
    if [[ ! -d "$BACKUP_PATH" ]]; then
        log_info "Creating backup directory: $BACKUP_PATH"
        if [[ "${DRY_RUN:-false}" != "true" ]]; then
            mkdir -p "$BACKUP_PATH"
        fi
    fi
}

# ============================================================================
# Backup Functions
# ============================================================================

get_backup_name() {
    local backup_type=$1
    echo "${DATE_PREFIX}_${backup_type}_${TIMESTAMP}"
}

perform_backup() {
    local backup_type=$1
    local backup_name
    backup_name=$(get_backup_name "$backup_type")
    local backup_dir="${BACKUP_PATH}/${backup_name}"
    
    log_info "Starting ${backup_type} backup: ${backup_name}"
    
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        log_info "[DRY RUN] Would create backup at: ${backup_dir}"
        return 0
    fi
    
    mkdir -p "$backup_dir"
    
    # Create backup metadata
    cat > "${backup_dir}/.backup_meta" <<EOF
backup_type: ${backup_type}
created: $(date -Iseconds)
wiki_path: ${WIKI_PATH}
hostname: $(hostname)
user: $(whoami)
EOF
    
    # Perform the backup
    if [[ "$backup_type" == "incremental" ]]; then
        perform_incremental_backup "$backup_dir"
    else
        perform_full_backup "$backup_dir"
    fi
    
    # Compress if enabled
    if [[ "${COMPRESS:-true}" == "true" ]]; then
        compress_backup "$backup_dir"
    fi
    
    # Encrypt if enabled
    if [[ "${ENCRYPT:-false}" == "true" ]]; then
        encrypt_backup "$backup_dir"
    fi
    
    # Verify if enabled
    if [[ "${VERIFY:-false}" == "true" ]]; then
        verify_backup "$backup_dir"
    fi
    
    log_success "Backup completed: ${backup_dir}"
    echo "$backup_dir"
}

perform_full_backup() {
    local backup_dir=$1
    
    log_info "Performing full backup..."
    
    # Use rsync for efficient copying
    if command -v rsync &>/dev/null; then
        rsync -av --delete \
            --exclude='.git/' \
            --exclude='.backup_meta' \
            "${WIKI_PATH}/" "${backup_dir}/"
    else
        # Fallback to cp
        cp -r "${WIKI_PATH}/"* "$backup_dir/" 2>/dev/null || true
    fi
    
    # Create manifest
    create_manifest "$backup_dir"
    
    log_success "Full backup completed"
}

perform_incremental_backup() {
    local backup_dir=$1
    
    log_info "Performing incremental backup..."
    
    # Find the most recent full backup
    local last_full_backup
    last_full_backup=$(find "$BACKUP_PATH" -maxdepth 1 -type d -name "*_full_*" | sort -r | head -1)
    
    if [[ -z "$last_full_backup" ]]; then
        log_warn "No previous full backup found, performing full backup instead"
        perform_full_backup "$backup_dir"
        return
    fi
    
    log_info "Using last full backup as base: $(basename "$last_full_backup")"
    
    # Use rsync with link-dest for incremental backup
    if command -v rsync &>/dev/null; then
        rsync -av --delete \
            --link-dest="$last_full_backup" \
            --exclude='.git/' \
            --exclude='.backup_meta' \
            "${WIKI_PATH}/" "${backup_dir}/"
    else
        # Fallback: copy only changed files
        log_warn "rsync not available, using cp fallback"
        cp -r "${WIKI_PATH}/"* "$backup_dir/" 2>/dev/null || true
    fi
    
    # Create manifest
    create_manifest "$backup_dir"
    
    log_success "Incremental backup completed"
}

create_manifest() {
    local backup_dir=$1
    local manifest_file="${backup_dir}/.manifest"
    
    log_verbose "Creating file manifest..."
    
    find "$backup_dir" -type f ! -name '.backup_meta' ! -name '.manifest' | while read -r file; do
        rel_path="${file#$backup_dir/}"
        checksum=$(sha256sum "$file" | cut -d' ' -f1)
        size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null || echo "0")
        mtime=$(stat -c%Y "$file" 2>/dev/null || stat -f%m "$file" 2>/dev/null || echo "0")
        echo "${checksum}|${size}|${mtime}|${rel_path}"
    done | sort > "$manifest_file"
    
    log_verbose "Manifest created: $(wc -l < "$manifest_file") files"
}

compress_backup() {
    local backup_dir=$1
    
    log_info "Compressing backup..."
    
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        log_info "[DRY RUN] Would compress: ${backup_dir}"
        return 0
    fi
    
    local tar_file="${backup_dir}.tar.gz"
    
    tar -czf "$tar_file" -C "$BACKUP_PATH" "$(basename "$backup_dir")"
    
    # Remove uncompressed directory
    rm -rf "$backup_dir"
    
    log_success "Backup compressed: ${tar_file}"
}

encrypt_backup() {
    local backup_dir=$1
    
    log_info "Encrypting backup..."
    
    if ! command -v gpg &>/dev/null; then
        log_error "GPG not found, cannot encrypt backup"
        exit 1
    fi
    
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        log_info "[DRY RUN] Would encrypt: ${backup_dir}"
        return 0
    fi
    
    local recipient_arg=""
    if [[ -n "${RECIPIENT:-}" ]]; then
        recipient_arg="--recipient ${RECIPIENT}"
    fi
    
    # Encrypt the tar.gz file
    local tar_file="${backup_dir}.tar.gz"
    if [[ -f "$tar_file" ]]; then
        gpg --encrypt --trust-model always $recipient_arg --output "${tar_file}.gpg" "$tar_file"
        rm -f "$tar_file"
        log_success "Backup encrypted: ${tar_file}.gpg"
    else
        # Encrypt directory contents
        tar -czf - -C "$BACKUP_PATH" "$(basename "$backup_dir")" | \
            gpg --encrypt --trust-model always $recipient_arg --output "${backup_dir}.tar.gz.gpg"
        rm -rf "$backup_dir"
        log_success "Backup encrypted: ${backup_dir}.tar.gz.gpg"
    fi
}

# ============================================================================
# Verification Functions
# ============================================================================

verify_backup() {
    local backup_dir=$1
    
    log_info "Verifying backup integrity..."
    
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        log_info "[DRY RUN] Would verify: ${backup_dir}"
        return 0
    fi
    
    local manifest_file="${backup_dir}/.manifest"
    
    if [[ ! -f "$manifest_file" ]]; then
        log_warn "Manifest not found, skipping verification"
        return 0
    fi
    
    local errors=0
    local checked=0
    
    while IFS='|' read -r expected_checksum expected_size expected_mtime rel_path; do
        local file="${backup_dir}/${rel_path}"
        
        if [[ ! -f "$file" ]]; then
            log_error "Missing file: ${rel_path}"
            ((errors++))
            continue
        fi
        
        local actual_checksum
        actual_checksum=$(sha256sum "$file" | cut -d' ' -f1)
        
        if [[ "$actual_checksum" != "$expected_checksum" ]]; then
            log_error "Checksum mismatch: ${rel_path}"
            ((errors++))
        fi
        
        ((checked++))
    done < "$manifest_file"
    
    if [[ $errors -eq 0 ]]; then
        log_success "Verification passed: ${checked} files checked"
    else
        log_error "Verification failed: ${errors} errors found"
        return 1
    fi
}

# ============================================================================
# Rotation Functions
# ============================================================================

rotate_backups() {
    local keep_count=${1:-$DEFAULT_KEEP}
    
    log_info "Rotating backups (keeping ${keep_count} most recent)..."
    
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        log_info "[DRY RUN] Would rotate backups in: ${BACKUP_PATH}"
        return 0
    fi
    
    # List all backups sorted by date (newest first)
    local backups
    backups=$(find "$BACKUP_PATH" -maxdepth 1 -type d -name "*_full_*" -o -name "*_incremental_*" | sort -r)
    
    local count=0
    local removed=0
    
    while IFS= read -r backup; do
        ((count++))
        if [[ $count -gt $keep_count ]]; then
            log_info "Removing old backup: $(basename "$backup")"
            rm -rf "$backup"
            # Also remove compressed/encrypted versions
            rm -f "${backup}.tar.gz" "${backup}.tar.gz.gpg"
            ((removed++))
        fi
    done <<< "$backups"
    
    log_success "Rotation complete: ${removed} backup(s) removed"
}

# ============================================================================
# Restore Functions
# ============================================================================

list_backups() {
    log_info "Available backups in ${BACKUP_PATH}:"
    
    if [[ ! -d "$BACKUP_PATH" ]]; then
        log_error "Backup path does not exist: $BACKUP_PATH"
        exit 1
    fi
    
    local found=false
    
    # List directory backups
    for backup in $(find "$BACKUP_PATH" -maxdepth 1 -type d -name "*_full_*" -o -name "*_incremental_*" | sort -r); do
        found=true
        local name
        name=$(basename "$backup")
        local size
        size=$(du -sh "$backup" 2>/dev/null | cut -f1)
        local file_count
        file_count=$(find "$backup" -type f | wc -l)
        echo "  [DIR]  ${name} (${size}, ${file_count} files)"
    done
    
    # List compressed backups
    for backup in $(find "$BACKUP_PATH" -maxdepth 1 -name "*.tar.gz" | sort -r); do
        found=true
        local name
        name=$(basename "$backup")
        local size
        size=$(du -sh "$backup" 2>/dev/null | cut -f1)
        echo "  [GZ]   ${name} (${size})"
    done
    
    # List encrypted backups
    for backup in $(find "$BACKUP_PATH" -maxdepth 1 -name "*.gpg" | sort -r); do
        found=true
        local name
        name=$(basename "$backup")
        local size
        size=$(du -sh "$backup" 2>/dev/null | cut -f1)
        echo "  [GPG]  ${name} (${size})"
    done
    
    if [[ "$found" == "false" ]]; then
        log_warn "No backups found"
    fi
}

restore_backup() {
    local restore_date="${RESTORE_DATE:-}"
    
    if [[ -z "$restore_date" ]]; then
        # Use most recent backup
        log_info "No date specified, using most recent backup"
        local most_recent
        most_recent=$(find "$BACKUP_PATH" -maxdepth 1 -type d -name "*_full_*" -o -name "*_incremental_*" | sort -r | head -1)
        
        if [[ -z "$most_recent" ]]; then
            # Try compressed backups (including encrypted)
            most_recent=$(find "$BACKUP_PATH" -maxdepth 1 -name "*.tar.gz*" | sort -r | head -1)
        fi
        
        if [[ -z "$most_recent" ]]; then
            log_error "No backups found to restore"
            exit 1
        fi
        
        do_restore "$most_recent"
    else
        # Find backup matching date
        local matching_backup
        matching_backup=$(find "$BACKUP_PATH" -maxdepth 1 -type d -name "${restore_date}_*" | head -1)
        
        if [[ -z "$matching_backup" ]]; then
            # Try compressed backups (including encrypted)
            matching_backup=$(find "$BACKUP_PATH" -maxdepth 1 -name "${restore_date}_*.tar.gz*" | head -1)
        fi
        
        if [[ -z "$matching_backup" ]]; then
            log_error "No backup found for date: ${restore_date}"
            exit 1
        fi
        
        do_restore "$matching_backup"
    fi
}

do_restore() {
    local backup_path=$1
    
    log_info "Restoring from: ${backup_path}"
    
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        log_info "[DRY RUN] Would restore from: ${backup_path}"
        return 0
    fi
    
    # Safety check: don't overwrite without confirmation
    if [[ -d "$WIKI_PATH" ]] && [[ -n "$(ls -A "$WIKI_PATH" 2>/dev/null)" ]]; then
        log_warn "Wiki directory is not empty: ${WIKI_PATH}"
        read -p "Overwrite existing files? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Restore cancelled"
            exit 0
        fi
    fi
    
    # Decrypt if needed (handles both .gpg and .tar.gz.gpg)
    local restore_source="$backup_path"
    if [[ "$backup_path" == *.gpg ]]; then
        log_info "Decrypting backup..."
        local decrypted="${backup_path%.gpg}"
        gpg --decrypt --output "$decrypted" "$backup_path"
        restore_source="$decrypted"
    fi
    
    # Decompress if needed
    if [[ "$restore_source" == *.tar.gz ]]; then
        log_info "Decompressing backup..."
        local temp_dir
        temp_dir=$(mktemp -d)
        tar -xzf "$restore_source" -C "$temp_dir"
        
        # Find the actual backup directory inside
        local inner_dir
        inner_dir=$(find "$temp_dir" -maxdepth 1 -type d | tail -1)
        
        if [[ -z "$inner_dir" ]]; then
            log_error "Invalid backup structure"
            rm -rf "$temp_dir"
            exit 1
        fi
        
        restore_source="$inner_dir"
    fi
    
    # Perform restore
    log_info "Copying files to: ${WIKI_PATH}"
    mkdir -p "$WIKI_PATH"
    
    if command -v rsync &>/dev/null; then
        rsync -av --delete "${restore_source}/" "${WIKI_PATH}/"
    else
        rm -rf "${WIKI_PATH:?}/"*
        cp -r "${restore_source}/"* "${WIKI_PATH}/" 2>/dev/null || true
    fi
    
    # Cleanup decrypted file if we created one
    if [[ "$backup_path" == *.gpg ]]; then
        rm -f "${backup_path%.gpg}"
    fi
    
    log_success "Restore completed successfully"
}

# ============================================================================
# Main
# ============================================================================

main() {
    # Parse arguments
    if [[ $# -lt 2 ]]; then
        usage
        exit 1
    fi
    
    WIKI_PATH=$1
    BACKUP_PATH=$2
    shift 2
    
    # Default values
    BACKUP_TYPE="full"
    COMPRESS=true
    ENCRYPT=false
    VERIFY=false
    DRY_RUN=false
    VERBOSE=false
    RESTORE=false
    LIST=false
    ROTATE=false
    KEEP=$DEFAULT_KEEP
    RESTORE_DATE=""
    RECIPIENT=""
    
    # Parse options
    while [[ $# -gt 0 ]]; do
        case $1 in
            -i|--incremental)
                BACKUP_TYPE="incremental"
                shift
                ;;
            -f|--full)
                BACKUP_TYPE="full"
                shift
                ;;
            -N|--rotate)
                ROTATE=true
                if [[ -n "${2:-}" ]] && [[ "$2" =~ ^[0-9]+$ ]]; then
                    KEEP=$2
                    shift 2
                else
                    shift
                fi
                ;;
            -V|--verify)
                VERIFY=true
                shift
                ;;
            -R|--restore)
                RESTORE=true
                shift
                ;;
            --restore-date)
                RESTORE_DATE=$2
                shift 2
                ;;
            -L|--list)
                LIST=true
                shift
                ;;
            -c|--compress)
                COMPRESS=true
                shift
                ;;
            --no-compress)
                COMPRESS=false
                shift
                ;;
            -e|--encrypt)
                ENCRYPT=true
                shift
                ;;
            --recipient)
                RECIPIENT=$2
                shift 2
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
    
    # Export variables for functions
    export WIKI_PATH BACKUP_PATH BACKUP_TYPE COMPRESS ENCRYPT VERIFY
    export DRY_RUN VERBOSE RESTORE LIST ROTATE KEEP RESTORE_DATE RECIPIENT
    
    # Validate paths
    validate_paths
    
    # Execute command
    if [[ "$LIST" == "true" ]]; then
        list_backups
        exit 0
    fi
    
    if [[ "$RESTORE" == "true" ]]; then
        restore_backup
        exit 0
    fi
    
    # Perform backup
    perform_backup "$BACKUP_TYPE"
    
    # Rotate if requested
    if [[ "$ROTATE" == "true" ]]; then
        rotate_backups "$KEEP"
    fi
}

main "$@"
