"""
Simple test for Krunker mouse control
This will show you exactly what's happening with mouse movements
"""

import pyautogui
from pynput.mouse import Controller as MouseController
import time

# Disable fail-safe
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

print("=" * 70)
print("🎯 KRUNKER MOUSE TEST")
print("=" * 70)
print("\nThis will move your mouse automatically.")
print("Instructions:")
print("1. Open Krunker in your browser")
print("2. Enter a game (wait for pointer lock)")
print("3. Alt+Tab to keep this window visible")
print("4. Watch both windows")
print("\nStarting in 3 seconds...")
time.sleep(3)

# Test both methods
mouse = MouseController()

print("\n📊 TESTING MOUSE CONTROL METHODS\n")

# Test 1: PyAutoGUI
print("Test 1: PyAutoGUI moveRel()")
for i in range(10):
    try:
        pyautogui.moveRel(50, 0)
        time.sleep(0.1)
        pyautogui.moveRel(-50, 0)
        time.sleep(0.1)
        print(f"  {i+1}/10: ✓ Moved")
    except Exception as e:
        print(f"  {i+1}/10: ✗ Failed - {e}")
        
time.sleep(1)

# Test 2: pynput
print("\nTest 2: pynput move()")
for i in range(10):
    try:
        mouse.move(50, 0)
        time.sleep(0.1)
        mouse.move(-50, 0)
        time.sleep(0.1)
        print(f"  {i+1}/10: ✓ Moved")
    except Exception as e:
        print(f"  {i+1}/10: ✗ Failed - {e}")

print("\n" + "=" * 70)
print("✅ TEST COMPLETE")
print("\nDid you see your cursor move?")
print("- If YES in both tests: System works!")
print("- If YES only in desktop: Browser pointer lock is blocking it")
print("- If NO: Check accessibility permissions")
print("\n💡 FOR KRUNKER:")
print("The browser captures mouse in pointer lock mode.")
print("You need to keep moving to overcome the browser's reset.")
print("=" * 70)

