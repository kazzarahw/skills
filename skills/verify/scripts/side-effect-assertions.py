#!/usr/bin/env python3
"""
side-effect-assertions.py — Library of side-effect assertions
Part of the verify skill

Provides deterministic side-effect assertion functions for verifying
security findings across web2 and web3 targets.

Usage:
    from side_effect_assertions import (
        assert_file_exists,
        assert_command_output,
        assert_network_callback,
        assert_process_running,
        assert_port_open,
        assert_http_response,
        assert_onchain_state_change,
        assert_transaction_verified,
    )

Each function returns an AssertionResult with:
    - passed: bool
    - message: str
    - evidence: dict
"""

import subprocess
import socket
import time
import json
import os
import re
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Callable
from pathlib import Path


@dataclass
class AssertionResult:
    """Result of a side-effect assertion."""
    passed: bool
    message: str
    evidence: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "message": self.message,
            "evidence": self.evidence,
        }

    def __bool__(self) -> bool:
        return self.passed


# ============================================================================
# File Existence Check
# ============================================================================

def assert_file_exists(
    file_path: str,
    min_size: int = 0,
    max_age_seconds: Optional[float] = None,
) -> AssertionResult:
    """
    Assert that a file exists on the filesystem.

    Args:
        file_path: Path to the file to check.
        min_size: Minimum file size in bytes (default: 0).
        max_age_seconds: Maximum age of the file in seconds (default: None).

    Returns:
        AssertionResult with passed=True if the file exists and meets criteria.

    Example:
        >>> result = assert_file_exists("/tmp/pwned.txt")
        >>> if result:
        ...     print("File exists!")
        >>> print(result.evidence["size"])
        1024
    """
    path = Path(file_path)

    if not path.exists():
        return AssertionResult(
            passed=False,
            message=f"File does not exist: {file_path}",
            evidence={"file_path": file_path, "exists": False},
        )

    if not path.is_file():
        return AssertionResult(
            passed=False,
            message=f"Path exists but is not a file: {file_path}",
            evidence={"file_path": file_path, "is_file": False},
        )

    size = path.stat().st_size
    if size < min_size:
        return AssertionResult(
            passed=False,
            message=f"File size {size} is less than minimum {min_size}",
            evidence={"file_path": file_path, "size": size, "min_size": min_size},
        )

    if max_age_seconds is not None:
        age = time.time() - path.stat().st_mtime
        if age > max_age_seconds:
            return AssertionResult(
                passed=False,
                message=f"File age {age:.1f}s exceeds maximum {max_age_seconds}s",
                evidence={"file_path": file_path, "age": age, "max_age": max_age_seconds},
            )

    return AssertionResult(
        passed=True,
        message=f"File exists: {file_path} (size: {size} bytes)",
        evidence={
            "file_path": file_path,
            "exists": True,
            "size": size,
            "mtime": path.stat().st_mtime,
        },
    )


# ============================================================================
# Command Output Check
# ============================================================================

def assert_command_output(
    command: str,
    expected_pattern: Optional[str] = None,
    expected_output: Optional[str] = None,
    timeout: int = 30,
    shell: bool = True,
) -> AssertionResult:
    """
    Assert that a command produces the expected output.

    Args:
        command: Command to execute.
        expected_pattern: Regex pattern to search for in output (default: None).
        expected_output: Exact output to match (default: None).
        timeout: Command timeout in seconds (default: 30).
        shell: Whether to use shell execution (default: True).

    Returns:
        AssertionResult with passed=True if the output matches.

    Example:
        >>> result = assert_command_output(
        ...     "cat /etc/passwd",
        ...     expected_pattern=r"root:"
        ... )
        >>> if result:
        ...     print("Command output matches!")
    """
    try:
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return AssertionResult(
            passed=False,
            message=f"Command timed out after {timeout}s: {command}",
            evidence={"command": command, "timeout": timeout},
        )
    except Exception as e:
        return AssertionResult(
            passed=False,
            message=f"Command failed: {e}",
            evidence={"command": command, "error": str(e)},
        )

    stdout = result.stdout
    stderr = result.stderr
    exit_code = result.returncode

    evidence = {
        "command": command,
        "exit_code": exit_code,
        "stdout": stdout,
        "stderr": stderr,
    }

    if expected_output is not None:
        if stdout.strip() != expected_output.strip():
            return AssertionResult(
                passed=False,
                message=f"Output does not match expected",
                evidence={**evidence, "expected": expected_output},
            )

    if expected_pattern is not None:
        if not re.search(expected_pattern, stdout, re.MULTILINE):
            return AssertionResult(
                passed=False,
                message=f"Pattern '{expected_pattern}' not found in output",
                evidence={**evidence, "pattern": expected_pattern},
            )

    return AssertionResult(
        passed=True,
        message=f"Command output matches: {command}",
        evidence=evidence,
    )


