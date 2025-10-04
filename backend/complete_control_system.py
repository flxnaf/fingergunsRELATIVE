"""
COMPLETE CS:GO CONTROL SYSTEM
Combines:
- Head tracking for WASD movement
- Right hand for gun control and shooting
- Left hand for crouch/jump
- Tongue tracking for spray emote

Controls:
- 't' to toggle control ON/OFF
- 'q' or ESC to quit
"""

import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time

# Safety
pyautogui.PAUSE = 0.01

# MediaPipe initialization
mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

def calculate_head_pose(face_landmarks, frame_width, frame_height):
    """Calculate head pose (yaw and pitch)"""
    nose_tip = face_landmarks.landmark[1]
    left_eye = face_landmarks.landmark[33]
    right_eye = face_landmarks.landmark[263]
    chin = face_landmarks.landmark[152]
    forehead = face_landmarks.landmark[10]
    
    # Yaw (left/right)
    eye_center_x = (left_eye.x + right_eye.x) / 2
    nose_x = nose_tip.x
    yaw = (nose_x - eye_center_x) * 100
    
    # Pitch (up/down)
    nose_y = nose_tip.y
    chin_y = chin.y
    forehead_y = forehead.y
    face_height = chin_y - forehead_y
    nose_position = (nose_y - forehead_y) / face_height if face_height > 0 else 0.5
    pitch = (nose_position - 0.5) * 100
    
    return yaw, pitch

def is_finger_extended(landmarks, tip, pip, mcp):
    """Check if a finger is extended"""
    if tip >= len(landmarks) or pip >= len(landmarks) or mcp >= len(landmarks):
        return False
    return landmarks[tip].y < landmarks[pip].y < landmarks[mcp].y

def calculate_angle(p1, p2, p3):
    """Calculate angle between three points"""
    a = np.array([p1.x, p1.y])
    b = np.array([p2.x, p2.y])
    c = np.array([p3.x, p3.y])
    
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
    
    return angle

def is_gun_gesture(landmarks):
    """Check if hand is in gun gesture (index extended, others curled)"""
    try:
        # Index finger extended
        index_extended = is_finger_extended(landmarks, 8, 6, 5)
        
        # Other fingers curled
        middle_curled = not is_finger_extended(landmarks, 12, 10, 9)
        ring_curled = not is_finger_extended(landmarks, 16, 14, 13)
        pinky_curled = not is_finger_extended(landmarks, 20, 18, 17)
        
        return index_extended and middle_curled and ring_curled and pinky_curled
    except:
        return False

def is_thumb_down(landmarks):
    """Check if thumb is pointing down"""
    try:
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        thumb_mcp = landmarks[2]
        
        # Thumb pointing down if tip is below IP joint
        return thumb_tip.y > thumb_ip.y
    except:
        return False

def are_bottom_fingers_curled(landmarks):
    """Check if bottom 3 fingers (middle, ring, pinky) are curled"""
    try:
        # Calculate distances
        middle_tip = landmarks[12]
        middle_pip = landmarks[10]
        middle_mcp = landmarks[9]
        
        ring_tip = landmarks[16]
        ring_pip = landmarks[14]
        ring_mcp = landmarks[13]
        
        pinky_tip = landmarks[20]
        pinky_pip = landmarks[18]
        pinky_mcp = landmarks[17]
        
        # Calculate distances
        middle_dist = np.sqrt((middle_tip.x - middle_pip.x)**2 + (middle_tip.y - middle_pip.y)**2)
        middle_mcp_dist = np.sqrt((middle_pip.x - middle_mcp.x)**2 + (middle_pip.y - middle_mcp.y)**2)
        
        ring_dist = np.sqrt((ring_tip.x - ring_pip.x)**2 + (ring_tip.y - ring_pip.y)**2)
        ring_mcp_dist = np.sqrt((ring_pip.x - ring_mcp.x)**2 + (ring_pip.y - ring_mcp.y)**2)
        
        pinky_dist = np.sqrt((pinky_tip.x - pinky_pip.x)**2 + (pinky_tip.y - pinky_pip.y)**2)
        pinky_mcp_dist = np.sqrt((pinky_pip.x - pinky_mcp.x)**2 + (pinky_pip.y - pinky_mcp.y)**2)
        
        # Check if fingers are curled (distance ratio)
        middle_curled = middle_dist < middle_mcp_dist * 1.8
        ring_curled = ring_dist < ring_mcp_dist * 1.8
        pinky_curled = pinky_dist < pinky_mcp_dist * 1.8
        
        curled_count = sum([middle_curled, ring_curled, pinky_curled])
        return curled_count >= 2
    except:
        return False

