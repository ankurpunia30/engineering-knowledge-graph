#!/usr/bin/env python3
"""
Comprehensive test runner for the Engineering Knowledge Graph system.
Runs all verification tests for Parts 2, 3, and 4.
"""

import sys
import os
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_test(test_file, description):
    """Run a test file and return success status."""
    print("\n" + "=" * 70)
    print(f"Running: {description}")
    print("=" * 70)
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            cwd=Path(__file__).parent,
            capture_output=False,
            text=True
        )
        
        success = result.returncode == 0
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"\n{status}: {description}")
        return success
        
    except Exception as e:
        print(f"\n❌ ERROR running {description}: {e}")
        return False


def main():
    """Run all tests and report results."""
    print("\n" + "=" * 70)
    print("ENGINEERING KNOWLEDGE GRAPH - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    
    tests_dir = Path(__file__).parent
    
    test_suite = [
        (tests_dir / "test_part2_requirements.py", "Part 2: Graph Storage (6/6 requirements)"),
        (tests_dir / "test_part3_requirements.py", "Part 3: Query Engine (10/10 tests)"),
        (tests_dir / "test_part4_requirements.py", "Part 4: Natural Language Interface (10/10 tests)"),
        (tests_dir / "test_part5_integration.py", "Part 5: Integration & Polish (end-to-end)"),
        (tests_dir / "test_connectors.py", "Connectors: Docker Compose, Teams, Kubernetes"),
        (tests_dir / "test_graph.py", "Graph: Storage and Models"),
    ]
    
    results = []
    
    for test_file, description in test_suite:
        if not test_file.exists():
            print(f"\n⚠️  SKIPPED: {description} (file not found: {test_file})")
            results.append((description, None))
            continue
            
        success = run_test(str(test_file), description)
        results.append((description, success))
    
    # Print summary
    print("\n\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, success in results if success is True)
    failed = sum(1 for _, success in results if success is False)
    skipped = sum(1 for _, success in results if success is None)
    
    for description, success in results:
        if success is True:
            print(f"✅ {description}")
        elif success is False:
            print(f"❌ {description}")
        else:
            print(f"⚠️  {description} (skipped)")
    
    print("\n" + "=" * 70)
    print(f"Total: {len(results)} test suites")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")
    print("=" * 70)
    
    if failed > 0:
        print("\n⚠️  Some tests failed. Please review the output above.")
        return 1
    elif passed == 0:
        print("\n⚠️  No tests were run successfully.")
        return 1
    else:
        print("\n🎉 All tests passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
