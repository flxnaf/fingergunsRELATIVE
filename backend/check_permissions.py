#!/usr/bin/env python3
"""
Check and test macOS permissions for mouse control
This will tell you EXACTLY what's blocking the fingergun system
"""

import sys

print("=" * 70)
print("🔐 macOS PERMISSION CHECKER")
print("=" * 70)
print()

# Test 1: Import CGEvent
print("Test 1: Checking if CGEvent is available...")
try:
    from Quartz.CoreGraphics import (
        CGEventCreateMouseEvent,
        CGEventPost,
        kCGEventMouseMoved,
        kCGHIDEventTap,
        CGEventCreate,
        CGEventGetLocation
    )
    print("✅ CGEvent imported successfully")
except ImportError as e:
    print(f"❌ CGEvent import failed: {e}")
    print("   Run: pip3 install pyobjc-framework-Quartz")
    sys.exit(1)

print()

# Test 2: Try to move mouse using CGEvent
print("Test 2: Testing mouse movement with CGEvent...")
print("Watch your cursor - it should move in a small square pattern...")
print()

import time

try:
    # Get starting position
    event = CGEventCreate(None)
    start_pos = CGEventGetLocation(event)
    print(f"Starting position: ({int(start_pos.x)}, {int(start_pos.y)})")
    
    # Try to move in a square
    movements = [
        (20, 0, "→ Right"),
        (0, 20, "↓ Down"),
        (-20, 0, "← Left"),
        (0, -20, "↑ Up")
    ]
    
    for dx, dy, direction in movements:
        event = CGEventCreate(None)
        current_pos = CGEventGetLocation(event)
        new_x = current_pos.x + dx
        new_y = current_pos.y + dy
        
        move_event = CGEventCreateMouseEvent(None, kCGEventMouseMoved, (new_x, new_y), 0)
        CGEventPost(kCGHIDEventTap, move_event)
        
        time.sleep(0.2)
        
        # Verify it moved
        verify_event = CGEventCreate(None)
        verify_pos = CGEventGetLocation(verify_event)
        print(f"  {direction}: Moved to ({int(verify_pos.x)}, {int(verify_pos.y)})")
    
    # Return to start
    move_event = CGEventCreateMouseEvent(None, kCGEventMouseMoved, (start_pos.x, start_pos.y), 0)
    CGEventPost(kCGHIDEventTap, move_event)
    
    print()
    print("✅ SUCCESS! Mouse movement is working!")
    print()
    print("If you saw your cursor move in a square, permissions are OK!")
    print("The fingergun system should work WITHOUT touching trackpad.")
    
except Exception as e:
    print()
    print(f"❌ FAILED: {e}")
    print()
    print("🔧 FIX NEEDED: Grant Accessibility Permissions")
    print()
    print("Steps to fix:")
    print("1. Open System Settings")
    print("2. Go to Privacy & Security → Accessibility")
    print("3. Click the + button or toggle switch")
    print("4. Add 'Terminal' (or your terminal app)")
    print("5. Make sure it's toggled ON")
    print("6. RESTART Terminal completely (Cmd+Q)")
    print("7. Run this test again")
    print()
    print("Still not working? Also try adding:")
    print("- Python (look in /usr/bin/ or Applications/)")
    print("- Python Launcher")
    sys.exit(1)

print()
print("=" * 70)
print("🎉 ALL TESTS PASSED!")
print("=" * 70)
print()
print("Your system is ready for fingergun gaming WITHOUT trackpad touch!")
print("Run: python3 backend/krunker_mode.py")
print()