def detect_left_hand_gestures(hand_landmarks):
    """Detect left hand gestures for crouch/jump"""
    try:
        if not hasattr(hand_landmarks, 'landmark') or len(hand_landmarks.landmark) < 21:
            return "invalid", None
            
        landmarks = hand_landmarks.landmark
        
        # Check individual finger states - for palm-facing camera, we check if fingers are DOWN
        thumb_down = not is_finger_extended(landmarks, 4, 3, 2)
        index_down = not is_finger_extended(landmarks, 8, 6, 5)
        middle_down = not is_finger_extended(landmarks, 12, 10, 9)
        ring_down = not is_finger_extended(landmarks, 16, 14, 13)
        pinky_down = not is_finger_extended(landmarks, 20, 18, 17)
        
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

def detect_tongue_out(face_landmarks):
    """Detect if tongue is out (mouth open)"""
    try:
        landmarks = face_landmarks.landmark
        
        # Use specific lip landmarks for mouth opening detection
        upper_lip_bottom = landmarks[13]  # Upper lip bottom
        lower_lip_top = landmarks[14]     # Lower lip top
        
        # Calculate vertical separation between lips
        lip_separation = abs(upper_lip_bottom.y - lower_lip_top.y)
        
        # Threshold for mouth opening (adjustable)
        threshold = 0.015
        
        return lip_separation > threshold
    except:
        return False

class WASDController:
    """Head tracking controller for WASD movement"""
    def __init__(self, yaw_threshold=5, pitch_threshold=8, pitch_threshold_back=12, hysteresis=0.7):
        self.yaw_threshold = yaw_threshold
        self.pitch_threshold = pitch_threshold
        self.pitch_threshold_back = pitch_threshold_back
        self.hysteresis = hysteresis
        self.current_keys = set()
        
    def update(self, yaw, pitch, control_enabled):
        if not control_enabled:
            self.release_all_keys()
            return set(), {'w': False, 'a': False, 's': False, 'd': False}
        
        desired_keys = set()
        
        # Calculate release thresholds
        yaw_release = self.yaw_threshold * self.hysteresis
        pitch_release = self.pitch_threshold * self.hysteresis
        pitch_release_back = self.pitch_threshold_back * self.hysteresis
        
        # Determine which keys should be pressed
        if 'a' in self.current_keys:
            if yaw > -yaw_release:
                pass
            else:
                desired_keys.add('a')
        elif yaw < -self.yaw_threshold:
            desired_keys.add('a')
            
        if 'd' in self.current_keys:
            if yaw < yaw_release:
                pass
            else:
                desired_keys.add('d')
        elif yaw > self.yaw_threshold:
            desired_keys.add('d')
            
        if 'w' in self.current_keys:
            if pitch > -pitch_release:
                pass
            else:
                desired_keys.add('w')
        elif pitch < -self.pitch_threshold:
            desired_keys.add('w')
            
        if 's' in self.current_keys:
            if pitch < pitch_release_back:
                pass
            else:
                desired_keys.add('s')
        elif pitch > self.pitch_threshold_back:
            desired_keys.add('s')
        
        # Update key states
        keys_to_release = self.current_keys - desired_keys
        for key in keys_to_release:
            pyautogui.keyUp(key)
        
        keys_to_press = desired_keys - self.current_keys
        for key in keys_to_press:
            pyautogui.keyDown(key)
        
        self.current_keys = desired_keys
        
        key_states = {
            'w': 'w' in desired_keys,
            'a': 'a' in desired_keys,
            's': 's' in desired_keys,
            'd': 'd' in desired_keys
        }
        
        return desired_keys, key_states
    
    def release_all_keys(self):
        for key in self.current_keys:
            pyautogui.keyUp(key)
        self.current_keys = set()

