# Web2 Disk Forensics

Techniques for acquiring and analyzing disk images during incident response.

## Table of Contents

- [Disk Imaging](#disk-imaging)
- [File System Analysis](#file-system-analysis)
- [File Recovery](#file-recovery)
- [Timeline Analysis](#timeline-analysis)
- [Registry Analysis](#registry-analysis)
- [Tools](#tools)
- [Best Practices](#best-practices)

## Disk Imaging

### Linux Imaging

#### dd

```bash
# Basic disk imaging
dd if=/dev/sda of=/evidence/disk-sda.img bs=4M status=progress

# With hash verification
dd if=/dev/sda bs=4M | tee /evidence/disk-sda.img | sha256sum > /evidence/disk-sda.img.sha256

# Image specific partition
dd if=/dev/sda1 of=/evidence/partition-sda1.img bs=4M status=progress

# Image with error handling
dd if=/dev/sda of=/evidence/disk-sda.img bs=4M conv=noerror,sync status=progress
```

#### dc3dd

```bash
# Basic imaging with logging
dc3dd if=/dev/sda of=/evidence/disk-sda.img log=/evidence/dc3dd.log

# With hash verification
dc3dd if=/dev/sda of=/evidence/disk-sda.img hash=sha256 log=/evidence/dc3dd.log

# Image with chunking
dc3dd if=/dev/sda of=/evidence/disk-sda.img hash=sha256 log=/evidence/dc3dd.log \
  hlog=/evidence/hash.log

# Verify image
dc3dd if=/evidence/disk-sda.img hash=sha256 log=/evidence/verify.log
```

### Windows Imaging

#### FTK Imager

```bash
# GUI-based imaging
# 1. File → Create Disk Image
# 2. Select source (physical drive, logical drive, image file)
# 3. Select destination format (E01, AFF, raw)
# 4. Set compression level
# 5. Set fragment size
# 6. Start imaging

# Command-line (FTK Imager CLI)
ftkimager.exe --src \\.\PhysicalDrive0 --dest E:\evidence\disk.e01 \
  --compress 5 --frag 2GB --verify
```

#### EnCase

```bash
# EnCase command-line
# 1. Create case
# 2. Add evidence (physical drive, logical drive, image file)
# 3. Select acquisition options
# 4. Start acquisition
# 5. Verify with hash
```

### macOS Imaging

```bash
# Using dd
dd if=/dev/disk0 of=/evidence/disk0.img bs=4M status=progress

# Using Disk Utility
# 1. Open Disk Utility
# 2. Select drive
# 3. File → New Image → Image from [drive]
# 4. Choose format (read-only, compressed)
# 5. Save to evidence location
```

## File System Analysis

### NTFS

```bash
# Mount NTFS image (read-only)
mount -o ro,loop /evidence/disk-sda.img /mnt/forensics/

# List NTFS metadata
ntfsinfo /dev/loop0

# Extract MFT
nftlsmft /dev/loop0 > /evidence/mft.txt

# List files with timestamps
ntfsls -a /dev/loop0

# Extract specific file
ntfscat /dev/loop0 /path/to/file > /evidence/file

# Analyze NTFS journal
ntfsjournal /dev/loop0 > /evidence/usn-journal.txt
```

### ext4

```bash
# Mount ext4 image (read-only)
mount -o ro,loop /evidence/disk-sda.img /mnt/forensics/

# List files with timestamps
ls -la --time-style=full-iso /mnt/forensics/

# Extract specific file
cp /mnt/forensics/path/to/file /evidence/file

# Analyze ext4 journal
dumpe2fs /dev/loop0 | grep -i journal
debugfs -R "logdump -a" /dev/loop0 > /evidence/ext4-journal.txt
```

### APFS

```bash
# Mount APFS image (read-only)
mount -o ro,loop /evidence/disk-sda.img /mnt/forensics/

# List files with timestamps
ls -la --time-style=full-iso /mnt/forensics/

# Extract specific file
cp /mnt/forensics/path/to/file /evidence/file

# Analyze APFS snapshots
tmutil listlocalsnapshots /mnt/forensics/
```

### FAT32

```bash
# Mount FAT32 image (read-only)
mount -o ro,loop /evidence/disk-sda.img /mnt/forensics/

# List files with timestamps
ls -la --time-style=full-iso /mnt/forensics/

# Extract specific file
cp /mnt/forensics/path/to/file /evidence/file
```

## File Recovery

### Deleted Files

```bash
# Using extundelete (ext3/ext4)
extundelete /dev/loop0 --restore-all
extundelete /dev/loop0 --restore-file /path/to/file
extundelete /dev/loop0 --restore-directory /path/to/dir

# Using photorec
photorec /evidence/disk-sda.img
# Select partition → File Opt → Select file types → Recover

# Using foremost
foremost -t all -i /evidence/disk-sda.img -o /evidence/recovered/

# Using scalpel
scalpel /evidence/disk-sda.img -o /evidence/recovered/
# Edit /etc/scalpel/scalpel.conf for file types
```

### Unallocated Space

```bash
# Extract unallocated space
blkls /dev/loop0 > /evidence/unallocated.blkls

# Search for files in unallocated space
strings /evidence/unallocated.blkls | grep -i "file signature"

# Using photorec on unallocated space
photorec /evidence/unallocated.blkls
```

### Slack Space

```bash
# Extract slack space
blkls -s /dev/loop0 > /evidence/slack-space.txt

# Search for sensitive data in slack space
strings /evidence/slack-space.txt | grep -iE "(password|key|secret|token)"

# Using TSK (The Sleuth Kit)
blkcat /dev/loop0 <block_number> > /evidence/slack-block.bin
```

## Timeline Analysis

### MAC Times

| Time | Description | NTFS Attribute | ext4 Attribute |
|------|-------------|----------------|----------------|
| Modified | File content last modified | $STANDARD_INFORMATION | mtime |
| Accessed | File last accessed | $STANDARD_INFORMATION | atime |
| Changed | File metadata last changed | $STANDARD_INFORMATION | ctime |
| Created | File creation time | $FILE_NAME | crtime |

### Extracting MAC Times

```bash
# Using TSK (The Sleuth Kit)
fls -r -m / /dev/loop0 > /evidence/body-file.txt
mactime -b /evidence/body-file.txt -d > /evidence/timeline.csv

# Using NTFS
ntfsls -a -l /dev/loop0 > /evidence/ntfs-timeline.txt

# Using ext4
debugfs -R "stat /path/to/file" /dev/loop0
```

### Timeline Analysis Tools

```bash
# Using Plaso (log2timeline)
log2timeline.py --storage_file /evidence/timeline.plaso /evidence/disk-sda.img
psort.py /evidence/timeline.plaso -o l2tcsv -w /evidence/timeline.csv

# Using Timesketch
timesketch_importer.py /evidence/timeline.csv

# Using Autopsy
# GUI-based timeline analysis
# 1. Create case
# 2. Add data source
# 3. Run ingest modules
# 4. View timeline
```

## Registry Analysis

### RegRipper

```bash
# Run RegRipper on registry hive
rip.exe -r /evidence/REGISTRY/SYSTEM -f system > /evidence/system-report.txt
rip.exe -r /evidence/REGISTRY/SOFTWARE -f software > /evidence/software-report.txt
rip.exe -r /evidence/REGISTRY/SAM -f sam > /evidence/sam-report.txt
rip.exe -r /evidence/REGISTRY/NTUSER.DAT -f ntuser > /evidence/ntuser-report.txt

# Run all plugins
rip.exe -r /evidence/REGISTRY/SYSTEM -a > /evidence/system-all.txt
```

### Windows Registry Forensics

#### Key Registry Hives

| Hive | Location | Content |
|------|----------|---------|
| SYSTEM | C:\Windows\System32\config\SYSTEM | System configuration, services, devices |
| SOFTWARE | C:\Windows\System32\config\SOFTWARE | Installed software, settings |
| SAM | C:\Windows\System32\config\SAM | User accounts, password hashes |
| SECURITY | C:\Windows\System32\config\SECURITY | Security policy, audit settings |
| NTUSER.DAT | C:\Users\<user>\NTUSER.DAT | User preferences, recent files |
| UsrClass.dat | C:\Users\<user>\AppData\Local\Microsoft\Windows\UsrClass.dat | COM registrations, file associations |

#### Registry Analysis Commands

```bash
# Using reg.exe (live system)
reg export HKLM\SYSTEM\CurrentControlSet\Services /evidence/services.reg
reg export HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /evidence/run-keys.reg
reg export HKCU\Software\Microsoft\Windows\CurrentVersion\Run /evidence/user-run-keys.reg

# Using regshot (registry diff)
regshot -before before.reg
# Make changes
regshot -after after.reg
# Compare

# Using Python (python-registry)
python3 -c "
from Registry import Registry
reg = Registry.Registry('/evidence/REGISTRY/SYSTEM')
key = reg.open('ControlSet001\Services')
for subkey in key.subkeys():
    print(subkey.name())
"
```

#### Common Registry Locations for Forensics

```
# Persistence
HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce
HKCU\Software\Microsoft\Windows\CurrentVersion\Run
HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce
HKLM\SYSTEM\CurrentControlSet\Services

# User activity
HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs
HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\OpenSavePidlMRU
HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU

# USB devices
HKLM\SYSTEM\CurrentControlSet\Enum\USBSTOR
HKLM\SYSTEM\CurrentControlSet\Enum\USB

# Network
HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces
HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkList\Profiles

# Installed software
HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall
HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall
```

## Tools

### Autopsy

```bash
# Installation
sudo apt-get install autopsy

# Launch
autopsy

# Command-line (Autopsy 4.x)
# 1. Create case
# 2. Add data source
# 3. Run ingest modules
# 4. Analyze results
```

### SANS SIFT

```bash
# Installation
wget https://github.com/sans-dfir/sift-cli/releases/latest/download/sift-cli-linux
chmod +x sift-cli-linux
sudo ./sift-cli-linux install

# SIFT includes:
# - Autopsy
# - Plaso/log2timeline
# - Volatility
# - Rekall
# - TSK
# - RegRipper
# - And many more
```

### EnCase

```bash
# Commercial tool
# GUI-based forensic analysis
# Supports multiple file systems
# Advanced search and reporting
# Court-accepted tool
```

### FTK

```bash
# Commercial tool
# GUI-based forensic analysis
# Distributed processing
# Advanced search and reporting
# Court-accepted tool
```

### X-Ways Forensics

```bash
# Commercial tool
# Advanced disk editing
# File carving
# Registry analysis
# Court-accepted tool
```

## Best Practices

1. **Use write blockers** — Always use hardware or software write blockers
2. **Hash everything** — Calculate MD5, SHA-1, and SHA-256 hashes
3. **Work on copies** — Never analyze the original disk image
4. **Document everything** — Record all commands and findings
5. **Use multiple tools** — Cross-validate findings
6. **Preserve metadata** — Maintain file timestamps and permissions
7. **Chain of custody** — Document all handling of evidence
8. **Verify integrity** — Re-hash images before and after analysis
