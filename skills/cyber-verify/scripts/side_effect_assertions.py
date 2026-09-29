#!/usr/bin/env python3
"""
side_effect_assertions.py - Side-Effect Assertion Library

A library of common side-effect assertions for verifying that exploits
and security tests have produced the expected effects on a target system.

Usage:
    from side_effect_assertions import (
        file_exists, command_output, network_callback,
        process_running, port_open, http_response
    )

    # Assert a file was created
    file_exists("/tmp/pwned", content="pwned")

    # Assert a command produces expected output
    command_output("id", expected="uid=0")

    # Assert a network callback was received
    network_callback("192.168.1.100", 4444, timeout=10)

    # Assert a process is running
    process_running("apache2")

    # Assert a port is open
    port_open("target.com", 8080)

    # Assert an HTTP response
    http_response("http://target.com", expected_status=200, expected_content="Welcome")

Exit Codes:
    0   All assertions passed
    1   One or more assertions failed
    2   Error during assertion execution
"""

import argparse
import hashlib
import http.client
import os
import socket
import subprocess
import sys
import time
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Union
from urllib.parse import urlparse


# =============================================================================
# ASSERTION RESULT
# =============================================================================

@dataclass
class AssertionResult:
    """Result of a single assertion."""
    name: str
    passed: bool
    message: str
    expected: Any = None
    actual: Any = None
    duration_ms: float = 0.0


@dataclass
class AssertionSuite:
    """Collection of assertion results."""
    results: list = field(default_factory=list)
    
    def add(self, result: AssertionResult):
        self.results.append(result)
    
    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.passed)
    
    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if not r.passed)
    
    @property
    def total(self) -> int:
        return len(self.results)
    
    @property
    def all_passed(self) -> bool:
        return self.failed == 0
    
    def summary(self) -> str:
        lines = [
            "=" * 60,
            "ASSERTION SUITE RESULTS",
            "=" * 60,
            f"Total: {self.total} | Passed: {self.passed} | Failed: {self.failed}",
            "-" * 60,
        ]
        for r in self.results:
            status = "PASS" if r.passed else "FAIL"
            lines.append(f"  [{status}] {r.name}: {r.message}")
            if not r.passed:
                lines.append(f"         Expected: {r.expected}")
                lines.append(f"         Actual:   {r.actual}")
        lines.append("=" * 60)
        return "\n".join(lines)


# =============================================================================
# ASSERTION FUNCTIONS
# =============================================================================

def file_exists(path: str, content: Optional[str] = None, 
               content_contains: Optional[str] = None,
               min_size: int = 0, max_size: Optional[int] = None) -> AssertionResult:
    """
    Assert that a file exists with optional content verification.
    
    Args:
        path: Path to the file to check
        content: Exact content the file must have (optional)
        content_contains: Substring the file content must contain (optional)
        min_size: Minimum file size in bytes (default: 0)
        max_size: Maximum file size in bytes (optional)
    
    Returns:
        AssertionResult with pass/fail status
    """
    start_time = time.time()
    name = f"file_exists({path})"
    
    try:
        if not os.path.exists(path):
            return AssertionResult(
                name=name, passed=False,
                message=f"File does not exist: {path}",
                expected="file exists", actual="not found",
                duration_ms=(time.time() - start_time) * 1000
            )
        
        if not os.path.isfile(path):
            return AssertionResult(
                name=name, passed=False,
                message=f"Path exists but is not a file: {path}",
                expected="regular file", actual="not a file",
                duration_ms=(time.time() - start_time) * 1000
            )
        
        file_size = os.path.getsize(path)
        
        # Check size constraints
        if file_size < min_size:
            return AssertionResult(
                name=name, passed=False,
                message=f"File too small: {file_size} bytes (min: {min_size})",
                expected=f"size >= {min_size}", actual=f"size = {file_size}",
                duration_ms=(time.time() - start_time) * 1000
            )
        
        if max_size is not None and file_size > max_size:
            return AssertionResult(
                name=name, passed=False,
                message=f"File too large: {file_size} bytes (max: {max_size})",
                expected=f"size <= {max_size}", actual=f"size = {file_size}",
                duration_ms=(time.time() - start_time) * 1000
            )
        
        # Check content if specified
        if content is not None or content_contains is not None:
            try:
                with open(path, 'r', errors='replace') as f:
                    file_content = f.read()
                
                if content is not None and file_content != content:
                    return AssertionResult(
                        name=name, passed=False,
                        message=f"File content mismatch",
                        expected=content[:100], actual=file_content[:100],
                        duration_ms=(time.time() - start_time) * 1000
                    )
                
                if content_contains is not None and content_contains not in file_content:
                    return AssertionResult(
                        name=name, passed=False,
                        message=f"File does not contain expected content",
                        expected=f"contains '{content_contains}'",
                        actual=f"content: {file_content[:100]}",
                        duration_ms=(time.time() - start_time) * 1000
                    )
            except (IOError, OSError) as e:
                return AssertionResult(
                    name=name, passed=False,
                    message=f"Error reading file: {e}",
                    expected="readable file", actual=str(e),
                    duration_ms=(time.time() - start_time) * 1000
                )
        
        return AssertionResult(
            name=name, passed=True,
            message=f"File exists: {path} ({file_size} bytes)",
            duration_ms=(time.time() - start_time) * 1000
        )
    
    except Exception as e:
        return AssertionResult(
            name=name, passed=False,
            message=f"Unexpected error: {e}",
            expected="file exists", actual=str(e),
            duration_ms=(time.time() - start_time) * 1000
        )