class StickyGunDetector:
    """Gun gesture detector with sticky behavior"""
    def __init__(self, grace_period=30):
        self.is_locked = False
        self.lock_frames = 0
        self.grace_period = grace_period
        self.frames_without_hand = 0
        
    def update(self, hand_landmarks):
        if hand_landmarks is None:
            self.frames_without_hand += 1
            if self.frames_without_hand > self.grace_period:
                self.is_locked = False
                self.lock_frames = 0
            return False
        
        self.frames_without_hand = 0
        
        # Check if we should lock the gun
        if is_gun_gesture(hand_landmarks.landmark):
            if not self.is_locked:
                self.is_locked = True
                self.lock_frames = 0
                print("🔫 Gun LOCKED!")
            return True
        
        # If locked, check if we should maintain the lock
        if self.is_locked:
            if are_bottom_fingers_curled(hand_landmarks.landmark):
                self.lock_frames += 1
                return True
            else:
                self.is_locked = False
                self.lock_frames = 0
                print("🔫 Gun UNLOCKED!")
        
        return False

class ThumbShootingController:
    """Mouse click controller based on thumb position"""
    def __init__(self):
        self.is_pressed = False
        self.last_thumb_down = False
        
    def update(self, hand_landmarks, gun_active):
        if not gun_active or hand_landmarks is None:
            self.force_release()
            return False, "Gun not active"
        
        thumb_down = is_thumb_down(hand_landmarks.landmark)
        
        # Detect thumb press (transition from up to down)
        if thumb_down and not self.last_thumb_down:
            if not self.is_pressed:
                pyautogui.mouseDown()
                self.is_pressed = True
                return True, "FIRING!"
        
        # Detect thumb release (transition from down to up)
        elif not thumb_down and self.last_thumb_down:
            if self.is_pressed:
                pyautogui.mouseUp()
                self.is_pressed = False
                return False, "Ready"
        
        self.last_thumb_down = thumb_down
        
        if self.is_pressed:
            return True, "FIRING!"
        else:
            return False, "Ready"
    
    def force_release(self):
        if self.is_pressed:
            pyautogui.mouseUp()
            self.is_pressed = False

class SmoothMouseController:
    """Smooth mouse movement controller"""
    def __init__(self, smoothing=0.7, sensitivity=3.0):
        self.smoothing = smoothing
        self.sensitivity = sensitivity
        self.last_x = None
        self.last_y = None
        
    def update(self, hand_landmarks, gun_active):
        if not gun_active or hand_landmarks is None:
            return
            
        try:
            # Get index finger tip position
            index_tip = hand_landmarks.landmark[8]
            
            # Convert to screen coordinates (assuming 1920x1080 screen)
            screen_x = int(index_tip.x * 1920)
            screen_y = int(index_tip.y * 1080)
            
            # Apply smoothing
            if self.last_x is not None and self.last_y is not None:
                screen_x = int(self.last_x * self.smoothing + screen_x * (1 - self.smoothing))
                screen_y = int(self.last_y * self.smoothing + screen_y * (1 - self.smoothing))
            
            # Move mouse
            pyautogui.moveTo(screen_x, screen_y)
            
            self.last_x = screen_x
            self.last_y = screen_y
            
        except Exception as e:
            print(f"Mouse control error: {e}")

class LeftHandGestureController:
    """Left hand gesture controller for crouch/jump"""
    def __init__(self):
        self.last_gesture = None
        self.last_gesture_time = 0
        self.gesture_debounce = 0.1
        
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
            print(f"Error in LeftHandGestureController: {e}")
            return None, "Error"

class TongueController:
    """Tongue detection controller for spray emote"""
    def __init__(self, debounce_frames=10):
        self.debounce_frames = debounce_frames
        self.frames_held = 0
        self.last_tongue_out = False
        
    def update(self, face_landmarks, control_enabled):
        if not control_enabled or face_landmarks is None:
            self.frames_held = 0
            self.last_tongue_out = False
            return False, "Control Disabled"
        
        tongue_out = detect_tongue_out(face_landmarks)
        
        if tongue_out:
            self.frames_held += 1
            if self.frames_held >= self.debounce_frames and not self.last_tongue_out:
                pyautogui.press('t')
                self.last_tongue_out = True
                return True, "Tongue out - T pressed!"
        else:
            self.frames_held = 0
            self.last_tongue_out = False
        
        return tongue_out, "Tongue ready"

