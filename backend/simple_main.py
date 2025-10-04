"""
Simple Main Application - Just the Hybrid Control System
This runs your working hybrid control system without the AI modes
"""

import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time
import sys

# Import the working hybrid control system
from leaning_control_system import LeaningControlSystem

# Safety
pyautogui.PAUSE = 0.01
pyautogui.FAILSAFE = True

def main():
    """Main application - just the hybrid control system"""
    print("🎮 CS:GO Gesture Control - Hybrid System")
    print("=" * 50)
    print("Controls:")
    print("  'g' - Toggle control ON/OFF")
    print("  'q' - Quit")
    print("\nMovement (WASD - Hybrid):")
    print("  - Head FORWARD → Press 'S' (move forward)")
    print("  - Head BACKWARD → Press 'W' (move backward)")
    print("  - Body Lean LEFT → Press 'A' (move left)")
    print("  - Body Lean RIGHT → Press 'D' (move right)")
    print("\nRight Hand: Gun control + shooting")
    print("Left Hand: Crouch (1 finger) / Jump (4 fingers)")
    print("Tongue: Spray emote (T key)")
    print("=" * 50)
    
    # Initialize the hybrid control system
    system = LeaningControlSystem()
    
    try:
        system.run()
    except KeyboardInterrupt:
        print("⏹️  Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print("🎉 Application finished!")

if __name__ == "__main__":
    main()