# ============================================================================
# Network Callback Check
# ============================================================================

def assert_network_callback(
    port: int,
    timeout: int = 10,
    expected_data: Optional[str] = None,
    host: str = "0.0.0.0",
) -> AssertionResult:
    """
    Assert that a network callback is received on a port.

    Args:
        port: Port to listen on.
        timeout: Timeout in seconds (default: 10).
        expected_data: Expected data in callback (default: None).
        host: Host to listen on (default: "0.0.0.0").

    Returns:
        AssertionResult with passed=True if a callback is received.

    Example:
        >>> # Start listener in background
        >>> import threading
        >>> def check_callback():
        ...     return assert_network_callback(4444, timeout=30)
        >>> # Run exploit, then check
        >>> result = check_callback()
    """
    received_data = []
    callback_received = False

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(1)
        sock.settimeout(timeout)

        try:
            conn, addr = sock.accept()
            callback_received = True
            data = conn.recv(4096).decode("utf-8", errors="replace")
            received_data.append(data)
            conn.close()
        except socket.timeout:
            pass
        finally:
            sock.close()
    except Exception as e:
        return AssertionResult(
            passed=False,
            message=f"Network callback check failed: {e}",
            evidence={"port": port, "error": str(e)},
        )

    if not callback_received:
        return AssertionResult(
            passed=False,
            message=f"No callback received on port {port} within {timeout}s",
            evidence={"port": port, "timeout": timeout},
        )

    data = received_data[0] if received_data else ""

    if expected_data is not None and expected_data not in data:
        return AssertionResult(
            passed=False,
            message=f"Callback data does not match expected",
            evidence={
                "port": port,
                "received": data,
                "expected": expected_data,
            },
        )

    return AssertionResult(
        passed=True,
        message=f"Callback received on port {port}",
        evidence={
            "port": port,
            "data": data,
            "data_length": len(data),
        },
    )


def assert_network_callback_async(
    port: int,
    callback_func: Callable[[], None],
    timeout: int = 30,
    expected_data: Optional[str] = None,
) -> AssertionResult:
    """
    Assert that a network callback is received while executing a function.

    This variant runs the callback function in a thread while listening.

    Args:
        port: Port to listen on.
        callback_func: Function to execute while listening.
        timeout: Timeout in seconds (default: 30).
        expected_data: Expected data in callback (default: None).

    Returns:
        AssertionResult with passed=True if a callback is received.

    Example:
        >>> def exploit():
        ...     subprocess.run(["curl", "http://localhost:4444/exploit"])
        >>> result = assert_network_callback_async(4444, exploit, timeout=30)
    """
    import threading

    received_data = []
    callback_received = False

    def listener():
        nonlocal callback_received, received_data
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("0.0.0.0", port))
            sock.listen(1)
            sock.settimeout(timeout)
            try:
                conn, addr = sock.accept()
                callback_received = True
                data = conn.recv(4096).decode("utf-8", errors="replace")
                received_data.append(data)
                conn.close()
            except socket.timeout:
                pass
            finally:
                sock.close()
        except Exception:
            pass

    listener_thread = threading.Thread(target=listener)
    listener_thread.start()

    # Execute the callback function
    try:
        callback_func()
    except Exception as e:
        listener_thread.join(timeout=1)
        return AssertionResult(
            passed=False,
            message=f"Callback function failed: {e}",
            evidence={"port": port, "error": str(e)},
        )

    listener_thread.join(timeout=timeout)

    if not callback_received:
        return AssertionResult(
            passed=False,
            message=f"No callback received on port {port} within {timeout}s",
            evidence={"port": port, "timeout": timeout},
        )

    data = received_data[0] if received_data else ""

    if expected_data is not None and expected_data not in data:
        return AssertionResult(
            passed=False,
            message=f"Callback data does not match expected",
            evidence={
                "port": port,
                "received": data,
                "expected": expected_data,
            },
        )

    return AssertionResult(
        passed=True,
        message=f"Callback received on port {port}",
        evidence={
            "port": port,
            "data": data,
            "data_length": len(data),
        },
    )


