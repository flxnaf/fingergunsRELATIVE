"""
DUAL HAND TRACKING: Two Hand Controls for CS:GO
Goal: Track both hands for enhanced control
- Right hand: Aiming and shooting (gun gesture + thumb)
- Left hand: Additional controls (weapon switching, grenades, etc.)

Controls: 
- Press 'c' to toggle control ON/OFF
- Press 'q' to quit
- Press '+'/'-' to adjust sensitivity
"""

import cv2
import mediapipe as mp
import numpy as np
import time
import pyautogui

# Safety
pyautogui.PAUSE = 0.01
pyautogui.FAILSAFE = True

def calculate_angle(point1, point2, point3):
    vector1 = np.array([point1[0] - point2[0], point1[1] - point2[1]])
    vector2 = np.array([point3[0] - point2[0], point3[1] - point2[1]])
    cosine = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2) + 1e-6)
    angle = np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))
    return angle

def is_finger_extended(landmarks, finger_tip_id, finger_pip_id, finger_mcp_id):
    tip = [landmarks[finger_tip_id].x, landmarks[finger_tip_id].y]
    pip = [landmarks[finger_pip_id].x, landmarks[finger_pip_id].y]
    mcp = [landmarks[finger_mcp_id].x, landmarks[finger_mcp_id].y]
    angle = calculate_angle(tip, pip, mcp)
    return angle > 130

def is_gun_gesture(hand_landmarks):
    """Detect gun gesture (index out, bottom 3 curled)"""
    landmarks = hand_landmarks.landmark
    index_extended = is_finger_extended(landmarks, 8, 6, 5)
    middle_curled = not is_finger_extended(landmarks, 12, 10, 9)
    ring_curled = not is_finger_extended(landmarks, 16, 14, 13)
    pinky_curled = not is_finger_extended(landmarks, 20, 18, 17)
    is_gun = index_extended and middle_curled and ring_curled and pinky_curled
    return is_gun

def is_thumb_down(hand_landmarks):
    """Detect if thumb is pressed down (shooting position)"""
    landmarks = hand_landmarks.landmark
    thumb_tip = landmarks[4]
    index_mcp = landmarks[5]
    wrist = landmarks[0]
    
    # Method 1: Y-position - thumb below index base = pressed down
    thumb_below = thumb_tip.y > index_mcp.y
    
    # Method 2: Distance from wrist - thumb close to wrist = pressed down
    thumb_to_wrist = ((thumb_tip.x - wrist.x)**2 + (thumb_tip.y - wrist.y)**2)**0.5
    index_to_wrist = ((index_mcp.x - wrist.x)**2 + (index_mcp.y - wrist.y)**2)**0.5
    thumb_close = thumb_to_wrist < index_to_wrist * 0.8
    
    return thumb_below or thumb_close

def are_bottom_fingers_curled(hand_landmarks):
    """Check if bottom 3 fingers are curled (rotation-proof) - from finger_tracking.py"""
    landmarks = hand_landmarks.landmark
    wrist = landmarks[0]
    
    middle_tip = landmarks[12]
    middle_mcp = landmarks[9]
    middle_dist = ((middle_tip.x - wrist.x)**2 + (middle_tip.y - wrist.y)**2)**0.5
    middle_mcp_dist = ((middle_mcp.x - wrist.x)**2 + (middle_mcp.y - wrist.y)**2)**0.5
    middle_curled = middle_dist < middle_mcp_dist * 1.8
    
    ring_tip = landmarks[16]
    ring_mcp = landmarks[13]
    ring_dist = ((ring_tip.x - wrist.x)**2 + (ring_tip.y - wrist.y)**2)**0.5
    ring_mcp_dist = ((ring_mcp.x - wrist.x)**2 + (ring_mcp.y - wrist.y)**2)**0.5
    ring_curled = ring_dist < ring_mcp_dist * 1.8
    
    pinky_tip = landmarks[20]
    pinky_mcp = landmarks[17]
    pinky_dist = ((pinky_tip.x - wrist.x)**2 + (pinky_tip.y - wrist.y)**2)**0.5
    pinky_mcp_dist = ((pinky_mcp.x - wrist.x)**2 + (pinky_mcp.y - wrist.y)**2)**0.5
    pinky_curled = pinky_dist < pinky_mcp_dist * 1.8
    
    curled_count = sum([middle_curled, ring_curled, pinky_curled])
    return curled_count >= 2

