"""Setup file for GOAT SDK."""

from setuptools import setup, find_packages

setup(
    name="goat_sdk",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "web3>=6.0.0",
        "eth-account>=0.8.0",
        "eth-typing>=3.0.0",
        "typing-extensions>=4.5.0",
        "solana>=0.18.0",
        "anchorpy>=0.3.0",
        "base58>=2.1.0",
        "construct-typing>=0.5.0",
    ],
    python_requires=">=3.11",
)