# ============================================================================
# Process Check
# ============================================================================

def assert_process_running(
    process_name: str,
    min_count: int = 1,
) -> AssertionResult:
    """
    Assert that a process is running.

    Args:
        process_name: Name of the process to check.
        min_count: Minimum number of matching processes (default: 1).

    Returns:
        AssertionResult with passed=True if the process is running.

    Example:
        >>> result = assert_process_running("nginx")
        >>> if result:
        ...     print("nginx is running!")
    """
    try:
        result = subprocess.run(
            ["pgrep", "-f", process_name],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception as e:
        return AssertionResult(
            passed=False,
            message=f"Process check failed: {e}",
            evidence={"process_name": process_name, "error": str(e)},
        )

    pids = [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
    count = len(pids)

    if count < min_count:
        return AssertionResult(
            passed=False,
            message=f"Process '{process_name}' not running (found {count}, need {min_count})",
            evidence={"process_name": process_name, "count": count, "min_count": min_count},
        )

    return AssertionResult(
        passed=True,
        message=f"Process '{process_name}' is running ({count} instances)",
        evidence={
            "process_name": process_name,
            "count": count,
            "pids": pids,
        },
    )


# ============================================================================
# Port Check
# ============================================================================

def assert_port_open(
    host: str,
    port: int,
    timeout: int = 5,
    protocol: str = "tcp",
) -> AssertionResult:
    """
    Assert that a port is open.

    Args:
        host: Host to check.
        port: Port to check.
        timeout: Timeout in seconds (default: 5).
        protocol: Protocol to check ("tcp" or "udp", default: "tcp").

    Returns:
        AssertionResult with passed=True if the port is open.

    Example:
        >>> result = assert_port_open("127.0.0.1", 8080)
        >>> if result:
        ...     print("Port 8080 is open!")
    """
    try:
        if protocol == "tcp":
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()

        if result != 0:
            return AssertionResult(
                passed=False,
                message=f"Port {port} is not open on {host}",
                evidence={"host": host, "port": port, "protocol": protocol, "error_code": result},
            )
    except Exception as e:
        return AssertionResult(
            passed=False,
            message=f"Port check failed: {e}",
            evidence={"host": host, "port": port, "error": str(e)},
        )

    return AssertionResult(
        passed=True,
        message=f"Port {port} is open on {host}",
        evidence={"host": host, "port": port, "protocol": protocol},
    )


# ============================================================================
# HTTP Response Check
# ============================================================================

def assert_http_response(
    url: str,
    method: str = "GET",
    expected_status: Optional[int] = None,
    expected_pattern: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
    data: Optional[str] = None,
    timeout: int = 30,
    verify_ssl: bool = True,
) -> AssertionResult:
    """
    Assert that an HTTP response matches expected criteria.

    Args:
        url: URL to request.
        method: HTTP method (default: "GET").
        expected_status: Expected HTTP status code (default: None).
        expected_pattern: Regex pattern to search for in response body (default: None).
        headers: HTTP headers to send (default: None).
        data: Request body data (default: None).
        timeout: Request timeout in seconds (default: 30).
        verify_ssl: Whether to verify SSL certificates (default: True).

    Returns:
        AssertionResult with passed=True if the response matches.

    Example:
        >>> result = assert_http_response(
        ...     "http://example.com/api",
        ...     expected_status=200,
        ...     expected_pattern=r"success"
        ... )
    """
    try:
        import urllib.request
        import urllib.error
        import ssl

        req = urllib.request.Request(url, method=method)

        if headers:
            for key, value in headers.items():
                req.add_header(key, value)

        if data:
            req.data = data.encode("utf-8")

        ctx = None
        if not verify_ssl:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

        response = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        status = response.getcode()
        body = response.read().decode("utf-8", errors="replace")
        response_headers = dict(response.getheaders())

    except urllib.error.HTTPError as e:
        status = e.code
        body = e.read().decode("utf-8", errors="replace")
        response_headers = dict(e.headers)
    except Exception as e:
        return AssertionResult(
            passed=False,
            message=f"HTTP request failed: {e}",
            evidence={"url": url, "method": method, "error": str(e)},
        )

    evidence = {
        "url": url,
        "method": method,
        "status": status,
        "body": body,
        "headers": response_headers,
    }

    if expected_status is not None and status != expected_status:
        return AssertionResult(
            passed=False,
            message=f"HTTP status {status} does not match expected {expected_status}",
            evidence={**evidence, "expected_status": expected_status},
        )

    if expected_pattern is not None:
        if not re.search(expected_pattern, body, re.MULTILINE):
            return AssertionResult(
                passed=False,
                message=f"Pattern '{expected_pattern}' not found in response body",
                evidence={**evidence, "pattern": expected_pattern},
            )

    return AssertionResult(
        passed=True,
        message=f"HTTP response matches: {status} {url}",
        evidence=evidence,
    )


# ============================================================================
# On-Chain State Change Check
# ============================================================================

def assert_onchain_state_change(
    rpc_url: str,
    contract_address: str,
    slot: str,
    expected_value: Optional[str] = None,
    changed_from: Optional[str] = None,
    wait_blocks: int = 12,
    block_time: float = 12.0,
) -> AssertionResult:
    """
    Assert that an on-chain storage slot has changed.

    Args:
        rpc_url: RPC URL for the blockchain.
        contract_address: Contract address.
        slot: Storage slot to check.
        expected_value: Expected value after change (default: None).
        changed_from: Expected value before change (default: None).
        wait_blocks: Number of blocks to wait for finality (default: 12).
        block_time: Average block time in seconds (default: 12.0).

    Returns:
        AssertionResult with passed=True if the state changed.

    Example:
        >>> result = assert_onchain_state_change(
        ...     rpc_url="https://mainnet.infura.io/v3/YOUR_KEY",
        ...     contract_address="0x1234...",
        ...     slot="0x0",
        ...     changed_from="0x0000...0000",
        ... )
    """
    def _cast_storage(address: str, slot: str) -> Optional[str]:
        try:
            result = subprocess.run(
                ["cast", "storage", address, slot, "--rpc-url", rpc_url],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    # Get current value
    current_value = _cast_storage(contract_address, slot)

    if current_value is None:
        return AssertionResult(
            passed=False,
            message=f"Failed to read storage slot {slot}",
            evidence={"contract": contract_address, "slot": slot},
        )

    # Always wait for finality before checking, regardless of initial state
    time.sleep(wait_blocks * block_time)
    current_value = _cast_storage(contract_address, slot)

    # Check if value matches expected
    if expected_value is not None:
        if current_value != expected_value:
            return AssertionResult(
                passed=False,
                message=f"Storage value {current_value} does not match expected {expected_value}",
                evidence={
                    "contract": contract_address,
                    "slot": slot,
                    "current": current_value,
                    "expected": expected_value,
                },
            )

    # Check if value changed
    if changed_from is not None:
        if current_value == changed_from:
            return AssertionResult(
                passed=False,
                message=f"Storage value did not change from {changed_from}",
                evidence={
                    "contract": contract_address,
                    "slot": slot,
                    "current": current_value,
                    "changed_from": changed_from,
                },
            )

    return AssertionResult(
        passed=True,
        message=f"Storage slot {slot} changed as expected",
        evidence={
            "contract": contract_address,
            "slot": slot,
            "current_value": current_value,
            "changed_from": changed_from,
            "expected_value": expected_value,
        },
    )


# ============================================================================
# Transaction Verification Check
# ============================================================================

def assert_transaction_verified(
    rpc_url: str,
    tx_hash: str,
    expected_status: str = "0x1",
    wait_blocks: int = 12,
    block_time: float = 12.0,
) -> AssertionResult:
    """
    Assert that a transaction was verified on-chain.

    Args:
        rpc_url: RPC URL for the blockchain.
        tx_hash: Transaction hash to verify.
        expected_status: Expected transaction status (default: "0x1").
        wait_blocks: Number of blocks to wait for finality (default: 12).
        block_time: Average block time in seconds (default: 12.0).

    Returns:
        AssertionResult with passed=True if the transaction is verified.

    Example:
        >>> result = assert_transaction_verified(
        ...     rpc_url="https://mainnet.infura.io/v3/YOUR_KEY",
        ...     tx_hash="0xabc123...",
        ... )
    """
    def _get_receipt(hash: str) -> Optional[Dict[str, Any]]:
        try:
            result = subprocess.run(
                ["cast", "receipt", hash, "--rpc-url", rpc_url, "--json"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
        except Exception:
            pass
        return None

    # Wait for finality
    time.sleep(wait_blocks * block_time)

    receipt = _get_receipt(tx_hash)

    if receipt is None:
        return AssertionResult(
            passed=False,
            message=f"Transaction receipt not found: {tx_hash}",
            evidence={"tx_hash": tx_hash, "rpc_url": rpc_url},
        )

    status = receipt.get("status", "0x0")

    if status != expected_status:
        return AssertionResult(
            passed=False,
            message=f"Transaction status {status} does not match expected {expected_status}",
            evidence={
                "tx_hash": tx_hash,
                "status": status,
                "expected_status": expected_status,
                "receipt": receipt,
            },
        )

    return AssertionResult(
        passed=True,
        message=f"Transaction verified: {tx_hash}",
        evidence={
            "tx_hash": tx_hash,
            "status": status,
            "receipt": receipt,
        },
    )


# ============================================================================
# Composite Assertions
# ============================================================================

def assert_all(*assertions: AssertionResult) -> AssertionResult:
    """
    Combine multiple assertions — all must pass.

    Args:
        *assertions: AssertionResult objects to combine.

    Returns:
        AssertionResult with passed=True if all assertions passed.

    Example:
        >>> r1 = assert_file_exists("/tmp/pwned.txt")
        >>> r2 = assert_command_output("whoami", expected_pattern="root")
        >>> result = assert_all(r1, r2)
    """
    failed = [a for a in assertions if not a.passed]

    if failed:
        messages = [a.message for a in failed]
        return AssertionResult(
            passed=False,
            message=f"{len(failed)} assertion(s) failed: {'; '.join(messages)}",
            evidence={"failed": [a.to_dict() for a in failed]},
        )

    return AssertionResult(
        passed=True,
        message=f"All {len(assertions)} assertions passed",
        evidence={"assertions": [a.to_dict() for a in assertions]},
    )


def assert_any(*assertions: AssertionResult) -> AssertionResult:
    """
    Combine multiple assertions — at least one must pass.

    Args:
        *assertions: AssertionResult objects to combine.

    Returns:
        AssertionResult with passed=True if at least one assertion passed.

    Example:
        >>> r1 = assert_port_open("127.0.0.1", 8080)
        >>> r2 = assert_port_open("127.0.0.1", 8443)
        >>> result = assert_any(r1, r2)
    """
    passed = [a for a in assertions if a.passed]

    if not passed:
        messages = [a.message for a in assertions]
        return AssertionResult(
            passed=False,
            message=f"All {len(assertions)} assertions failed: {'; '.join(messages)}",
            evidence={"failed": [a.to_dict() for a in assertions]},
        )

    return AssertionResult(
        passed=True,
        message=f"{len(passed)} of {len(assertions)} assertions passed",
        evidence={"passed": [a.to_dict() for a in passed]},
    )


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """CLI interface for running assertions from the command line."""
    import argparse

    parser = argparse.ArgumentParser(description="Side-effect assertion runner")
    parser.add_argument("--type", required=True,
                        choices=["file", "output", "callback", "process", "port", "http", "onchain", "transaction"])
    parser.add_argument("--target", help="Target (file path, command, host, URL, contract address)")
    parser.add_argument("--port", type=int, help="Port for callback/port checks")
    parser.add_argument("--pattern", help="Expected pattern for output/HTTP checks")
    parser.add_argument("--status", type=int, help="Expected HTTP status code")
    parser.add_argument("--rpc-url", help="RPC URL for on-chain checks")
    parser.add_argument("--slot", help="Storage slot for on-chain checks")
    parser.add_argument("--tx-hash", help="Transaction hash for transaction checks")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout in seconds")

    args = parser.parse_args()

    if args.type == "file":
        result = assert_file_exists(args.target)
    elif args.type == "output":
        result = assert_command_output(args.target, expected_pattern=args.pattern, timeout=args.timeout)
    elif args.type == "callback":
        result = assert_network_callback(args.port or 4444, timeout=args.timeout)
    elif args.type == "process":
        result = assert_process_running(args.target)
    elif args.type == "port":
        result = assert_port_open(args.target, args.port or 80)
    elif args.type == "http":
        result = assert_http_response(args.target, expected_status=args.status, expected_pattern=args.pattern, timeout=args.timeout)
    elif args.type == "onchain":
        result = assert_onchain_state_change(args.rpc_url, args.target, args.slot or "0x0")
    elif args.type == "transaction":
        result = assert_transaction_verified(args.rpc_url, args.tx_hash)
    else:
        parser.error(f"Unknown assertion type: {args.type}")

    print(json.dumps(result.to_dict(), indent=2))
    return 0 if result.passed else 1


if __name__ == "__main__":
    exit(main())