def command_output(command: str, expected: Optional[str] = None,
                  expected_contains: Optional[str] = None,
                  expected_exit_code: int = 0,
                  timeout: int = 30, shell: bool = True) -> AssertionResult:
    """
    Assert that a command produces expected output.
    
    Args:
        command: Command to execute
        expected: Exact output the command must produce (optional)
        expected_contains: Substring the output must contain (optional)
        expected_exit_code: Expected exit code (default: 0)
        timeout: Command timeout in seconds (default: 30)
        shell: Whether to use shell execution (default: True)
    
    Returns:
        AssertionResult with pass/fail status
    """
    start_time = time.time()
    name = f"command_output({command})"
    
    try:
        result = subprocess.run(
            command, shell=shell, capture_output=True, text=True,
            timeout=timeout
        )
        
        output = result.stdout + result.stderr
        
        # Check exit code
        if result.returncode != expected_exit_code:
            return AssertionResult(
                name=name, passed=False,
                message=f"Exit code mismatch: got {result.returncode}, expected {expected_exit_code}",
                expected=f"exit code {expected_exit_code}",
                actual=f"exit code {result.returncode}",
                duration_ms=(time.time() - start_time) * 1000
            )
        
        # Check exact output
        if expected is not None and output.strip() != expected.strip():
            return AssertionResult(
                name=name, passed=False,
                message=f"Output mismatch",
                expected=expected[:200], actual=output.strip()[:200],
                duration_ms=(time.time() - start_time) * 1000
            )
        
        # Check output contains
        if expected_contains is not None and expected_contains not in output:
            return AssertionResult(
                name=name, passed=False,
                message=f"Output does not contain expected string",
                expected=f"contains '{expected_contains}'",
                actual=f"output: {output.strip()[:200]}",
                duration_ms=(time.time() - start_time) * 1000
            )
        
        return AssertionResult(
            name=name, passed=True,
            message=f"Command produced expected output (exit code: {result.returncode})",
            duration_ms=(time.time() - start_time) * 1000
        )
    
    except subprocess.TimeoutExpired:
        return AssertionResult(
            name=name, passed=False,
            message=f"Command timed out after {timeout}s",
            expected=f"completion within {timeout}s", actual="timeout",
            duration_ms=(time.time() - start_time) * 1000
        )
    except Exception as e:
        return AssertionResult(
            name=name, passed=False,
            message=f"Error executing command: {e}",
            expected="successful execution", actual=str(e),
            duration_ms=(time.time() - start_time) * 1000
        )