def detect_left_hand_gestures(hand_landmarks):
    """
    Detect left hand gestures for CS:GO controls - palm facing camera
    Returns: gesture_name, action_key
    """
    try:
        if not hasattr(hand_landmarks, 'landmark') or len(hand_landmarks.landmark) < 21:
            return "invalid", None
            
        landmarks = hand_landmarks.landmark
        
        # Check individual finger states - for palm-facing camera, we check if fingers are DOWN
        thumb_down = not is_finger_extended(landmarks, 4, 3, 2)  # Inverted logic
        index_down = not is_finger_extended(landmarks, 8, 6, 5)  # Inverted logic
        middle_down = not is_finger_extended(landmarks, 12, 10, 9)  # Inverted logic
        ring_down = not is_finger_extended(landmarks, 16, 14, 13)  # Inverted logic
        pinky_down = not is_finger_extended(landmarks, 20, 18, 17)  # Inverted logic
        
        # Gesture detection based on fingers DOWN
        fingers_down = [thumb_down, index_down, middle_down, ring_down, pinky_down]
        num_fingers_down = sum(fingers_down)
        
        
        if num_fingers_down == 1:  # One finger down
            return "one_down", "ctrl"  # Crouch
        elif num_fingers_down == 4:  # Four fingers down (thumb up)
            return "four_down", "space"  # Jump
        else:
            return "unknown", None
            
    except Exception as e:
        print(f"Error in detect_left_hand_gestures: {e}")
        return "error", None

class StickyGunDetector:
    def __init__(self, grace_period=30):
        self.is_locked = False
        self.lock_frames = 0
        self.grace_period = grace_period
        self.frames_without_hand = 0
        
    def update(self, hand_landmarks):
        if hand_landmarks is None:
            if self.is_locked:
                self.frames_without_hand += 1
                if self.frames_without_hand > self.grace_period:
                    self.is_locked = False
                    self.lock_frames = 0
                    self.frames_without_hand = 0
                    return False
                else:
                    return True
            else:
                self.frames_without_hand = 0
                return False
        
        self.frames_without_hand = 0
        gun_detected = is_gun_gesture(hand_landmarks)
        bottom_fingers_curled = are_bottom_fingers_curled(hand_landmarks)
        
        if not self.is_locked:
            if gun_detected:
                self.is_locked = True
                self.lock_frames = 0
                return True
            else:
                return False
        else:
            self.lock_frames += 1
            if not bottom_fingers_curled:
                self.is_locked = False
                self.lock_frames = 0
                return False
            else:
                return True

class ThumbShootingController:
    def __init__(self):
        self.is_shooting = False
        
    def update(self, thumb_is_down, control_enabled):
        if not control_enabled:
            if self.is_shooting:
                pyautogui.mouseUp()
                self.is_shooting = False
            return False, "Control Disabled"
        
        if thumb_is_down and not self.is_shooting:
            pyautogui.mouseDown()
            self.is_shooting = True
            return True, "Started Shooting!"
        elif not thumb_is_down and self.is_shooting:
            pyautogui.mouseUp()
            self.is_shooting = False
            return False, "Stopped Shooting"
        elif self.is_shooting:
            return True, "Shooting..."
        else:
            return False, "Ready"
    
    def force_release(self):
        if self.is_shooting:
            pyautogui.mouseUp()
            self.is_shooting = False

class SmoothMouseController:
    def __init__(self, smoothing_factor=0.5):
        self.smoothing_factor = smoothing_factor
        self.prev_x = None
        self.prev_y = None
        self.screen_width, self.screen_height = pyautogui.size()
        
    def update(self, finger_x, finger_y):
        screen_x = int(finger_x * self.screen_width)
        screen_y = int(finger_y * self.screen_height)
        
        if self.prev_x is not None:
            screen_x = int(self.smoothing_factor * self.prev_x + (1 - self.smoothing_factor) * screen_x)
            screen_y = int(self.smoothing_factor * self.prev_y + (1 - self.smoothing_factor) * screen_y)
        
        self.prev_x = screen_x
        self.prev_y = screen_y
        
        return screen_x, screen_y
    
    def move_mouse(self, screen_x, screen_y):
        pyautogui.moveTo(screen_x, screen_y)

