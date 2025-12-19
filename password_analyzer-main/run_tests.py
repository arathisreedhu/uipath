#!/usr/bin/env python3
"""
Test runner script for Password Analyzer.
Runs all tests and provides a summary.
"""

import subprocess
import sys
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80 + "\n")


def run_tests():
    """Run all tests with pytest."""
    print_header("PASSWORD ANALYZER - TEST SUITE")
    
    print("Checking if pytest is installed...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--version"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
    except Exception as e:
        print(f"❌ pytest not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-cov"])
    
    print_header("Running All Tests")
    
    # Run tests with verbose output
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        cwd=Path(__file__).parent
    )
    
    if result.returncode == 0:
        print_header("✅ ALL TESTS PASSED")
    else:
        print_header("❌ SOME TESTS FAILED")
    
    return result.returncode


def run_coverage():
    """Run tests with coverage report."""
    print_header("Running Tests with Coverage")
    
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/",
            "--cov=password_analyzer",
            "--cov-report=term-missing",
            "--cov-report=html"
        ],
        cwd=Path(__file__).parent
    )
    
    if result.returncode == 0:
        print("\n✅ Coverage report generated in htmlcov/index.html")
    
    return result.returncode


def run_specific_tests():
    """Run specific test categories."""
    print_header("Test Categories")
    
    test_files = [
        ("Analyzer Tests", "tests/test_analyzer.py"),
        ("Entropy Tests", "tests/test_entropy.py"),
        ("Pattern Detector Tests", "tests/test_pattern_detector.py"),
        ("Wordlist Generator Tests", "tests/test_wordlist_generator.py"),
        ("EULA Manager Tests", "tests/test_eula.py"),
    ]
    
    results = {}
    
    for name, test_file in test_files:
        print(f"\nRunning {name}...")
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_file, "-v"],
            cwd=Path(__file__).parent,
            capture_output=True
        )
        results[name] = result.returncode == 0
        print("✅ PASSED" if results[name] else "❌ FAILED")
    
    print_header("Test Summary")
    for name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name}: {status}")
    
    return 0 if all(results.values()) else 1


def main():
    """Main test runner."""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "coverage":
            sys.exit(run_coverage())
        elif command == "specific":
            sys.exit(run_specific_tests())
        elif command == "help":
            print("Usage: python run_tests.py [command]")
            print("\nCommands:")
            print("  (no command)  - Run all tests")
            print("  coverage      - Run tests with coverage report")
            print("  specific      - Run tests by category")
            print("  help          - Show this help message")
            return
        else:
            print(f"Unknown command: {command}")
            print("Use 'help' for available commands")
            sys.exit(1)
    else:
        sys.exit(run_tests())


if __name__ == '__main__':
    main()
