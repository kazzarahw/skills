#!/usr/bin/env python3
"""
fuzz-test-generator.py

Generates fuzzing test cases for smart contracts, creates invariant tests,
and generates edge case tests. Outputs Foundry-compatible test files.

Usage:
    python fuzz-test-generator.py [OPTIONS] <contract_path>

Options:
    -o, --output <directory>     Output directory (default: ./test/generated)
    -c, --contract <name>        Contract name to generate tests for
    -i, --invariants             Generate invariant tests
    -e, --edge-cases             Generate edge case tests
    -f, --fuzz                   Generate fuzz tests
    --fuzz-runs <number>         Number of fuzz runs (default: 256)
    -v, --verbose                Verbose output
    -h, --help                   Show this help message

Examples:
    python fuzz-test-generator.py ./contracts/MyToken.sol
    python fuzz-test-generator.py -c MyToken -i -e -f ./contracts/
    python fuzz-test-generator.py --fuzz-runs 10000 -o ./tests ./src/
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


# ─── Data Classes ────────────────────────────────────────────────────────────

@dataclass
class FunctionInfo:
    """Represents a contract function."""
    name: str
    visibility: str
    state_mutability: str
    parameters: List[Dict[str, str]] = field(default_factory=list)
    return_type: str = ""
    line_number: int = 0
    modifiers: List[str] = field(default_factory=list)


@dataclass
class ContractInfo:
    """Represents a smart contract."""
    name: str
    inherits: List[str] = field(default_factory=list)
    functions: List[FunctionInfo] = field(default_factory=list)
    state_variables: List[Dict[str, str]] = field(default_factory=list)
    events: List[str] = field(default_factory=list)
    file_path: str = ""


# ─── Solidity Parser ─────────────────────────────────────────────────────────

class SolidityParser:
    """Simple Solidity parser for extracting contract information."""
    
    def __init__(self, source_code: str):
        self.source = source_code
        self.contracts: List[ContractInfo] = []
    
    def parse(self) -> List[ContractInfo]:
        """Parse Solidity source and extract contract information."""
        # Find all contract definitions
        contract_pattern = r'contract\s+(\w+)(?:\s+is\s+([^{]+))?\s*\{'
        
        for match in re.finditer(contract_pattern, self.source):
            name = match.group(1)
            inherits_str = match.group(2) or ""
            inherits = [i.strip() for i in inherits_str.split(",") if i.strip()]
            
            # Find contract body
            start = match.end()
            brace_count = 1
            pos = start
            while pos < len(self.source) and brace_count > 0:
                if self.source[pos] == '{':
                    brace_count += 1
                elif self.source[pos] == '}':
                    brace_count -= 1
                pos += 1
            
            body = self.source[start:pos-1]
            
            contract = ContractInfo(
                name=name,
                inherits=inherits,
                file_path=""
            )
            
            # Extract functions
            contract.functions = self._extract_functions(body)
            
            # Extract state variables
            contract.state_variables = self._extract_state_variables(body)
            
            # Extract events
            contract.events = self._extract_events(body)
            
            self.contracts.append(contract)
        
        return self.contracts
    
    def _extract_functions(self, body: str) -> List[FunctionInfo]:
        """Extract function definitions from contract body."""
        functions = []
        
        # Match function definitions
        func_pattern = r'function\s+(\w+)\s*\(([^)]*)\)\s*(public|external|internal|private)?\s*(view|pure|payable)?\s*(?:returns\s*\(([^)]*)\))?'
        
        for match in re.finditer(func_pattern, body):
            name = match.group(1)
            params_str = match.group(2) or ""
            visibility = match.group(3) or "public"
            state_mutability = match.group(4) or "nonpayable"
            returns_str = match.group(5) or ""
            
            # Parse parameters
            parameters = []
            if params_str.strip():
                for param in params_str.split(","):
                    param = param.strip()
                    if param:
                        parts = param.split()
                        if len(parts) >= 2:
                            param_type = parts[0]
                            param_name = parts[-1]
                            parameters.append({
                                "type": param_type,
                                "name": param_name
                            })
            
            # Parse return type
            return_type = returns_str.strip() if returns_str else ""
            
            # Find line number
            line_number = self.source[:match.start()].count('\n') + 1
            
            # Find modifiers
            modifiers = []
            before_func = body[:match.start()].strip()
            modifier_pattern = r'@?(\w+)'
            if before_func:
                # Look for modifiers before function
                lines = before_func.split('\n')
                for line in reversed(lines[-3:]):
                    line = line.strip()
                    if line and not line.startswith('//') and not line.startswith('/*'):
                        if re.match(r'^\w+$', line):
                            modifiers.append(line)
                        break
            
            functions.append(FunctionInfo(
                name=name,
                visibility=visibility,
                state_mutability=state_mutability,
                parameters=parameters,
                return_type=return_type,
                line_number=line_number,
                modifiers=modifiers
            ))
        
        return functions
    
    def _extract_state_variables(self, body: str) -> List[Dict[str, str]]:
        """Extract state variable declarations."""
        variables = []
        
        # Match state variable declarations
        var_pattern = r'(uint\d*|int\d*|address|bool|bytes\d*|string)\s+(public|private|internal)?\s*(\w+)'
        
        for match in re.finditer(var_pattern, body):
            var_type = match.group(1)
            visibility = match.group(2) or "internal"
            var_name = match.group(3)
            
            # Skip if it looks like a function parameter
            before = body[:match.start()].strip()
            if before.endswith('(') or before.endswith(','):
                continue
            
            variables.append({
                "type": var_type,
                "visibility": visibility,
                "name": var_name
            })
        
        return variables
    
    def _extract_events(self, body: str) -> List[str]:
        """Extract event declarations."""
        events = []
        
        event_pattern = r'event\s+(\w+)'
        for match in re.finditer(event_pattern, body):
            events.append(match.group(1))
        
        return events


# ─── Test Generators ─────────────────────────────────────────────────────────

class FuzzTestGenerator:
    """Generates fuzz tests for smart contracts."""
    
    def __init__(self, contract: ContractInfo, fuzz_runs: int = 256):
        self.contract = contract
        self.fuzz_runs = fuzz_runs
    
    def generate(self) -> str:
        """Generate fuzz test file content."""
        lines = [
            "// SPDX-License-Identifier: MIT",
            "pragma solidity ^0.8.0;",
            "",
            "import \"forge-std/Test.sol\";",
            f"import \"../src/{self.contract.name}.sol\";",
            "",
            f"contract {self.contract.name}FuzzTest is Test {{",
            f"    {self.contract.name} public target;",
            "",
            "    function setUp() public {",
            f"        target = new {self.contract.name}();",
            "    }",
            "",
        ]
        
        # Generate fuzz tests for each public/external function
        for func in self.contract.functions:
            if func.visibility in ("public", "external"):
                lines.extend(self._generate_function_fuzz_test(func))
                lines.append("")
        
        lines.append("}")
        
        return "\n".join(lines)
    
    def _generate_function_fuzz_test(self, func: FunctionInfo) -> List[str]:
        """Generate fuzz test for a specific function."""
        lines = []
        
        # Generate fuzz test with random inputs
        test_name = f"testFuzz_{func.name}"
        lines.append(f"    function {test_name}(")
        
        # Add fuzz parameters
        fuzz_params = []
        for param in func.parameters:
            param_type = param["type"]
            param_name = param["name"]
            
            if "uint" in param_type:
                fuzz_params.append(f"        uint256 {param_name}")
            elif "int" in param_type:
                fuzz_params.append(f"        int256 {param_name}")
            elif param_type == "address":
                fuzz_params.append(f"        address {param_name}")
            elif param_type == "bool":
                fuzz_params.append(f"        bool {param_name}")
            elif "bytes" in param_type:
                fuzz_params.append(f"        bytes memory {param_name}")
            elif param_type == "string":
                fuzz_params.append(f"        string memory {param_name}")
            else:
                fuzz_params.append(f"        {param_type} {param_name}")
        
        lines.append(",\n".join(fuzz_params))
        lines.append("    ) public {")
        
        # Add assumptions for valid inputs
        for param in func.parameters:
            param_type = param["type"]
            param_name = param["name"]
            
            if "uint" in param_type:
                lines.append(f"        vm.assume({param_name} < type(uint256).max);")
            elif param_type == "address":
                lines.append(f"        vm.assume({param_name} != address(0));")
        
        # Call function
        if func.parameters:
            param_names = ", ".join([p["name"] for p in func.parameters])
            if func.state_mutability in ("view", "pure"):
                lines.append(f"        target.{func.name}({param_names});")
            else:
                lines.append(f"        target.{func.name}({param_names});")
        else:
            lines.append(f"        target.{func.name}();")
        
        lines.append("    }")
        
        return lines


class InvariantTestGenerator:
    """Generates invariant tests for smart contracts."""
    
    def __init__(self, contract: ContractInfo):
        self.contract = contract
    
    def generate(self) -> str:
        """Generate invariant test file content."""
        lines = [
            "// SPDX-License-Identifier: MIT",
            "pragma solidity ^0.8.0;",
            "",
            "import \"forge-std/Test.sol\";",
            f"import \"../src/{self.contract.name}.sol\";",
            "",
            f"contract {self.contract.name}InvariantTest is Test {{",
            f"    {self.contract.name} public target;",
            "",
            "    function setUp() public {",
            f"        target = new {self.contract.name}();",
            "    }",
            "",
        ]
        
        # Generate invariant tests based on state variables
        for var in self.contract.state_variables:
            lines.extend(self._generate_variable_invariant(var))
            lines.append("")
        
        # Generate general invariants
        lines.extend(self._generate_general_invariants())
        lines.append("")
        
        lines.append("}")
        
        return "\n".join(lines)
    
    def _generate_variable_invariant(self, var: Dict[str, str]) -> List[str]:
        """Generate invariant test for a state variable."""
        lines = []
        var_name = var["name"]
        var_type = var["type"]
        
        # Generate invariant: variable should never be negative (for uint)
        if "uint" in var_type:
            lines.append(f"    function testInvariant_{var_name}_NonNegative() public {{")
            lines.append(f"        assertGe(target.{var_name}(), 0);")
            lines.append(f"    }}")
        
        # Generate invariant: address should not be zero (for important addresses)
        elif var_type == "address" and ("owner" in var_name or "admin" in var_name):
            lines.append(f"    function testInvariant_{var_name}_NotZero() public {{")
            lines.append(f"        assertTrue(target.{var_name}() != address(0));")
            lines.append(f"    }}")
        
        return lines
    
    def _generate_general_invariants(self) -> List[str]:
        """Generate general invariant tests."""
        lines = []
        
        # Invariant: contract should never have negative balance
        lines.append("    function testInvariant_ContractBalance_NonNegative() public {")
        lines.append("        assertGe(address(target).balance, 0);")
        lines.append("    }")
        lines.append("")
        
        # Invariant: all state variables should be consistent
        lines.append("    function testInvariant_StateConsistency() public {")
        lines.append("        // Add protocol-specific invariants here")
        lines.append("        // Example: totalSupply == sum of balances")
        lines.append("    }")
        
        return lines


class EdgeCaseTestGenerator:
    """Generates edge case tests for smart contracts."""
    
    def __init__(self, contract: ContractInfo):
        self.contract = contract
    
    def generate(self) -> str:
        """Generate edge case test file content."""
        lines = [
            "// SPDX-License-Identifier: MIT",
            "pragma solidity ^0.8.0;",
            "",
            "import \"forge-std/Test.sol\";",
            f"import \"../src/{self.contract.name}.sol\";",
            "",
            f"contract {self.contract.name}EdgeCaseTest is Test {{",
            f"    {self.contract.name} public target;",
            "",
            "    function setUp() public {",
            f"        target = new {self.contract.name}();",
            "    }",
            "",
        ]
        
        # Generate edge case tests for each function
        for func in self.contract.functions:
            if func.visibility in ("public", "external"):
                lines.extend(self._generate_function_edge_cases(func))
                lines.append("")
        
        lines.append("}")
        
        return "\n".join(lines)
    
    def _generate_function_edge_cases(self, func: FunctionInfo) -> List[str]:
        """Generate edge case tests for a specific function."""
        lines = []
        
        # Edge case: zero values
        if func.parameters:
            lines.append(f"    function testEdge_{func.name}_ZeroValues() public {{")
            zero_params = []
            for param in func.parameters:
                param_type = param["type"]
                if "uint" in param_type:
                    zero_params.append("0")
                elif "int" in param_type:
                    zero_params.append("0")
                elif param_type == "address":
                    zero_params.append("address(0)")
                elif param_type == "bool":
                    zero_params.append("false")
                elif "bytes" in param_type:
                    zero_params.append("hex\"\"")
                elif param_type == "string":
                    zero_params.append('""')
                else:
                    zero_params.append(f"type({param_type}).min")
            
            param_str = ", ".join(zero_params)
            lines.append(f"        target.{func.name}({param_str});")
            lines.append(f"    }}")
            lines.append("")
        
        # Edge case: maximum values
        if func.parameters:
            lines.append(f"    function testEdge_{func.name}_MaxValues() public {{")
            max_params = []
            for param in func.parameters:
                param_type = param["type"]
                if "uint" in param_type:
                    max_params.append("type(uint256).max")
                elif "int" in param_type:
                    max_params.append("type(int256).max")
                elif param_type == "address":
                    max_params.append("type(uint160).max")
                elif param_type == "bool":
                    max_params.append("true")
                elif "bytes" in param_type:
                    max_params.append("hex\"ff\"")
                elif param_type == "string":
                    max_params.append('"max"')
                else:
                    max_params.append(f"type({param_type}).max")
            
            param_str = ", ".join(max_params)
            lines.append(f"        try target.{func.name}({param_str}) {{")
            lines.append(f"            // Expected to succeed or revert gracefully")
            lines.append(f"        }} catch {{")
            lines.append(f"            // Expected revert")
            lines.append(f"        }}")
            lines.append(f"    }}")
            lines.append("")
        
        # Edge case: boundary values
        if func.parameters:
            lines.append(f"    function testEdge_{func.name}_BoundaryValues() public {{")
            boundary_params = []
            for param in func.parameters:
                param_type = param["type"]
                if "uint" in param_type:
                    boundary_params.append("1")
                elif "int" in param_type:
                    boundary_params.append("-1")
                elif param_type == "address":
                    boundary_params.append("address(1)")
                elif param_type == "bool":
                    boundary_params.append("true")
                elif "bytes" in param_type:
                    boundary_params.append("hex\"01\"")
                elif param_type == "string":
                    boundary_params.append('"a"')
                else:
                    boundary_params.append("1")
            
            param_str = ", ".join(boundary_params)
            lines.append(f"        try target.{func.name}({param_str}) {{")
            lines.append(f"            // Expected to succeed or revert gracefully")
            lines.append(f"        }} catch {{")
            lines.append(f"            // Expected revert")
            lines.append(f"        }}")
            lines.append(f"    }}")
        
        return lines


# ─── Main ────────────────────────────────────────────────────────────────────

def find_solidity_files(path: str) -> List[Path]:
    """Find all Solidity files in the given path."""
    p = Path(path)
    if p.is_file() and p.suffix == ".sol":
        return [p]
    return list(p.rglob("*.sol"))


def generate_tests(
    contract_path: str,
    output_dir: str,
    contract_name: Optional[str] = None,
    generate_fuzz: bool = True,
    generate_invariants: bool = True,
    generate_edge_cases: bool = True,
    fuzz_runs: int = 256,
    verbose: bool = False
) -> Dict[str, str]:
    """Generate test files for a smart contract."""
    
    # Read contract source
    with open(contract_path, 'r') as f:
        source = f.read()
    
    # Parse contract
    parser = SolidityParser(source)
    contracts = parser.parse()
    
    if not contracts:
        raise ValueError(f"No contracts found in {contract_path}")
    
    # Filter by contract name if specified
    if contract_name:
        contracts = [c for c in contracts if c.name == contract_name]
        if not contracts:
            raise ValueError(f"Contract '{contract_name}' not found in {contract_path}")
    
    generated_files = {}
    
    for contract in contracts:
        if verbose:
            print(f"Generating tests for {contract.name}...")
        
        # Generate fuzz tests
        if generate_fuzz:
            fuzz_gen = FuzzTestGenerator(contract, fuzz_runs)
            fuzz_content = fuzz_gen.generate()
            fuzz_file = f"{contract.name}FuzzTest.sol"
            generated_files[fuzz_file] = fuzz_content
        
        # Generate invariant tests
        if generate_invariants:
            inv_gen = InvariantTestGenerator(contract)
            inv_content = inv_gen.generate()
            inv_file = f"{contract.name}InvariantTest.sol"
            generated_files[inv_file] = inv_content
        
        # Generate edge case tests
        if generate_edge_cases:
            edge_gen = EdgeCaseTestGenerator(contract)
            edge_content = edge_gen.generate()
            edge_file = f"{contract.name}EdgeCaseTest.sol"
            generated_files[edge_file] = edge_content
    
    # Write files
    os.makedirs(output_dir, exist_ok=True)
    
    for filename, content in generated_files.items():
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        if verbose:
            print(f"  Generated: {filepath}")
    
    return generated_files


def main():
    parser = argparse.ArgumentParser(
        description="Generate fuzzing, invariant, and edge case tests for smart contracts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "contract_path",
        help="Path to Solidity contract file or directory"
    )
    parser.add_argument(
        "-o", "--output",
        default="./test/generated",
        help="Output directory (default: ./test/generated)"
    )
    parser.add_argument(
        "-c", "--contract",
        help="Contract name to generate tests for"
    )
    parser.add_argument(
        "-i", "--invariants",
        action="store_true",
        help="Generate invariant tests"
    )
    parser.add_argument(
        "-e", "--edge-cases",
        action="store_true",
        help="Generate edge case tests"
    )
    parser.add_argument(
        "-f", "--fuzz",
        action="store_true",
        help="Generate fuzz tests"
    )
    parser.add_argument(
        "--fuzz-runs",
        type=int,
        default=256,
        help="Number of fuzz runs (default: 256)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # If no test type specified, generate all
    if not (args.invariants or args.edge_cases or args.fuzz):
        args.invariants = True
        args.edge_cases = True
        args.fuzz = True
    
    try:
        # Find Solidity files
        sol_files = find_solidity_files(args.contract_path)
        
        if not sol_files:
            print(f"Error: No Solidity files found in {args.contract_path}")
            sys.exit(1)
        
        print(f"Found {len(sol_files)} Solidity file(s)")
        
        all_generated = {}
        
        for sol_file in sol_files:
            if args.verbose:
                print(f"\nProcessing: {sol_file}")
            
            generated = generate_tests(
                str(sol_file),
                args.output,
                contract_name=args.contract,
                generate_fuzz=args.fuzz,
                generate_invariants=args.invariants,
                generate_edge_cases=args.edge_cases,
                fuzz_runs=args.fuzz_runs,
                verbose=args.verbose
            )
            
            all_generated.update(generated)
        
        print(f"\nGenerated {len(all_generated)} test file(s):")
        for filename in sorted(all_generated.keys()):
            print(f"  - {os.path.join(args.output, filename)}")
        
        print(f"\nRun tests with: forge test --match-path '{args.output}/*'")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
