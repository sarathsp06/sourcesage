#!/usr/bin/env python3
"""Test script for the Makefile."""

import os
import subprocess
import sys


def test_makefile_exists():
    """Test that the Makefile exists."""
    assert os.path.isfile("Makefile"), "Makefile does not exist"
    print("✓ Makefile exists")


def test_makefile_targets():
    """Test that the Makefile contains the expected targets."""
    expected_targets = [
        "init",
        "test",
        "lint",
        "fix",
        "format",
        "clean",
        "run",
        "build",
        "install",
        "help"
    ]
    
    # Run 'make -pn' to get all targets
    try:
        output = subprocess.check_output(["make", "-pn"], stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running 'make -pn': {e}")
        return False
    
    # Check each expected target
    missing_targets = []
    for target in expected_targets:
        if f"{target}:" not in output:
            missing_targets.append(target)
    
    if missing_targets:
        print(f"Missing targets in Makefile: {', '.join(missing_targets)}")
        return False
    
    print(f"✓ All {len(expected_targets)} expected targets found in Makefile")
    return True


def test_help_target():
    """Test that the help target works."""
    try:
        output = subprocess.check_output(["make", "help"], stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running 'make help': {e}")
        return False
    
    # Check that help output contains descriptions for all targets
    expected_targets = ["init", "test", "lint", "fix", "format", "clean", "run", "build", "install", "help"]
    missing_descriptions = []
    
    for target in expected_targets:
        if target not in output:
            missing_descriptions.append(target)
    
    if missing_descriptions:
        print(f"Help output missing descriptions for: {', '.join(missing_descriptions)}")
        return False
    
    print("✓ Help target works correctly")
    return True


def main():
    """Run all tests."""
    print("=== Testing Makefile ===")
    
    tests = [
        test_makefile_exists,
        test_makefile_targets,
        test_help_target
    ]
    
    success = True
    for test in tests:
        try:
            result = test()
            if result is False:  # Only check if explicitly False
                success = False
        except Exception as e:
            print(f"Error in {test.__name__}: {e}")
            success = False
    
    if success:
        print("\nAll Makefile tests passed!")
        return 0
    else:
        print("\nSome Makefile tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
