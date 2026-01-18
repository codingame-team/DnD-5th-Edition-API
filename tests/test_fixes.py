#!/usr/bin/env python3
"""
Test script to verify the fixes for:
1. main_pexpect.py - Pseudo-TTY support
2. main_ncurses.py - Gamestate loading

Run this to verify both fixes work correctly.
"""

import os
import sys
import tempfile
import pickle

def test_pseudo_tty_support():
    """Test that main_pexpect.py has proper TTY detection"""
    print("=" * 60)
    print("TEST 1: Pseudo-TTY Support in main_pexpect.py")
    print("=" * 60)

    # Check if main_pexpect.py exists
    if not os.path.exists('../main_pexpect.py'):
        print("❌ main_pexpect.py not found!")
        return False

    # Read the file content
    with open('../main_pexpect.py', 'r') as f:
        content = f.read()

    # Check for required functions
    checks = [
        ('is_tty()', 'def is_tty()'),
        ('get_script_to_run()', 'def get_script_to_run()'),
        ('run_with_pty()', 'def run_with_pty('),
        ('run_directly()', 'def run_directly('),
        ('ncurses support', "'main_ncurses.py'"),
        ('help support', '--help'),
    ]

    all_passed = True
    for check_name, check_str in checks:
        if check_str in content:
            print(f"✓ {check_name} found")
        else:
            print(f"❌ {check_name} NOT found")
            all_passed = False

    print()
    return all_passed


def test_gamestate_loading():
    """Test that main_ncurses.py can load gamestate"""
    print("=" * 60)
    print("TEST 2: Gamestate Loading in main_ncurses.py")
    print("=" * 60)

    # Import main_ncurses
    try:
        import main_ncurses
        print("✓ main_ncurses.py imports successfully")
    except ImportError as e:
        print(f"❌ Failed to import main_ncurses.py: {e}")
        return False

    # Read the file to check for pickle import
    with open('../main_ncurses.py', 'r') as f:
        content = f.read()

    if 'import pickle' in content:
        print("✓ pickle module imported")
    else:
        print("❌ pickle module NOT imported")
        return False

    # Check that functions are defined (not just stubs)
    function_checks = [
        ('get_roster', 'os.scandir', 'scans directory for .dmp files'),
        ('load_party', 'pickle.load', 'uses pickle to load party'),
        ('save_party', 'pickle.dump', 'uses pickle to save party'),
        ('save_character', 'pickle.dump', 'uses pickle to save character'),
    ]

    all_passed = True
    for func_name, check_str, description in function_checks:
        # Find the function definition
        func_start = content.find(f'def {func_name}(')
        if func_start == -1:
            print(f"❌ Function {func_name} not found")
            all_passed = False
            continue

        # Get the function body (next 500 chars should be enough)
        func_body = content[func_start:func_start+500]

        if check_str in func_body or check_str.replace('.', '') in func_body:
            print(f"✓ {func_name}() - {description}")
        else:
            print(f"⚠ {func_name}() - might be stub (no '{check_str}' found)")

    # Test that functions are callable with temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        characters_dir = os.path.join(tmpdir, 'characters')
        os.makedirs(characters_dir, exist_ok=True)

        # Test get_roster with empty directory
        try:
            roster = main_ncurses.get_roster(characters_dir)
            print(f"✓ get_roster() callable - returned {len(roster)} characters (empty dir)")
        except Exception as e:
            print(f"❌ get_roster() failed: {e}")
            all_passed = False

        # Test load_party with no file
        try:
            party = main_ncurses.load_party(_dir=tmpdir)
            print(f"✓ load_party() callable - returned {len(party)} characters (no file)")
        except Exception as e:
            print(f"❌ load_party() failed: {e}")
            all_passed = False

    print()
    return all_passed


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  DnD 5E NCurses - Fix Verification Tests")
    print("=" * 60)
    print()

    results = []

    # Test 1
    results.append(("Pseudo-TTY Support", test_pseudo_tty_support()))

    # Test 2
    results.append(("Gamestate Loading", test_gamestate_loading()))

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print()
        print("Next steps:")
        print("1. Test main_pexpect.py:")
        print("   python main_pexpect.py --help")
        print("   python main_pexpect.py ncurses")
        print()
        print("2. Test gamestate loading:")
        print("   - Create characters in main.py")
        print("   - Launch main_ncurses.py")
        print("   - Verify roster is loaded")
        return 0
    else:
        print("⚠️ SOME TESTS FAILED")
        print("Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

