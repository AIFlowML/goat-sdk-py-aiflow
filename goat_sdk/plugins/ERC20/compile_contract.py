"""Compile Solidity contracts."""

import json
from pathlib import Path
from typing import Tuple
from solcx import compile_standard, install_solc


def compile_contract() -> Tuple[dict, str]:
    """Compile the TestToken contract.
    
    Returns:
        Tuple containing the contract ABI and bytecode.
    """
    # Install solc
    install_solc("0.8.20")

    # Get contract path and node_modules path
    contract_path = Path(__file__).parent / "contracts" / "TestToken.sol"
    node_modules = Path(__file__).parent / "node_modules"
    oz_contracts = node_modules / "@openzeppelin/contracts"

    # Read contract source
    with open(contract_path, "r", encoding="utf-8") as f:
        contract_source = f.read()

    # Read OpenZeppelin sources
    sources = {
        "TestToken.sol": {
            "content": contract_source
        }
    }

    # Add OpenZeppelin sources
    oz_files = [
        "token/ERC20/ERC20.sol",
        "token/ERC20/IERC20.sol",
        "token/ERC20/extensions/IERC20Metadata.sol",
        "utils/Context.sol",
        "interfaces/draft-IERC6093.sol"
    ]

    for oz_file in oz_files:
        with open(oz_contracts / oz_file, "r", encoding="utf-8") as f:
            sources[f"@openzeppelin/contracts/{oz_file}"] = {
                "content": f.read()
            }

    # Compile contract
    compiled_sol = compile_standard(
        {
            "language": "Solidity",
            "sources": sources,
            "settings": {
                "outputSelection": {
                    "*": {
                        "*": ["abi", "evm.bytecode"]
                    }
                }
            }
        },
        solc_version="0.8.20",
        allow_paths=[str(node_modules)]
    )

    # Extract ABI and bytecode
    abi = compiled_sol["contracts"]["TestToken.sol"]["TestToken"]["abi"]
    bytecode = compiled_sol["contracts"]["TestToken.sol"]["TestToken"]["evm"]["bytecode"]["object"]

    # Create build directory if it doesn't exist
    build_dir = Path(__file__).parent / "build"
    build_dir.mkdir(exist_ok=True)

    # Write ABI and bytecode to files
    with open(build_dir / "TestToken.abi", "w", encoding="utf-8") as f:
        json.dump(abi, f, indent=2)
    with open(build_dir / "TestToken.bin", "w", encoding="utf-8") as f:
        f.write(bytecode)

    return abi, bytecode
