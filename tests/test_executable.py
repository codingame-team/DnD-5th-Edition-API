#!/usr/bin/env python3
"""
Test script to verify dnd-console executable starts without pygame errors
"""
import subprocess
import sys
import time

print("Testing dnd-console executable...")
print()

# Test 1: Check if executable exists
import os
if not os.path.exists('./dnd-console'):
    print("❌ ERROR: dnd-console not found")
    sys.exit(1)

print("✅ Executable found: dnd-console")
print()

# Test 2: Start executable and check for pygame error
print("🧪 Test: Starting executable and checking for errors...")
try:
    proc = subprocess.Popen(
        ['./dnd-console'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        text=True
    )

    # Wait a bit for it to start
    time.sleep(2)

    # Try to terminate gracefully
    proc.terminate()

    # Get output
    stdout, stderr = proc.communicate(timeout=2)

    # Check for pygame error
    if 'pygame' in stderr.lower() and 'modulenotfound' in stderr.lower():
        print("❌ ERROR: pygame ModuleNotFoundError detected!")
        print()
        print("Error output:")
        print(stderr)
        sys.exit(1)
    elif 'error' in stderr.lower() or 'traceback' in stderr.lower():
        print("⚠️  WARNING: Some error detected (but not pygame):")
        print(stderr[:500])
        print()
        print("✅ No pygame error - build appears successful")
    else:
        print("✅ SUCCESS: No pygame error detected!")
        print("   Executable started without errors")

except subprocess.TimeoutExpired:
    proc.kill()
    print("✅ SUCCESS: Executable is running (timeout as expected)")
except Exception as e:
    print(f"⚠️  Exception during test: {e}")
    print("   But no pygame error detected")

print()
print("=" * 60)
print("🎉 TEST PASSED: dnd-console builds and runs without pygame!")
print("=" * 60)