def network_callback(host: str, port: int, timeout: int = 10,
                     send_data: Optional[bytes] = None,
                     expected_response: Optional[bytes] = None) -> AssertionResult:
    """
    Assert that a network callback is received on a specific host/port.
    
    This function connects to a host:port to verify a listener is present,
    optionally sending data and checking the response.
    
    Args:
        host: Hostname or IP address to connect to
        port: Port number to connect to
        timeout: Connection timeout in seconds (default: 10)
        send_data: Data to send after connection (optional)
        expected_response: Expected response data (optional)
    
    Returns:
        AssertionResult with pass/fail status
    """
    start_time = time.time()
    name = f"network_callback({host}:{port})"
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        
        # Send data if specified
        if send_data is not None:
            sock.sendall(send_data)
        
        # Receive response if expected
        if expected_response is not None:
            response = b""
            while len(response) < len(expected_response):
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
            
            sock.close()
            
            if response != expected_response:
                return AssertionResult(
                    name=name, passed=False,
                    message=f"Response mismatch",
                    expected=expected_response[:100], actual=response[:100],
                    duration_ms=(time.time() - start_time) * 1000
                )
        
        sock.close()
        
        return AssertionResult(
            name=name, passed=True,
            message=f"Successfully connected to {host}:{port}",
            duration_ms=(time.time() - start_time) * 1000
        )
    
    except socket.timeout:
        return AssertionResult(
            name=name, passed=False,
            message=f"Connection to {host}:{port} timed out after {timeout}s",
            expected="successful connection", actual="timeout",
            duration_ms=(time.time() - start_time) * 1000
        )
    except (ConnectionRefusedError, OSError) as e:
        return AssertionResult(
            name=name, passed=False,
            message=f"Connection to {host}:{port} failed: {e}",
            expected="successful connection", actual=str(e),
            duration_ms=(time.time() - start_time) * 1000
        )
    except Exception as e:
        return AssertionResult(
            name=name, passed=False,
            message=f"Unexpected error: {e}",
            expected="successful connection", actual=str(e),
            duration_ms=(time.time() - start_time) * 1000
        )