class CompleteControlSystem:
    """Complete CS:GO control system integrating all tracking methods"""
    def __init__(self):
        # Initialize MediaPipe
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        self.face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Initialize controllers
        self.wasd_controller = WASDController()
        self.gun_detector = StickyGunDetector()
        self.shooting_controller = ThumbShootingController()
        self.mouse_controller = SmoothMouseController()
        self.left_hand_controller = LeftHandGestureController()
        self.tongue_controller = TongueController()
        
        # Control state
        self.control_enabled = False
        
        print("Complete CS:GO Control System initialized!")
        print("Head: WASD movement")
        print("Right hand: Gun control + shooting")
        print("Left hand: Crouch/jump")
        print("Tongue: Spray emote")
    
    def identify_hands(self, hand_landmarks_list):
        """Identify which hand is left vs right based on position"""
        if len(hand_landmarks_list) == 0:
            return None, None
        elif len(hand_landmarks_list) == 1:
            # Only one hand detected, assume it's the right hand
            return None, hand_landmarks_list[0]
        else:
            # Two hands detected, identify by x position
            hand1 = hand_landmarks_list[0]
            hand2 = hand_landmarks_list[1]
            
            # Get wrist positions
            wrist1_x = hand1.landmark[0].x
            wrist2_x = hand2.landmark[0].x
            
            # Left hand is on the left side of screen (lower x value)
            if wrist1_x < wrist2_x:
                return hand1, hand2  # hand1 is left, hand2 is right
            else:
                return hand2, hand1  # hand2 is left, hand1 is right
    
    def run(self):
        """Main control loop"""
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        if not cap.isOpened():
            print("Error: Could not open camera")
            return
        
        print("Camera initialized successfully")
        print("Complete CS:GO Control System")
        print("=" * 50)
        print("Controls:")
        print("  't' - Toggle control ON/OFF")
        print("  'q' - Quit")
        print("\nHead Movement (WASD):")
        print("  - Tilt LEFT → Press 'A' (move left)")
        print("  - Tilt RIGHT → Press 'D' (move right)")
        print("  - Tilt UP → Press 'W' (move forward)")
        print("  - Tilt DOWN → Press 'S' (move backward)")
        print("\nRight Hand (Gun Control):")
        print("  - Gun gesture (index out, bottom 3 curled)")
        print("  - Thumb UP = ready to shoot")
        print("  - Thumb DOWN = START FIRING")
        print("  - Index finger controls cursor")
        print("\nLeft Hand (Palm-Facing Controls):")
        print("  - One finger down = Press 'CTRL' (Crouch)")
        print("  - Four fingers down = Press 'SPACE' (Jump)")
        print("  - Other positions = No action")
        print("\nTongue:")
        print("  - Stick out tongue = Press 'T' (Spray emote)")
        print("\nPerfect for complete CS:GO control!")
        print("=" * 50)
        
        frame_count = 0
        last_frame_time = time.time()
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    time.sleep(0.1)
                    continue
                
                frame_count += 1
                current_time = time.time()
                if current_time - last_frame_time >= 1.0:
                    fps = frame_count / (current_time - last_frame_time)
                    print(f"Frame {frame_count}: Running... FPS: {fps:.1f}")
                    frame_count = 0
                    last_frame_time = current_time
                
                frame = cv2.flip(frame, 1)
                h, w, _ = frame.shape
                
                # Process hands
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                hand_results = self.hands.process(rgb_frame)
                
                # Process face
                face_results = self.face_mesh.process(rgb_frame)
                
                # Initialize status variables
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
                
                # Process face for head tracking and tongue detection
                if face_results and face_results.multi_face_landmarks:
                    try:
                        face_landmarks = face_results.multi_face_landmarks[0]
                        
                        # Head tracking for WASD
                        head_yaw, head_pitch = calculate_head_pose(face_landmarks, w, h)
                        active_wasd_keys, wasd_states = self.wasd_controller.update(
                            head_yaw, head_pitch, self.control_enabled
                        )
                        
                        # Tongue detection for spray emote
                        tongue_out, tongue_status = self.tongue_controller.update(
                            face_landmarks, self.control_enabled
                        )
                        
                    except Exception as e:
                        print(f"Error processing face: {e}")
                
                # Process hands
                if hand_results and hand_results.multi_hand_landmarks:
                    try:
                        # Identify left and right hands
                        left_hand, right_hand = self.identify_hands(hand_results.multi_hand_landmarks)
                        
                        # Process right hand (gun control)
                        if right_hand:
                            try:
                                gun_active = self.gun_detector.update(right_hand)
                                
                                if gun_active:
                                    # Thumb shooting
                                    is_shooting, shoot_status = self.shooting_controller.update(
                                        right_hand, gun_active
                                    )
                                    
                                    # Mouse movement
                                    self.mouse_controller.update(right_hand, gun_active)
                                else:
                                    # Gun not active - release mouse if held
                                    self.shooting_controller.force_release()
                                    
                            except Exception as e:
                                print(f"Error processing right hand: {e}")
                        
                        # Process left hand (gesture controls)
                        if left_hand:
                            try:
                                left_action, left_status = self.left_hand_controller.update(
                                    left_hand, self.control_enabled
                                )
                                
                            except Exception as e:
                                print(f"Error processing left hand: {e}")
                        
                    except Exception as e:
                        print(f"Error processing hands: {e}")
                
                # Display status overlay
                self.display_status(frame, wasd_states, gun_active, shoot_status, 
                                  left_status, tongue_status, head_yaw, head_pitch, tongue_out)
                
                # Show frame
                cv2.imshow('Complete CS:GO Control System', frame)
                
                # Handle keyboard input
                try:
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q') or key == 27:  # 'q' or ESC to quit
                        print("Quit key pressed - exiting...")
                        break
                    elif key == ord('t'):
                        self.control_enabled = not self.control_enabled
                        if not self.control_enabled:
                            self.shooting_controller.force_release()
                            self.wasd_controller.release_all_keys()
                        print(f"\n{'='*50}")
                        print(f"Control {'ENABLED ✓' if self.control_enabled else 'DISABLED ✗'}")
                        print(f"{'='*50}\n")
                except Exception as e:
                    print(f"Error handling keyboard input: {e}")
                    
        except KeyboardInterrupt:
            print("Interrupted by user")
        except Exception as e:
            print(f"Error in main loop: {e}")
        finally:
            # Cleanup
            try:
                print("Cleaning up resources...")
                self.shooting_controller.force_release()
                self.wasd_controller.release_all_keys()
                cap.release()
                cv2.destroyAllWindows()
                self.hands.close()
                self.face_mesh.close()
                print("Camera released")
                print("Windows closed")
                print("MediaPipe closed")
                print("\n🎉 Complete control system finished!")
            except Exception as e:
                print(f"Error during cleanup: {e}")
    
    def display_status(self, frame, wasd_states, gun_active, shoot_status, 
                      left_status, tongue_status, head_yaw, head_pitch, tongue_out):
        """Display status overlay on frame"""
        h, w = frame.shape[:2]
        
        # Control status
        control_status = "CONTROL: ON ✓" if self.control_enabled else "CONTROL: OFF (press 't')"
        cv2.putText(frame, control_status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, 
                   (0, 255, 0) if self.control_enabled else (0, 0, 255), 2)
        
        # Head tracking status
        cv2.putText(frame, f"Head Yaw: {head_yaw:.1f}° Pitch: {head_pitch:.1f}°", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # WASD status
        wasd_text = "WASD: "
        wasd_colors = []
        for key, active in wasd_states.items():
            if active:
                wasd_text += f"{key.upper()} "
                wasd_colors.append((0, 255, 0))  # Green for active
            else:
                wasd_colors.append((128, 128, 128))  # Gray for inactive
        
        cv2.putText(frame, wasd_text, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Right hand status
        gun_color = (0, 255, 0) if gun_active else (0, 0, 255)
        cv2.putText(frame, f"Gun: {'ACTIVE ✓' if gun_active else 'INACTIVE ✗'}", (10, 130), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, gun_color, 1)
        cv2.putText(frame, f"Shoot: {shoot_status}", (10, 160), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Left hand status
        cv2.putText(frame, f"Left: {left_status}", (10, 190), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Tongue status
        tongue_color = (0, 255, 0) if tongue_out else (255, 255, 255)
        cv2.putText(frame, f"Tongue: {tongue_status}", (10, 220), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, tongue_color, 1)
        
        # Instructions
        cv2.putText(frame, "Press 't' to toggle | 'q' to quit", (10, h - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

if __name__ == "__main__":
    system = CompleteControlSystem()
    system.run()
