#!/usr/bin/env python3
"""
fuzz-test-generator.py
Generates Foundry fuzz tests for smart contracts.
Supports: test template generation, invariant tests, stateful fuzz tests.
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class ContractInfo:
    """Parsed contract information."""
    name: str
    path: str
    functions: List[dict] = field(default_factory=list)
    state_vars: List[dict] = field(default_factory=list)
    events: List[str] = field(default_factory=list)
    modifiers: List[str] = field(default_factory=list)
    is_payable: bool = False


@dataclass
class FuzzConfig:
    """Fuzzing configuration."""
    runs: int = 10000
    depth: int = 10
    invariant_runs: int = 1000
    stateful_depth: int = 50
    include_edge_cases: bool = True
    include_boundaries: bool = True


class SolidityParser:
    """Parse Solidity contracts to extract testable information."""

    def __init__(self, source: str):
        self.source = source

    def parse_contract(self, contract_name: str, path: str) -> ContractInfo:
        """Parse a single contract from source."""
        info = ContractInfo(name=contract_name, path=path)

        # Extract functions
        func_pattern = r'function\s+(\w+)\s*\(([^)]*)\)[^{]*{([^}]*)}'
        for match in re.finditer(func_pattern, self.source):
            func_name = match.group(1)
            params = match.group(2).strip()
            body = match.group(3)

            # Skip constructor and receive/fallback
            if func_name in ('constructor', 'receive', 'fallback'):
                continue

            # Determine visibility
            visibility = 'public'
            if 'external' in match.group(0):
                visibility = 'external'
            elif 'internal' in match.group(0):
                visibility = 'internal'
            elif 'private' in match.group(0):
                visibility = 'private'

            # Check if payable
            is_payable = 'payable' in match.group(0)

            # Parse parameters
            param_list = []
            if params:
                for param in params.split(','):
                    param = param.strip()
                    if param:
                        param_list.append(param)

            info.functions.append({
                'name': func_name,
                'params': param_list,
                'visibility': visibility,
                'is_payable': is_payable,
                'body': body
            })

        # Extract state variables
        var_pattern = r'(?:uint\d*|int\d*|address|bool|bytes\d*|string)\s+(?:public|private|internal)?\s*(\w+)'
        for match in re.finditer(var_pattern, self.source):
            info.state_vars.append({
                'name': match.group(1),
                'type': match.group(0).split()[0]
            })

        # Extract events
        event_pattern = r'event\s+(\w+)\s*\(([^)]*)\)'
        for match in re.finditer(event_pattern, self.source):
            info.events.append(match.group(1))

        # Extract modifiers
        modifier_pattern = r'modifier\s+(\w+)'
        for match in re.finditer(modifier_pattern, self.source):
            info.modifiers.append(match.group(1))

        return info


class TestGenerator:
    """Generate Foundry fuzz tests."""

    def __init__(self, config: FuzzConfig):
        self.config = config

    def generate_test_template(self, contract: ContractInfo) -> str:
        """Generate basic test template for a contract."""
        lines = [
            "// SPDX-License-Identifier: MIT",
            "pragma solidity ^0.8.0;",
            "",
            "import \"forge-std/Test.sol\";",
            f"import \"../{contract.path}\";",
            "",
            f"contract {contract.name}Test is Test {{",
            f"    {contract.name} private target;",
            "",
            "    function setUp() public {",
            f"        target = new {contract.name}();",
            "    }",
            "",
        ]

        # Generate test stubs for each public/external function
        for func in contract.functions:
            if func['visibility'] in ('public', 'external'):
                lines.extend(self._generate_function_test_stub(func))

        lines.append("}")
        return '\n'.join(lines)

    def _generate_function_test_stub(self, func: dict) -> List[str]:
        """Generate a test stub for a single function."""
        func_name = func['name']
        params = func['params']

        # Generate fuzz parameters
        fuzz_params = []
        for param in params:
            param_type = param.split()[0] if param else 'uint256'
            if 'uint' in param_type:
                fuzz_params.append(f'uint256 {param.split()[-1]}')
            elif 'int' in param_type:
                fuzz_params.append(f'int256 {param.split()[-1]}')
            elif 'address' in param_type:
                fuzz_params.append(f'address {param.split()[-1]}')
            elif 'bool' in param_type:
                fuzz_params.append(f'bool {param.split()[-1]}')
            elif 'bytes' in param_type:
                fuzz_params.append(f'bytes memory {param.split()[-1]}')
            elif 'string' in param_type:
                fuzz_params.append(f'string memory {param.split()[-1]}')
            else:
                fuzz_params.append(f'uint256 {param.split()[-1]}')

        param_str = ', '.join(fuzz_params) if fuzz_params else ''
        call_params = ', '.join([p.split()[-1] for p in params]) if params else ''

        lines = [
            f"    function testFuzz_{func_name}({param_str}) public {{",
            f"        // TODO: Add assertions",
            f"        target.{func_name}({call_params});",
            f"        // Assert expected behavior",
            "    }",
            "",
        ]

        return lines

    def generate_invariant_tests(self, contract: ContractInfo) -> str:
        """Generate invariant tests for a contract."""
        lines = [
            "// SPDX-License-Identifier: MIT",
            "pragma solidity ^0.8.0;",
            "",
            "import \"forge-std/Test.sol\";",
            f"import \"../{contract.path}\";",
            "",
            f"contract {contract.name}InvariantTest is Test {{",
            f"    {contract.name} private target;",
            "",
            "    function setUp() public {",
            f"        target = new {contract.name}();",
            "    }",
            "",
            "    // Invariant: Contract should never hold negative balance",
            "    function invariant_balanceNonNegative() public {",
            "        assertGe(address(target).balance, 0);",
            "    }",
            "",
        ]

        # Generate invariant tests for state variables
        for var in contract.state_vars:
            var_name = var['name']
            var_type = var['type']

            if 'uint' in var_type:
                lines.extend([
                    f"    // Invariant: {var_name} should never underflow",
                    f"    function invariant_{var_name}NonNegative() public {{",
                    f"        // TODO: Add assertion for {var_name}",
                    f"        // assertGe(target.{var_name}(), 0);",
                    "    }",
                    "",
                ])

        lines.append("}")
        return '\n'.join(lines)

    def generate_stateful_fuzz_test(self, contract: ContractInfo) -> str:
        """Generate stateful fuzz test with handler pattern."""
        lines = [
            "// SPDX-License-Identifier: MIT",
            "pragma solidity ^0.8.0;",
            "",
            "import \"forge-std/Test.sol\";",
            f"import \"../{contract.path}\";",
            "",
            f"contract {contract.name}StatefulFuzzTest is Test {{",
            f"    {contract.name} private target;",
            "",
            "    // State tracking",
            "    uint256 private actionCount;",
            "    mapping(uint256 => bool) private usedSelectors;",
            "",
            "    function setUp() public {",
            f"        target = new {contract.name}();",
            "    }",
            "",
            "    // Stateful fuzz: call functions in sequence",
            "    function fuzz_stateful_sequence(uint256[] calldata actions) public {",
            "        for (uint256 i = 0; i < actions.length; i++) {",
            "            _executeAction(actions[i]);",
            "            actionCount++;",
            "        }",
            "    }",
            "",
            "    function _executeAction(uint256 action) internal {",
            "        // TODO: Implement action dispatch",
            "        // Example:",
            "        // if (action % 3 == 0) { target.deposit{value: msg.value}(); }",
            "        // else if (action % 3 == 1) { target.withdraw(); }",
            "        // else { target.transfer(); }",
            "    }",
            "",
            "    // Invariant: action count should match executed actions",
            "    function invariant_actionCountMatches() public {",
            "        // Assert state consistency",
            "    }",
            "",
            "    // Invariant: no reentrancy during stateful execution",
            "    function invariant_noReentrancy() public {",
            "        // Assert no reentrant calls occurred",
            "    }",
            "}",
        ]

        return '\n'.join(lines)

    def generate_cheatcode_tests(self, contract: ContractInfo) -> str:
        """Generate tests using Foundry cheatcodes."""
        lines = [
            "// SPDX-License-Identifier: MIT",
            "pragma solidity ^0.8.0;",
            "",
            "import \"forge-std/Test.sol\";",
            f"import \"../{contract.path}\";",
            "",
            f"contract {contract.name}CheatcodeTest is Test {{",
            f"    {contract.name} private target;",
            "",
            "    function setUp() public {",
            f"        target = new {contract.name}();",
            "    }",
            "",
            "    // Test with specific block numbers",
            "    function testFuzz_withBlockNumber(uint256 blockNumber) public {",
            "        vm.roll(blockNumber);",
            "        // Test behavior at specific block",
            "    }",
            "",
            "    // Test with specific timestamps",
            "    function testFuzz_withTimestamp(uint256 timestamp) public {",
            "        vm.warp(timestamp);",
            "        // Test time-dependent behavior",
            "    }",
            "",
            "    // Test with pranked caller",
            "    function testFuzz_withPrank(address caller) public {",
            "        vm.prank(caller);",
            "        // Test access control",
            "    }",
            "",
            "    // Test with specific ether balance",
            "    function testFuzz_withBalance(uint256 balance) public {",
            "        vm.deal(address(this), balance);",
            "        // Test with specific balance",
            "    }",
            "",
            "    // Test expectRevert",
            "    function testFuzz_expectRevert(uint256 amount) public {",
            "        vm.expectRevert();",
            "        // target.someFunction(amount);",
            "    }",
            "",
            "    // Test expectEmit",
            "    function testFuzz_expectEmit() public {",
            "        // vm.expectEmit(true, true, true, true);",
            "        // emit Transfer(address(this), address(target), amount);",
            "        // target.someFunction();",
            "    }",
            "}",
        ]

        return '\n'.join(lines)

    def generate_coverage_config(self, contract: ContractInfo) -> str:
        """Generate Foundry configuration for coverage analysis."""
        config = {
            "src": "src",
            "out": "out",
            "libs": ["lib"],
            "test": "test",
            "script": "script",
            "cache_path": "cache",
            "solc": "0.8.20",
            "optimizer": True,
            "optimizer_runs": 200,
            "fuzz": {
                "runs": self.config.runs,
                "max_local_rejects": 65536,
                "max_global_rejects": 1024,
                "seed": "0x3e8",
                "dictionary_weight": 40,
                "include_storage": True,
                "include_push_bytes": True
            },
            "invariant": {
                "runs": self.config.invariant_runs,
                "depth": self.config.depth,
                "fail_on_revert": False,
                "call_override": False,
                "shrink_run_limit": 5000
            },
            "ffi": False,
            "ast": False,
            "force": False,
            "evm_version": "shanghai",
            "gas_reports": ["*"],
            "gas_reports_ignore": [],
            "no_match_test": f"testFuzz_{contract.name}.*",
            "no_match_contract": f"{contract.name}.*"
        }
        return json.dumps(config, indent=2)


def find_contracts(project_dir: str) -> List[Path]:
    """Find all Solidity contracts in project."""
    contracts = []
    for path in Path(project_dir).rglob("*.sol"):
        # Skip test files and interfaces
        if "test" in path.name.lower() or "interface" in path.name.lower():
            continue
        if "mock" in path.name.lower():
            continue
        contracts.append(path)
    return contracts


def extract_contract_name(source: str) -> Optional[str]:
    """Extract contract name from Solidity source."""
    match = re.search(r'contract\s+(\w+)', source)
    return match.group(1) if match else None


def main():
    parser = argparse.ArgumentParser(
        description="Generate Foundry fuzz tests for smart contracts"
    )
    parser.add_argument(
        "--contract",
        type=str,
        help="Specific contract name to generate tests for"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="test",
        help="Output directory for generated tests"
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=10000,
        help="Number of fuzz runs"
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=10,
        help="Fuzzing depth"
    )
    parser.add_argument(
        "--project-dir",
        type=str,
        default=".",
        help="Project root directory"
    )
    parser.add_argument(
        "--type",
        choices=["template", "invariant", "stateful", "cheatcode", "all"],
        default="all",
        help="Type of test to generate"
    )

    args = parser.parse_args()

    config = FuzzConfig(runs=args.runs, depth=args.depth)
    generator = TestGenerator(config)

    # Find contracts
    contracts = find_contracts(args.project_dir)
    if not contracts:
        print("No Solidity contracts found.")
        sys.exit(1)

    # Filter by contract name if specified
    if args.contract:
        contracts = [c for c in contracts if args.contract in c.name]
        if not contracts:
            print(f"Contract '{args.contract}' not found.")
            sys.exit(1)

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate tests for each contract
    for contract_path in contracts:
        source = contract_path.read_text()
        contract_name = extract_contract_name(source)

        if not contract_name:
            continue

        print(f"Generating tests for: {contract_name}")

        # Parse contract
        parser = SolidityParser(source)
        contract_info = parser.parse_contract(contract_name, str(contract_path.relative_to(args.project_dir)))

        # Generate requested test types
        test_types = ["template", "invariant", "stateful", "cheatcode"] if args.type == "all" else [args.type]

        for test_type in test_types:
            if test_type == "template":
                content = generator.generate_test_template(contract_info)
                filename = f"{contract_name}Test.t.sol"
            elif test_type == "invariant":
                content = generator.generate_invariant_tests(contract_info)
                filename = f"{contract_name}Invariant.t.sol"
            elif test_type == "stateful":
                content = generator.generate_stateful_fuzz_test(contract_info)
                filename = f"{contract_name}Stateful.t.sol"
            elif test_type == "cheatcode":
                content = generator.generate_cheatcode_tests(contract_info)
                filename = f"{contract_name}Cheatcode.t.sol"
            else:
                continue

            output_path = output_dir / filename
            output_path.write_text(content)
            print(f"  Generated: {output_path}")

    # Generate coverage config
    if contracts:
        first_source = contracts[0].read_text()
        first_name = extract_contract_name(first_source)
        if first_name:
            parser = SolidityParser(first_source)
            contract_info = parser.parse_contract(first_name, str(contracts[0].relative_to(args.project_dir)))
            config_content = generator.generate_coverage_config(contract_info)
            config_path = output_dir / "foundry.toml"
            config_path.write_text(config_content)
            print(f"\nGenerated config: {config_path}")

    print(f"\nTest generation complete. Output: {output_dir}")
    print(f"Fuzz runs: {args.runs}, Depth: {args.depth}")


if __name__ == "__main__":
    main()