def process_running(process_name: str, 
                    check_cmdline: bool = True) -> AssertionResult:
    """
    Assert that a process is currently running.
    
    Args:
        process_name: Name of the process to check
        check_cmdline: Also check command line arguments (default: True)
    
    Returns:
        AssertionResult with pass/fail status
    """
    start_time = time.time()
    name = f"process_running({process_name})"
    
    try:
        # Use pgrep to find the process
        result = subprocess.run(
            ["pgrep", "-f" if check_cmdline else "-x", process_name],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode != 0:
            return AssertionResult(
                name=name, passed=False,
                message=f"Process not found: {process_name}",
                expected="process running", actual="not found",
                duration_ms=(time.time() - start_time) * 1000
            )
        
        pids = result.stdout.strip().split('\n')
        pid_list = [p for p in pids if p.strip()]
        
        return AssertionResult(
            name=name, passed=True,
            message=f"Process running: {process_name} (PIDs: {', '.join(pid_list)})",
            duration_ms=(time.time() - start_time) * 1000
        )
    
    except subprocess.TimeoutExpired:
        return AssertionResult(
            name=name, passed=False,
            message=f"Timeout checking for process: {process_name}",
            expected="process check", actual="timeout",
            duration_ms=(time.time() - start_time) * 1000
        )
    except FileNotFoundError:
        # pgrep not available, fallback to ps
        try:
            result = subprocess.run(
                ["ps", "aux"], capture_output=True, text=True, timeout=10
            )
            if process_name in result.stdout:
                return AssertionResult(
                    name=name, passed=True,
                    message=f"Process running: {process_name}",
                    duration_ms=(time.time() - start_time) * 1000
                )
            else:
                return AssertionResult(
                    name=name, passed=False,
                    message=f"Process not found: {process_name}",
                    expected="process running", actual="not found",
                    duration_ms=(time.time() - start_time) * 1000
                )
        except Exception as e:
            return AssertionResult(
                name=name, passed=False,
                message=f"Error checking process: {e}",
                expected="process check", actual=str(e),
                duration_ms=(time.time() - start_time) * 1000
            )
    except Exception as e:
        return AssertionResult(
            name=name, passed=False,
            message=f"Unexpected error: {e}",
            expected="process check", actual=str(e),
            duration_ms=(time.time() - start_time) * 1000
        )


def port_open(host: str, port: int, timeout: int = 5,
              protocol: str = "tcp") -> AssertionResult:
    """
    Assert that a port is open on a target host.
    
    Args:
        host: Hostname or IP address
        port: Port number to check
        timeout: Connection timeout in seconds (default: 5)
        protocol: Protocol to check - "tcp" or "udp" (default: "tcp")
    
    Returns:
        AssertionResult with pass/fail status
    """
    start_time = time.time()
    name = f"port_open({host}:{port}/{protocol})"
    
    try:
        if protocol == "tcp":
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        elif protocol == "udp":
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            return AssertionResult(
                name=name, passed=False,
                message=f"Invalid protocol: {protocol}",
                expected="tcp or udp", actual=protocol,
                duration_ms=(time.time() - start_time) * 1000
            )
        
        sock.settimeout(timeout)
        
        if protocol == "tcp":
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result != 0:
                return AssertionResult(
                    name=name, passed=False,
                    message=f"Port {port}/tcp is closed on {host}",
                    expected="port open", actual=f"connection failed (error {result})",
                    duration_ms=(time.time() - start_time) * 1000
                )
        else:
            # UDP - send a packet and check for ICMP unreachable
            sock.sendto(b"\x00", (host, port))
            try:
                sock.recvfrom(1024)
            except socket.timeout:
                # Timeout might mean open (no response) or filtered
                pass
            sock.close()
        
        return AssertionResult(
            name=name, passed=True,
            message=f"Port {port}/{protocol} is open on {host}",
            duration_ms=(time.time() - start_time) * 1000
        )
    
    except socket.timeout:
        return AssertionResult(
            name=name, passed=False,
            message=f"Connection to {host}:{port} timed out",
            expected="port open", actual="timeout",
            duration_ms=(time.time() - start_time) * 1000
        )
    except (socket.gaierror, OSError) as e:
        return AssertionResult(
            name=name, passed=False,
            message=f"Connection to {host}:{port} failed: {e}",
            expected="port open", actual=str(e),
            duration_ms=(time.time() - start_time) * 1000
        )
    except Exception as e:
        return AssertionResult(
            name=name, passed=False,
            message=f"Unexpected error: {e}",
            expected="port open", actual=str(e),
            duration_ms=(time.time() - start_time) * 1000
        )


def http_response(url: str, expected_status: Optional[int] = None,
                 expected_content: Optional[str] = None,
                 expected_header: Optional[dict] = None,
                 method: str = "GET", data: Optional[bytes] = None,
                 headers: Optional[dict] = None, timeout: int = 30,
                 verify_ssl: bool = True) -> AssertionResult:
    """
    Assert that an HTTP response matches expectations.
    
    Args:
        url: URL to request
        expected_status: Expected HTTP status code (optional)
        expected_content: Substring expected in response body (optional)
        expected_header: Dict of expected header key-value pairs (optional)
        method: HTTP method (default: GET)
        data: Request body data (optional)
        headers: Request headers (optional)
        timeout: Request timeout in seconds (default: 30)
        verify_ssl: Whether to verify SSL certificates (default: True)
    
    Returns:
        AssertionResult with pass/fail status
    """
    start_time = time.time()
    name = f"http_response({url})"
    
    try:
        # Create request
        req = urllib.request.Request(url, data=data, method=method)
        
        if headers:
            for key, value in headers.items():
                req.add_header(key, value)
        
        # Handle SSL verification
        if not verify_ssl:
            import ssl
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            response = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        else:
            response = urllib.request.urlopen(req, timeout=timeout)
        
        status = response.getcode()
        body = response.read().decode('utf-8', errors='replace')
        resp_headers = dict(response.getheaders())
        
        # Check status code
        if expected_status is not None and status != expected_status:
            return AssertionResult(
                name=name, passed=False,
                message=f"Status code mismatch: got {status}, expected {expected_status}",
                expected=f"status {expected_status}", actual=f"status {status}",
                duration_ms=(time.time() - start_time) * 1000
            )
        
        # Check content
        if expected_content is not None and expected_content not in body:
            return AssertionResult(
                name=name, passed=False,
                message=f"Response body does not contain expected content",
                expected=f"contains '{expected_content}'",
                actual=f"body: {body[:200]}",
                duration_ms=(time.time() - start_time) * 1000
            )
        
        # Check headers
        if expected_header is not None:
            for key, value in expected_header.items():
                actual_value = resp_headers.get(key, resp_headers.get(key.title(), ""))
                if value.lower() not in actual_value.lower():
                    return AssertionResult(
                        name=name, passed=False,
                        message=f"Header mismatch: {key}",
                        expected=f"{key}: {value}", actual=f"{key}: {actual_value}",
                        duration_ms=(time.time() - start_time) * 1000
                    )
        
        return AssertionResult(
            name=name, passed=True,
            message=f"HTTP response matches expectations (status: {status})",
            duration_ms=(time.time() - start_time) * 1000
        )
    
    except urllib.error.HTTPError as e:
        # HTTP errors still give us status codes
        if expected_status is not None and e.code == expected_status:
            return AssertionResult(
                name=name, passed=True,
                message=f"HTTP response matches expectations (status: {e.code})",
                duration_ms=(time.time() - start_time) * 1000
            )
        return AssertionResult(
            name=name, passed=False,
            message=f"HTTP error: {e.code} {e.reason}",
            expected=f"status {expected_status}" if expected_status else "success",
            actual=f"status {e.code}",
            duration_ms=(time.time() - start_time) * 1000
        )
    except urllib.error.URLError as e:
        return AssertionResult(
            name=name, passed=False,
            message=f"URL error: {e.reason}",
            expected="successful request", actual=str(e.reason),
            duration_ms=(time.time() - start_time) * 1000
        )
    except Exception as e:
        return AssertionResult(
            name=name, passed=False,
            message=f"Unexpected error: {e}",
            expected="successful request", actual=str(e),
            duration_ms=(time.time() - start_time) * 1000
        )


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Side-effect assertion library for security testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check file exists
  %(prog)s --assert file --path /tmp/pwned --content "pwned"

  # Check command output
  %(prog)s --assert command --command "id" --expected "uid=0"

  # Check port is open
  %(prog)s --assert port --host target.com --port 8080

  # Check HTTP response
  %(prog)s --assert http --url http://target.com --status 200 --content "Welcome"

  # Check process is running
  %(prog)s --assert process --name apache2

  # Check network callback
  %(prog)s --assert callback --host 192.168.1.100 --port 4444
        """
    )
    
    parser.add_argument("--assert", "-a", required=True,
                       choices=["file", "command", "callback", "process", "port", "http"],
                       help="Type of assertion to perform")
    parser.add_argument("--path", help="File path (for file assertion)")
    parser.add_argument("--content", help="Expected file content")
    parser.add_argument("--command", help="Command to execute (for command assertion)")
    parser.add_argument("--expected", help="Expected command output")
    parser.add_argument("--host", help="Target host")
    parser.add_argument("--port", type=int, help="Target port")
    parser.add_argument("--url", help="URL (for HTTP assertion)")
    parser.add_argument("--status", type=int, help="Expected HTTP status code")
    parser.add_argument("--name", help="Process name (for process assertion)")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout in seconds")
    
    args = parser.parse_args()
    
    suite = AssertionSuite()
    
    if args.assert == "file":
        if not args.path:
            print("Error: --path required for file assertion", file=sys.stderr)
            sys.exit(2)
        result = file_exists(args.path, content=args.content)
        suite.add(result)
    
    elif args.assert == "command":
        if not args.command:
            print("Error: --command required for command assertion", file=sys.stderr)
            sys.exit(2)
        result = command_output(args.command, expected=args.expected, timeout=args.timeout)
        suite.add(result)
    
    elif args.assert == "callback":
        if not args.host or not args.port:
            print("Error: --host and --port required for callback assertion", file=sys.stderr)
            sys.exit(2)
        result = network_callback(args.host, args.port, timeout=args.timeout)
        suite.add(result)
    
    elif args.assert == "process":
        if not args.name:
            print("Error: --name required for process assertion", file=sys.stderr)
            sys.exit(2)
        result = process_running(args.name)
        suite.add(result)
    
    elif args.assert == "port":
        if not args.host or not args.port:
            print("Error: --host and --port required for port assertion", file=sys.stderr)
            sys.exit(2)
        result = port_open(args.host, args.port, timeout=args.timeout)
        suite.add(result)
    
    elif args.assert == "http":
        if not args.url:
            print("Error: --url required for HTTP assertion", file=sys.stderr)
            sys.exit(2)
        result = http_response(args.url, expected_status=args.status,
                             expected_content=args.content, timeout=args.timeout)
        suite.add(result)
    
    # Print results
    print(suite.summary())
    
    if suite.all_passed:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
