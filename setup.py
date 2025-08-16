"""
Setup script for the Gaming System
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gaming-system",
    version="1.0.0",
    author="Gaming System Team",
    description="A WebSocket-based dice gambling game system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    package_dir={'': '.'},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "protobuf>=4.21.0",
        "websockets>=11.0",
        "bcrypt>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "flake8>=5.0.0",
            "black>=22.0.0",
            "mypy>=1.0.0",
        ],
        "prod": [
            "uvloop>=0.17.0",
            "structlog>=22.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "game-server=run_server:main",
            "game-client=run_client:main",
        ],
    },
)