class LeftHandGestureController:
    def __init__(self):
        self.last_gesture = None
        self.last_gesture_time = 0
        self.gesture_debounce = 0.1  # 0.1 second between gestures (much faster)
        
    def update(self, hand_landmarks, control_enabled):
        try:
            if not control_enabled or hand_landmarks is None:
                return None, "Control Disabled"
            
            current_time = time.time()
            gesture_name, action_key = detect_left_hand_gestures(hand_landmarks)
            
            if gesture_name == "error" or gesture_name == "invalid":
                return None, "Gesture detection error"
            
            if action_key and gesture_name != self.last_gesture:
                if current_time - self.last_gesture_time > self.gesture_debounce:
                    pyautogui.press(action_key)
                    self.last_gesture = gesture_name
                    self.last_gesture_time = current_time
                    return action_key, f"Pressed '{action_key}' - {gesture_name}"
                else:
                    return None, f"Gesture detected (debounced): {gesture_name}"
            elif gesture_name == self.last_gesture:
                return None, f"Holding: {gesture_name}"
            else:
                return None, "Left hand ready"
                
        except Exception as e:
            print(f"Error in LeftHandGestureController.update: {e}")
            return None, "Error processing gesture"

class DualHandTrackingController:
    def __init__(self):
        # Initialize MediaPipe Hands for dual hand tracking
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,  # Enable dual hand tracking
            min_detection_confidence=0.5,
            min_tracking_confidence=0.3
        )
        
        # Initialize camera with higher resolution settings
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Test camera
        if not self.cap.isOpened():
            print("Error: Could not open camera")
            return
        else:
            print("Camera initialized successfully")
        
        # Initialize controllers
        self.right_gun_detector = StickyGunDetector(grace_period=30)
        self.shooting_controller = ThumbShootingController()
        self.mouse_controller = SmoothMouseController(smoothing_factor=0.5)
        self.left_hand_controller = LeftHandGestureController()
        
        # Control state
        self.control_enabled = False
        
        print("Dual hand tracking controller initialized!")
        print("Right hand: Gun gesture + thumb shooting")
        print("Left hand: Palm-facing controls (crouch/jump)")
    
    def identify_hands(self, hand_landmarks_list):
        """
        Identify which hand is left vs right based on position
        Returns: (left_hand, right_hand)
        """
        try:
            if len(hand_landmarks_list) < 2:
                # Only one hand detected
                if len(hand_landmarks_list) == 1:
                    hand = hand_landmarks_list[0]
                    # Assume it's right hand for gun control if no left hand
                    return None, hand
                else:
                    return None, None
            
            # Two hands detected - identify by position
            hand1 = hand_landmarks_list[0]
            hand2 = hand_landmarks_list[1]
            
            # Get wrist positions safely
            if not hasattr(hand1, 'landmark') or not hasattr(hand2, 'landmark'):
                print("Warning: Hand landmarks not properly formatted")
                return None, hand1  # Default to first hand as right
            
            if len(hand1.landmark) < 1 or len(hand2.landmark) < 1:
                print("Warning: Insufficient hand landmarks")
                return None, hand1  # Default to first hand as right
            
            wrist1_x = hand1.landmark[0].x
            wrist2_x = hand2.landmark[0].x
            
            # Left hand is on the left side of screen (smaller x value)
            if wrist1_x < wrist2_x:
                return hand1, hand2
            else:
                return hand2, hand1
                
        except Exception as e:
            print(f"Error in identify_hands: {e}")
            # Return safe defaults
            if len(hand_landmarks_list) >= 1:
                return None, hand_landmarks_list[0]
            else:
                return None, None
    
    def run(self):
        """Main dual hand tracking loop"""
        print("=" * 70)
        print("DUAL HAND TRACKING: Enhanced CS:GO Controls")
        print("=" * 70)
        print("Controls:")
        print("  't' - Toggle control ON/OFF")
        print("  'q' - Quit")
        print("\nRight Hand (Gun Control):")
        print("  - Gun gesture (index out, bottom 3 curled)")
        print("  - Thumb UP = ready to shoot")
        print("  - Thumb DOWN = START FIRING")
        print("  - Index finger controls cursor")
        print("\nLeft Hand (Palm-Facing Controls):")
        print("  - One finger down = Press 'CTRL' (Crouch)")
        print("  - Four fingers down = Press 'SPACE' (Jump)")
        print("  - Other positions = No action")
        print("\nPerfect for advanced CS:GO control!")
        print("=" * 70)
        
        frame_count = 0
        last_frame_time = time.time()
        
        while self.cap.isOpened():
            try:
                frame_count += 1
                current_time = time.time()
                
                # Print status every 30 frames (about 1 second at 30fps)
                if frame_count % 30 == 0:
                    fps = frame_count / (current_time - last_frame_time) if current_time > last_frame_time else 0
                    print(f"Frame {frame_count}: Running... FPS: {fps:.1f}")
                
                success, frame = self.cap.read()
                if not success:
                    print("Failed to read frame from camera - retrying...")
                    time.sleep(0.1)  # Small delay before retry
                    continue  # Skip this frame and try again
                
                frame = cv2.flip(frame, 1)
                h, w, _ = frame.shape
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process hands with error handling
                try:
                    results = self.hands.process(rgb_frame)
                except Exception as e:
                    print(f"Error in MediaPipe processing: {e}")
                    results = None
                
                # Initialize hand states
                left_hand = None
                right_hand = None
                gun_active = False
                is_shooting = False
                shoot_status = "Ready"
                left_action = None
                left_status = "No left hand"
                
                if results and results.multi_hand_landmarks:
                    try:
                        # Identify left and right hands
                        left_hand, right_hand = self.identify_hands(results.multi_hand_landmarks)
                        
                        # Process right hand (gun control)
                        if right_hand:
                            try:
                                gun_active = self.right_gun_detector.update(right_hand)
                                
                                if gun_active:
                                    # Get index finger for aiming
                                    if len(right_hand.landmark) > 8:
                                        index_tip = right_hand.landmark[8]
                                        
                                        # Move mouse cursor
                                        if self.control_enabled:
                                            screen_x, screen_y = self.mouse_controller.update(index_tip.x, index_tip.y)
                                            self.mouse_controller.move_mouse(screen_x, screen_y)
                                    
                                    # Check thumb position for shooting
                                    thumb_down = is_thumb_down(right_hand)
                                    is_shooting, shoot_status = self.shooting_controller.update(thumb_down, self.control_enabled)
                                    
                                    # Visual indicators for thumb
                                    if len(right_hand.landmark) > 4:
                                        thumb_tip = right_hand.landmark[4]
                                        tx = int(thumb_tip.x * w)
                                        ty = int(thumb_tip.y * h)
                                        thumb_color = (0, 0, 255) if thumb_down else (0, 255, 255)
                                        cv2.circle(frame, (tx, ty), 12, thumb_color, -1)
                                        cv2.putText(frame, "RIGHT THUMB", (tx + 15, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.6, thumb_color, 2)
                                else:
                                    # Gun not active - release mouse if held
                                    self.shooting_controller.force_release()
                            except Exception as e:
                                print(f"Error processing right hand: {e}")
                        
                        # Process left hand (gesture controls)
                        if left_hand:
                            try:
                                left_action, left_status = self.left_hand_controller.update(left_hand, self.control_enabled)
                                
                                # Visual indicators for left hand
                                if len(left_hand.landmark) > 0:
                                    wrist = left_hand.landmark[0]
                                    wx = int(wrist.x * w)
                                    wy = int(wrist.y * h)
                                    cv2.circle(frame, (wx, wy), 15, (255, 0, 0), -1)
                                    cv2.putText(frame, "LEFT HAND", (wx + 20, wy), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                            except Exception as e:
                                print(f"Error processing left hand: {e}")
                                left_action = None
                                left_status = "Error processing left hand"
                                
                    except Exception as e:
                        print(f"Error in hand processing: {e}")
                        left_hand = None
                        right_hand = None
                
                # Draw hand landmarks
                try:
                    if results and results.multi_hand_landmarks:
                        for hand_landmarks in results.multi_hand_landmarks:
                            self.mp_drawing.draw_landmarks(
                                frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                                self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                                self.mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2)
                            )
                except Exception as e:
                    print(f"Error drawing landmarks: {e}")
                
                # Display status
                try:
                    self.display_dual_hand_status(frame, gun_active, is_shooting, shoot_status, left_action, left_status, w, h)
                except Exception as e:
                    print(f"Error displaying status: {e}")
            
                # Show frame
                try:
                    cv2.imshow('Dual Hand Tracking: Enhanced CS:GO Controls', frame)
                except Exception as e:
                    print(f"Error showing frame: {e}")
                    break
                
                # Handle keyboard input
                try:
                    key = cv2.waitKey(1) & 0xFF  # Increased wait time from 5 to 1ms
                    if key == ord('q'):
                        print("Quit key pressed - exiting...")
                        self.shooting_controller.force_release()
                        break
                    elif key == ord('t'):
                        self.control_enabled = not self.control_enabled
                        if not self.control_enabled:
                            self.shooting_controller.force_release()
                        print(f"\n{'='*50}")
                        print(f"Control {'ENABLED ✓' if self.control_enabled else 'DISABLED ✗'}")
                        print(f"{'='*50}\n")
                    elif key == 27:  # ESC key
                        print("ESC key pressed - exiting...")
                        self.shooting_controller.force_release()
                        break
                except Exception as e:
                    print(f"Error handling keyboard input: {e}")
                    
            except Exception as e:
                print(f"Error in main loop: {e}")
                continue  # Continue to next frame instead of breaking
        
        # Cleanup
        print("Cleaning up resources...")
        try:
            self.cap.release()
            print("Camera released")
        except:
            pass
        
        try:
            cv2.destroyAllWindows()
            print("Windows closed")
        except:
            pass
            
        try:
            self.hands.close()
            print("MediaPipe hands closed")
        except:
            pass
            
        try:
            self.shooting_controller.force_release()
            print("Shooting controller released")
        except:
            pass
            
        print("\n🎉 Dual hand tracking complete! Ready for advanced CS:GO!")
    
    def display_dual_hand_status(self, frame, gun_active, is_shooting, shoot_status, left_action, left_status, w, h):
        """Display dual hand status information"""
        # Control status
        control_status = "CONTROL: ON ✓" if self.control_enabled else "CONTROL: OFF (press 't')"
        control_color = (0, 255, 0) if self.control_enabled else (0, 0, 255)
        cv2.putText(frame, control_status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, control_color, 2)
        
        # Right hand status
        if gun_active:
            right_status = "🔒 RIGHT HAND: GUN LOCKED"
            right_color = (0, 255, 0)
        else:
            right_status = "Right hand: Make gun gesture"
            right_color = (0, 0, 255)
        
        cv2.putText(frame, right_status, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, right_color, 2)
        
        # Shooting status
        if is_shooting:
            shoot_color = (0, 0, 255)
            shoot_text = "🔥 FIRING! 🔥"
            # Red flash background
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 255), -1)
            frame = cv2.addWeighted(frame, 0.7, overlay, 0.3, 0)
        else:
            shoot_color = (255, 255, 255)
            shoot_text = shoot_status
        
        cv2.putText(frame, shoot_text, (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, shoot_color, 2)
        
        # Left hand status
        left_color = (0, 255, 255) if left_action else (255, 255, 255)
        cv2.putText(frame, f"LEFT HAND: {left_status}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, left_color, 2)
        
        # Instructions
        cv2.putText(frame, "Press 't' to toggle | 'q' to quit", (10, h - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

if __name__ == "__main__":
    controller = DualHandTrackingController()
    controller.run()
