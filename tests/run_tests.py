#!/usr/bin/env python3
"""
Test runner for fabricpy unit tests.

This script runs all unit tests for the fabricpy library and provides
detailed reporting on test results and coverage.
"""

import os
import sys
import unittest
from pathlib import Path

# Add the parent directory to the path so we can import fabricpy
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_all_tests():
    """Run all tests and return the results."""
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern="test_*.py")

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)

    return result


def run_specific_test_module(module_name):
    """Run tests from a specific module."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(f"tests.{module_name}")

    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)

    return result


def print_test_summary(result):
    """Print a summary of test results."""
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, "skipped") else 0
    passed = total_tests - failures - errors - skipped

    print(f"Total Tests Run: {total_tests}")
    print(f"Passed: {passed}")
    print(f"Failed: {failures}")
    print(f"Errors: {errors}")
    print(f"Skipped: {skipped}")

    if failures > 0:
        print(f"\nFAILURES ({failures}):")
        for test, traceback in result.failures:
            print(f"  - {test}")

    if errors > 0:
        print(f"\nERRORS ({errors}):")
        for test, traceback in result.errors:
            print(f"  - {test}")

    success_rate = (passed / total_tests) * 100 if total_tests > 0 else 0
    print(f"\nSuccess Rate: {success_rate:.1f}%")

    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED!")

    print("=" * 70)


def main():
    """Main entry point."""
    print("fabricpy Unit Test Runner")
    print("=" * 70)

    if len(sys.argv) > 1:
        # Run specific test module
        module_name = sys.argv[1]
        if not module_name.startswith("test_"):
            module_name = f"test_{module_name}"

        print(f"Running tests from module: {module_name}")
        result = run_specific_test_module(module_name)
    else:
        # Run all tests
        print("Running all tests...")
        result = run_all_tests()

    print_test_summary(result)

    # Exit with error code if tests failed
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
