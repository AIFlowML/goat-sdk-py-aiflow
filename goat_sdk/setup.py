"""Setup script for Mode SDK."""

from setuptools import setup, find_namespace_packages

setup(
    name="goat-sdk",
    version="0.1.0",
    description="Mode SDK for Python",
    author="Mode Labs",
    author_email="info@mode.network",
    packages=find_namespace_packages(include=["goat_sdk*", "plugins*"]),
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8.0",
        "pydantic>=2.0.0",
        "tenacity>=8.0.0",
        "solana>=0.30.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.20.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
) 