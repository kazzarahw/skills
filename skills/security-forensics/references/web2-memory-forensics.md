# Web2 Memory Forensics

Techniques for acquiring and analyzing volatile memory during incident response.

## Table of Contents

- [Memory Acquisition](#memory-acquisition)
- [Volatility Framework](#volatility-framework)
- [Memory Analysis Patterns](#memory-analysis-patterns)
- [Credential Extraction from Memory](#credential-extraction-from-memory)
- [Timeline Analysis from Memory](#timeline-analysis-from-memory)
- [Tools](#tools)
- [Best Practices](#best-practices)

## Memory Acquisition

### Linux Memory Acquisition

#### LiME (Linux Memory Extractor)

```bash
# Load LiME kernel module (compile first)
insmod lime.ko "path=/evidence/lime-mem.lime format=lime"

# Acquisition over network (avoid writing to disk)
insmod lime.ko "path=tcp:4444 format=lime"

# Receive on remote host
nc -l -p 4444 > /evidence/lime-mem.lime

# Acquisition to USB drive (write-blocked)
insmod lime.ko "path=/mnt/usb/lime-mem.lime format=lime"
```

**Advantages:** Kernel-level acquisition, minimal footprint, supports multiple formats
**Disadvantages:** Requires kernel module compilation, may trigger anti-rootkit detection

#### /dev/crash (Crash Dump)

```bash
# Configure kdump
systemctl enable kdump
systemctl start kdump

# Trigger memory dump (for testing)
echo c > /proc/sysrq-trigger

# Dump location
ls -la /var/crash/
```

### Windows Memory Acquisition

#### WinPmem

```bash
# Acquire memory to file
win_pmem.exe -o /evidence/winpmem.raw

# Acquire with compression
win_pmem.exe -c -o /evidence/winpmem.lime

# Acquire specific range
win_pmem.exe -o /evidence/winpmem.raw --range 0x0-0x100000000
```

#### DumpIt

```bash
# Simple one-click acquisition
DumpIt.exe /O /evidence/dumpit.raw

# Silent mode
DumpIt.exe /Q /O /evidence/dumpit.raw
```

#### FTK Imager

```bash
# GUI-based acquisition
# 1. File → Acquire Memory
# 2. Select destination
# 3. Choose format (raw, Lime, EWF)
# 4. Start acquisition
```

### macOS Memory Acquisition

```bash
# Using osxpmem (requires SIP disable)
sudo osxpmem -o /evidence/osxpmem.raw

# Using MacQuisition (Cellebrite)
# GUI-based acquisition with chain of custody
```

## Volatility Framework

### Volatility 3

#### Process Enumeration

```bash
# List all processes
volatility3 -f /evidence/memory.raw windows.pslist

# Process tree
volatility3 -f /evidence/memory.raw windows.pstree

# Process details with command line
volatility3 -f /evidence/memory.raw windows.cmdline

# Process with specific name
volatility3 -f /evidence/memory.raw windows.pslist | grep -i "cmd.exe"

# DLLs loaded by process
volatility3 -f /evidence/memory.raw windows.dlllist --pid 1234

# Process handles
volatility3 -f /evidence/memory.raw windows.handles --pid 1234
```

#### Network Connections

```bash
# Network connections (Windows)
volatility3 -f /evidence/memory.raw windows.netstat

# Network connections (Linux)
volatility3 -f /evidence/memory.raw linux.netstat

# Sockets
volatility3 -f /evidence/memory.raw windows.sockets

# Scan for network artifacts
volatility3 -f /evidence.memory.raw windows.netscan
```

#### DLL Injection Detection

```bash
# List loaded DLLs for all processes
volatility3 -f /evidence/memory.raw windows.dlllist

# Find DLLs loaded from unusual paths
volatility3 -f /evidence/memory.raw windows.dlllist | grep -v "C:\\Windows\\System32"

# Check for DLL hijacking
volatility3 -f /evidence/memory.raw windows.dlllist | grep -i "temp\|appdata\|downloads"

# Verify DLL signatures
volatility3 -f /evidence/memory.raw windows.verinfo
```

#### Rootkit Detection

```bash
# Check for hidden processes
volatility3 -f /evidence/memory.raw windows.psxview

# Check for process injection
volatility3 -f /evidence/memory.raw windows.malfind

# Check for hooked functions
volatility3 -f /evidence/memory.raw windows.apihooks

# Check for SSDT hooks
volatility3 -f /evidence/memory.raw windows.ssdt

# Check for driver anomalies
volatility3 -f /evidence/memory.raw windows.driverscan

# Check for callback routines
volatility3 -f /evidence/memory.raw windows.callbacks
```

### Volatility 2 (Legacy)

```bash
# Process list
volatility -f /evidence/memory.raw --profile=Win7SP1x64 pslist

# Network connections
volatility -f /evidence/memory.raw --profile=Win7SP1x64 netscan

# Malfind (code injection)
volatility -f /evidence/memory.raw --profile=Win7SP1x64 malfind

# API hooks
volatility -f /evidence/memory.raw --profile=Win7SP1x64 apihooks

# SSDT hooks
volatility -f /evidence/memory.raw --profile=Win7SP1x64 ssdt

# Driver scan
volatility -f /evidence/memory.raw --profile=Win7SP1x64 driverscan

# Callbacks
volatility -f /evidence/memory.raw --profile=Win7SP1x64 callbacks
```

## Memory Analysis Patterns

### Process Hollowing

**Indicators:**
- Process with legitimate name but suspicious parent
- Memory region with RWX permissions
- Mismatch between on-disk and in-memory PE headers
- Unusual memory mappings

**Detection:**
```bash
# Find processes with RWX memory regions
volatility3 -f /evidence/memory.raw windows.vadinfo | grep -i "READWRITEEXECUTE"

# Check for process hollowing
volatility3 -f /evidence/memory.raw windows.malfind

# Compare in-memory PE with on-disk
volatility3 -f /evidence/memory.raw windows.pslist
# Then dump and compare
volatility3 -f /evidence/memory.raw windows.procdump --pid 1234
```

### Code Injection

**Indicators:**
- Executable memory in non-executable processes
- Memory regions backed by unknown files
- Unusual thread start addresses

**Detection:**
```bash
# Find injected code
volatility3 -f /evidence/memory.raw windows.malfind

# Check thread start addresses
volatility3 -f /evidence/memory.raw windows.thrdscan

# Find remote threads
volatility3 -f /evidence/memory.raw windows.timers
```

### API Hooking

**Indicators:**
- Modified function prologues
- JMP instructions to unexpected locations
- Modified IAT/EAT entries

**Detection:**
```bash
# Find API hooks
volatility3 -f /evidence/memory.raw windows.apihooks

# Check IAT hooks
volatility3 -f /evidence/memory.raw windows.iat

# Find inline hooks
volatility3 -f /evidence/memory.raw windows.apihooks | grep -i "inline"
```

## Credential Extraction from Memory

### LSASS Dumping

```bash
# Dump LSASS process memory
volatility3 -f /evidence/memory.raw windows.lsass --pid 1234

# Using procdump
procdump.exe -ma lsass.exe /evidence/lsass.dmp

# Using comsvcs.dll
rundll32.exe C:\Windows\System32\comsvcs.dll, MiniDump 1234 C:\evidence\lsass.dmp full
```

### Mimikatz

```bash
# Run Mimikatz on live system (for testing only)
mimikatz.exe
mimikatz # privilege::debug
mimikatz # sekurlsa::logonpasswords
mimikatz # sekurlsa::tickets
mimikatz # lsadump::sam
mimikatz # token::elevate

# Extract credentials from memory dump
mimikatz.exe "sekurlsa::minidump lsass.dmp" "sekurlsa::logonpasswords"
```

### Credential Types in Memory

| Credential Type | Location | Tool |
|-----------------|----------|------|
| NTLM hashes | LSASS | Mimikatz |
| Kerberos tickets | LSASS | Mimikatz |
| Plaintext passwords | LSASS (WDigest) | Mimikatz |
| SAM database | Registry | Mimikatz |
| LSA secrets | Registry | Mimikatz |
| DPAPI keys | Various | Mimikatz |
| Browser credentials | Browser process | Custom tools |
| SSH keys | Memory | Volatility plugins |

## Timeline Analysis from Memory

### Process Timeline

```bash
# Get process creation times
volatility3 -f /evidence/memory.raw windows.pslist

# Get process exit times
volatility3 -f /evidence/memory.raw windows.pslist | grep -i "exit"

# Get thread creation times
volatility3 -f /evidence/memory.raw windows.thrdscan

# Get socket creation times
volatility3 -f /evidence/memory.raw windows.netstat
```

### File Timeline

```bash
# Get file open times
volatility3 -f /evidence/memory.raw windows.filescan

# Get file mapping times
volatility3 -f /evidence/memory.raw windows.malfind

# Get registry key access times
volatility3 -f /evidence/memory.raw windows.registry.hivelist
```

## Tools

### Volatility 3

```bash
# Installation
pip install volatility3

# Basic usage
volatility3 -f <memory_dump> <plugin>

# List all plugins
volatility3 -f <memory_dump> --info

# Export all data
volatility3 -f <memory_dump> --export json -o /evidence/export.json
```

### Rekall

```bash
# Process list
rekall -f /evidence/memory.raw pslist

# Network connections
rekall -f /evidence/memory.raw netstat

# Malfind
rekall -f /evidence/memory.raw malfind

# API hooks
rekall -f /evidence/memory.raw apihooks
```

### MemProcFS

```bash
# Mount memory dump as filesystem
memprocfs.exe -device /evidence/memory.raw

# Access via mounted drive
# Processes: M:\proc\
# Files: M:\files\
# Registry: M:\registry\
# Network: M:\net\
```

## Best Practices

1. **Acquire memory first** — Memory is volatile; capture before any other action
2. **Use write blockers** — Prevent modification of the source system
3. **Document the acquisition** — Record tool version, method, timestamp
4. **Hash the memory dump** — SHA-256 hash immediately after acquisition
5. **Work on copies** — Never analyze the original memory dump
6. **Use multiple tools** — Cross-validate findings with different tools
7. **Document all commands** — Record every command for reproducibility
