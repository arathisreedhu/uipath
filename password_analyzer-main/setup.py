"""
Setup script for Password Strength Analyzer.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="password-analyzer",
    version="1.0.0",
    author="Password Analyzer Team",
    description="Defensive Password Strength Analyzer and Educational Wordlist Generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/password-analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: Education",
    ],
    python_requires=">=3.10",
    install_requires=[
        "zxcvbn>=4.4.28",
        "nltk>=3.8.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "password-analyzer=password_analyzer.cli:main",
            "password-analyzer-gui=password_analyzer.gui:main",
        ],
    },
)
