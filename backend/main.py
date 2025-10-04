"""
Main CS:GO Gesture Control Application
Integrates all systems: Hybrid Control + Tutorial Mode + Backseat Gamer Mode
"""

import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time
import sys
import os

# Import our custom modules
from leaning_control_system import LeaningControlSystem
from tutorial_mode import tutorial_mode
from backseat_mode import backseat_mode
from config import config

# Safety
pyautogui.PAUSE = 0.01
pyautogui.FAILSAFE = True

class MainApplication:
    """Main application with mode switching"""
    
    def __init__(self):
        # Initialize the hybrid control system
        self.control_system = LeaningControlSystem()
        
        # Mode states
        self.current_mode = 'normal'  # 'normal', 'tutorial', 'backseat'
        self.control_enabled = False
        
        # Performance tracking
        self.frame_count = 0
        self.last_frame_time = time.time()
        
        print("🎮 CS:GO Gesture Control - Main Application")
        print("=" * 60)
        self._print_mode_instructions()
    
    def _print_mode_instructions(self):
        """Print mode switching instructions"""
        print("\n🎯 MODE CONTROLS:")
        print("  'g' - Toggle control ON/OFF")
        print("  't' - Switch to Tutorial Mode")
        print("  'b' - Switch to Backseat Gamer Mode")
        print("  'n' - Switch to Normal Mode")
        print("  'q' - Quit")
        
        print(f"\n🎮 CURRENT MODE: {self.current_mode.upper()}")
        print(f"🎯 CONTROL: {'ENABLED' if self.control_enabled else 'DISABLED'}")
        
        print("\n📋 GESTURE CONTROLS:")
        print("  Head FORWARD → Press 'S' (move forward)")
        print("  Head BACKWARD → Press 'W' (move backward)")
        print("  Body Lean LEFT → Press 'A' (move left)")
        print("  Body Lean RIGHT → Press 'D' (move right)")
        print("  Right Hand: Gun control + shooting")
        print("  Left Hand: Crouch (1 finger) / Jump (4 fingers)")
        print("  Tongue: Spray emote (T key)")
        
        print("\n🤖 AI FEATURES:")
        print("  Tutorial Mode: Step-by-step gesture training with AI tips")
        print("  Backseat Mode: AI coach with live commentary and character")
        
        print("\n" + "=" * 60)
    
    def run(self):
        """Main application loop"""
        # Initialize camera
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        if not cap.isOpened():
            print("❌ Error: Could not open camera")
            return
        
        print("✅ Camera initialized successfully")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    time.sleep(0.1)
                    continue
                
                self.frame_count += 1
                current_time = time.time()
                if current_time - self.last_frame_time >= 1.0:
                    fps = self.frame_count / (current_time - self.last_frame_time)
                    print(f"📊 Frame {self.frame_count}: Running... FPS: {fps:.1f}")
                    self.frame_count = 0
                    self.last_frame_time = current_time
                
                frame = cv2.flip(frame, 1)
                h, w, _ = frame.shape
                
                # Process frame based on current mode
                status_message = self._process_frame(frame, w, h)
                
                # Display mode and status information
                self._draw_status_overlay(frame, status_message)
                
                # Show frame
                cv2.imshow('CS:GO Gesture Control - Main Application', frame)
                
                # Handle keyboard input
                self._handle_keyboard_input()
                
        except KeyboardInterrupt:
            print("⏹️  Interrupted by user")
        except Exception as e:
            print(f"❌ Error in main loop: {e}")
        finally:
            self._cleanup(cap)
    
    def _process_frame(self, frame: np.ndarray, w: int, h: int) -> str:
        """Process frame based on current mode"""
        if self.current_mode == 'tutorial':
            return self._process_tutorial_mode(frame, w, h)
        elif self.current_mode == 'backseat':
            return self._process_backseat_mode(frame, w, h)
        else:  # normal mode
            return self._process_normal_mode(frame, w, h)
    
    def _process_normal_mode(self, frame: np.ndarray, w: int, h: int) -> str:
        """Process frame in normal mode (basic hybrid control)"""
        # Use the existing leaning control system
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process hands
        hand_results = self.control_system.hands.process(rgb_frame)
        
        # Process pose
        pose_results = self.control_system.pose.process(rgb_frame)
        
        # Process face
        face_results = self.control_system.face_mesh.process(rgb_frame)
        
        # Initialize variables
        left_right_lean = 0
        head_yaw, head_pitch = 0, 0
        active_wasd_keys = set()
        wasd_states = {'w': False, 'a': False, 's': False, 'd': False}
        
        gun_active = False
        is_shooting = False
        shoot_status = "No right hand"
        left_action = None
        left_status = "No left hand"
        tongue_out = False
        tongue_status = "No face"
        
        # Process pose for body leaning (A/D only)
        if pose_results and pose_results.pose_landmarks:
            try:
                # Draw pose landmarks
                mp_drawing = mp.solutions.drawing_utils
                mp_pose = mp.solutions.pose
                mp_drawing.draw_landmarks(
                    frame, pose_results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2)
                )
                
                # Body leaning for A/D only
                from leaning_control_system import calculate_lean_pose
                left_right_lean = calculate_lean_pose(pose_results.pose_landmarks, w, h)
                
            except Exception as e:
                print(f"Error processing pose: {e}")
        
        # Process face for head pose (W/S) and tongue detection
        if face_results and face_results.multi_face_landmarks:
            try:
                face_landmarks = face_results.multi_face_landmarks[0]
                
                # Draw face mesh
                mp_face_mesh = mp.solutions.face_mesh
                mp_drawing.draw_landmarks(
                    frame, face_landmarks, mp_face_mesh.FACEMESH_CONTOURS,
                    None, mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1)
                )
                
                # Head pose for W/S movement
                from leaning_control_system import calculate_head_pose
                head_yaw, head_pitch = calculate_head_pose(face_landmarks, w, h)
                
                # Tongue detection for spray emote
                tongue_out, tongue_status = self.control_system.tongue_controller.update(
                    face_landmarks, self.control_enabled
                )
                
            except Exception as e:
                print(f"Error processing face: {e}")
        
        # Update WASD controller
        active_wasd_keys, wasd_states = self.control_system.wasd_controller.update(
            left_right_lean, head_pitch, self.control_enabled
        )
        
        # Process hands
        if hand_results and hand_results.multi_hand_landmarks:
            try:
                # Draw hand landmarks
                mp_hands = mp.solutions.hands
                for hand_landmarks in hand_results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
                        mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=2)
                    )
                
                # Identify hands
                left_hand, right_hand = self.control_system.identify_hands(hand_results.multi_hand_landmarks)
                
                # Process right hand
                if right_hand:
                    try:
                        gun_active = self.control_system.gun_detector.update(right_hand)
                        
                        if gun_active:
                            is_shooting, shoot_status = self.control_system.shooting_controller.update(
                                right_hand, gun_active
                            )
                            self.control_system.mouse_controller.update(right_hand, gun_active)
                        else:
                            self.control_system.shooting_controller.force_release()
                            
                    except Exception as e:
                        print(f"Error processing right hand: {e}")
                
                # Process left hand
                if left_hand:
                    try:
                        left_action, left_status = self.control_system.left_hand_controller.update(
                            left_hand, self.control_enabled
                        )
                    except Exception as e:
                        print(f"Error processing left hand: {e}")
                        
            except Exception as e:
                print(f"Error processing hands: {e}")
        
        # Display status
        self.control_system.display_status(frame, wasd_states, gun_active, shoot_status, 
                                         left_status, tongue_status, left_right_lean, head_pitch, tongue_out)
        
        return f"Normal Mode | Control: {'ON' if self.control_enabled else 'OFF'}"
    
    def _process_tutorial_mode(self, frame: np.ndarray, w: int, h: int) -> str:
        """Process frame in tutorial mode"""
        # Start tutorial if not already started
        if not hasattr(tutorial_mode, '_tutorial_started'):
            tutorial_mode.start_tutorial()
            tutorial_mode._tutorial_started = True
        
        # Create gesture data for tutorial evaluation
        gesture_data = {
            'gun_active': False,
            'is_shooting': False,
            'wasd_states': {'w': False, 'a': False, 's': False, 'd': False},
            'left_action': None,
            'tongue_out': False,
            'head_pitch': 0,
            'left_right_lean': 0
        }
        
        # Get basic gesture data (simplified for tutorial)
        # This would normally come from the full gesture processing
        # For now, we'll use placeholder data
        
        # Update tutorial
        tutorial_complete, status_message = tutorial_mode.update_tutorial(gesture_data, frame)
        
        if tutorial_complete:
            print("🎉 Tutorial completed! Switching to Normal Mode.")
            self.current_mode = 'normal'
            tutorial_mode._tutorial_started = False
        
        return f"Tutorial Mode | {status_message}"
    
    def _process_backseat_mode(self, frame: np.ndarray, w: int, h: int) -> str:
        """Process frame in backseat gamer mode"""
        # Start backseat mode if not already started
        if not backseat_mode.is_active_mode():
            backseat_mode.start_backseat_mode()
        
        # Create gesture data for backseat evaluation
        gesture_data = {
            'gun_active': False,
            'is_shooting': False,
            'wasd_states': {'w': False, 'a': False, 's': False, 'd': False},
            'left_action': None,
            'tongue_out': False,
            'head_pitch': 0,
            'left_right_lean': 0
        }
        
        # Update backseat mode
        status_message = backseat_mode.update_backseat_mode(gesture_data, frame)
        
        return status_message
    
    def _draw_status_overlay(self, frame: np.ndarray, status_message: str):
        """Draw status overlay on frame"""
        h, w = frame.shape[:2]
        
        # Mode indicator
        mode_color = {
            'normal': (0, 255, 0),
            'tutorial': (255, 255, 0),
            'backseat': (255, 0, 255)
        }.get(self.current_mode, (255, 255, 255))
        
        cv2.putText(frame, f"MODE: {self.current_mode.upper()}", (w - 200, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, mode_color, 2)
        
        # Status message
        cv2.putText(frame, status_message, (10, h - 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Instructions
        cv2.putText(frame, "Press 't' for Tutorial | 'b' for Backseat | 'n' for Normal | 'g' to toggle | 'q' to quit", 
                   (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    def _handle_keyboard_input(self):
        """Handle keyboard input for mode switching"""
        try:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # 'q' or ESC to quit
                print("⏹️  Quit key pressed - exiting...")
                sys.exit(0)
            elif key == ord('g'):
                self.control_enabled = not self.control_enabled
                if not self.control_enabled:
                    self.control_system.shooting_controller.force_release()
                    self.control_system.wasd_controller.release_all_keys()
                print(f"\n{'='*50}")
                print(f"🎯 Control {'ENABLED ✓' if self.control_enabled else 'DISABLED ✗'}")
                print(f"{'='*50}\n")
            elif key == ord('t'):
                self._switch_to_mode('tutorial')
            elif key == ord('b'):
                self._switch_to_mode('backseat')
            elif key == ord('n'):
                self._switch_to_mode('normal')
        except Exception as e:
            print(f"Error handling keyboard input: {e}")
    
    def _switch_to_mode(self, new_mode: str):
        """Switch to a new mode"""
        if new_mode == self.current_mode:
            return
        
        # Cleanup current mode
        if self.current_mode == 'backseat' and backseat_mode.is_active_mode():
            backseat_mode.stop_backseat_mode()
        
        # Switch mode
        self.current_mode = new_mode
        
        print(f"\n{'='*50}")
        print(f"🔄 Switched to {new_mode.upper()} MODE")
        print(f"{'='*50}\n")
        
        if new_mode == 'tutorial':
            print("📚 Tutorial Mode: Learn gesture controls step by step!")
        elif new_mode == 'backseat':
            print("🤖 Backseat Gamer Mode: AI coach with live commentary!")
        else:
            print("🎮 Normal Mode: Standard gesture control gameplay!")
    
    def _cleanup(self, cap):
        """Cleanup resources"""
        try:
            print("🧹 Cleaning up resources...")
            
            # Stop backseat mode if active
            if backseat_mode.is_active_mode():
                backseat_mode.stop_backseat_mode()
            
            # Release control system resources
            self.control_system.shooting_controller.force_release()
            self.control_system.wasd_controller.release_all_keys()
            
            # Release camera
            cap.release()
            cv2.destroyAllWindows()
            
            # Close MediaPipe
            self.control_system.hands.close()
            self.control_system.pose.close()
            self.control_system.face_mesh.close()
            
            print("✅ Cleanup completed")
            print("\n🎉 CS:GO Gesture Control Application finished!")
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")

if __name__ == "__main__":
    app = MainApplication()
    app.run()
