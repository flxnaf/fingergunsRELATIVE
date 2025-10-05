"""
INTEGRATED CS:GO CONTROL SYSTEM
Combines:
- Dual hand tracking (from dual_hand_tracking.py)
- Head tracking for W/S only (from head_tracking.py, modified)
- Tongue tracking for spray emote (from tongue_tracking.py)

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
pyautogui.FAILSAFE = True

# MediaPipe initialization
mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

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
    thumb_ip = landmarks[3]
    thumb_mcp = landmarks[2]
    
    # Thumb pointing down if tip is below IP joint
    return thumb_tip.y > thumb_ip.y

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

def calculate_head_pose(face_landmarks, frame_width, frame_height):
    """Calculate head pose (yaw and pitch for WASD movement)"""
    nose_tip = face_landmarks.landmark[1]
    left_eye = face_landmarks.landmark[33]
    right_eye = face_landmarks.landmark[263]
    chin = face_landmarks.landmark[152]
    forehead = face_landmarks.landmark[10]
    
    # Yaw (left/right)
    eye_center_x = (left_eye.x + right_eye.x) / 2
    nose_x = nose_tip.x
    yaw = (nose_x - eye_center_x) * 100
    
    # Pitch (forward/backward)
    nose_y = nose_tip.y
    chin_y = chin.y
    forehead_y = forehead.y
    face_height = chin_y - forehead_y
    nose_position = (nose_y - forehead_y) / face_height if face_height > 0 else 0.5
    pitch = (nose_position - 0.5) * 100
    
    return yaw, pitch

def detect_mouth_open(face_landmarks):
    """Detect mouth opening using blue line separation method"""
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

class StickyGunDetector:
    """Gun gesture detector with sticky behavior (from dual_hand_tracking.py)"""
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
        if is_gun_gesture(hand_landmarks):
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
    """Mouse click controller based on thumb position (from dual_hand_tracking.py)"""
    def __init__(self):
        self.is_pressed = False
        self.last_thumb_down = False
        
    def update(self, hand_landmarks, gun_active):
        if not gun_active or hand_landmarks is None:
            self.force_release()
            return False, "Gun not active"
        
        thumb_down = is_thumb_down(hand_landmarks)
        
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
    """Relative mouse movement controller for FPS games - TRUE relative positioning, no snapping"""
    def __init__(self, sensitivity=1.0):
        self.sensitivity = sensitivity
        self.last_x = None
        self.last_y = None
        self.debug_counter = 0
        self.gun_was_active = False  # Track gun state to prevent snapping
        
    def update(self, hand_landmarks, gun_active):
        if not gun_active or hand_landmarks is None:
            # DON'T reset position - keep last known position to prevent snapping
            self.gun_was_active = False
            return
            
        try:
            # Get index finger tip position (normalized 0-1)
            index_tip = hand_landmarks.landmark[8]
            
            # Convert to screen pixels for tracking (using standard 1920x1080)
            current_x = index_tip.x * 1920
            current_y = index_tip.y * 1080
            
            # Check if this is first frame after gun activation
            if not self.gun_was_active:
                # First frame - establish baseline WITHOUT moving cursor
                print("🔄 Position tracking reestablished (no snap)")
            elif self.last_x is not None and self.last_y is not None:
                # Subsequent frames - calculate and apply delta movement
                delta_x = (current_x - self.last_x) * self.sensitivity
                delta_y = (current_y - self.last_y) * self.sensitivity
                
                # Use relative mouse movement (perfect for FPS games)
                pyautogui.moveRel(int(delta_x), int(delta_y))
                
                # Debug output every 30 frames
                self.debug_counter += 1
                if self.debug_counter % 30 == 0:
                    print(f"Relative mouse delta: x={int(delta_x)}, y={int(delta_y)}")
            
            # Always update last position for next frame
            self.last_x = current_x
            self.last_y = current_y
            self.gun_was_active = True
            
        except Exception as e:
            print(f"Mouse control error: {e}")

class LeftHandGestureController:
    """Left hand gesture controller for crouch/jump (from dual_hand_tracking.py)"""
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

class WASDController:
    """Head tracking controller for WASD movement (modified from head_tracking.py)"""
    def __init__(self, yaw_threshold=2, pitch_threshold=8, pitch_threshold_back=12, hysteresis=0.7):
        self.yaw_threshold = yaw_threshold
        self.pitch_threshold = pitch_threshold  # For W (head forward)
        self.pitch_threshold_back = pitch_threshold_back  # For S (head backward)
        self.hysteresis = hysteresis  # Multiplier for release threshold
        self.current_keys = set()  # Currently pressed keys
        
    def update(self, yaw, pitch, control_enabled):
        """
        Update WASD keys based on head tilt
        Returns: (active_keys, key_states)
        """
        if not control_enabled:
            # Release all keys if control disabled
            self.release_all_keys()
            return set(), {'w': False, 'a': False, 's': False, 'd': False}
        
        desired_keys = set()
        
        # Calculate release thresholds (closer to center)
        yaw_release = self.yaw_threshold * self.hysteresis
        pitch_release = self.pitch_threshold * self.hysteresis
        pitch_release_back = self.pitch_threshold_back * self.hysteresis
        
        # Determine which keys should be pressed (with hysteresis)
        # Left/Right
        if 'a' in self.current_keys:
            # Already pressing A
            if yaw > -yaw_release:
                pass  # Release A
            else:
                desired_keys.add('a')  # Keep pressing A
        elif yaw < -self.yaw_threshold:
            desired_keys.add('a')  # Start pressing A (head left)
            
        if 'd' in self.current_keys:
            # Already pressing D
            if yaw < yaw_release:
                pass  # Release D
            else:
                desired_keys.add('d')  # Keep pressing D
        elif yaw > self.yaw_threshold:
            desired_keys.add('d')  # Start pressing D (head right)
            
        # Forward/Backward (switched W and S)
        if 'w' in self.current_keys:
            # Already pressing W
            if pitch < pitch_release_back:
                pass  # Release W
            else:
                desired_keys.add('w')  # Keep pressing W
        elif pitch > self.pitch_threshold_back:
            desired_keys.add('w')  # Start pressing W (head backward)
            
        if 's' in self.current_keys:
            # Already pressing S
            if pitch > -pitch_release:
                pass  # Release S
            else:
                desired_keys.add('s')  # Keep pressing S
        elif pitch < -self.pitch_threshold:
            desired_keys.add('s')  # Start pressing S (head forward)
        
        # Release keys that should no longer be pressed
        keys_to_release = self.current_keys - desired_keys
        for key in keys_to_release:
            pyautogui.keyUp(key)
            print(f"Released: {key.upper()}")
        
        # Press keys that should be pressed
        keys_to_press = desired_keys - self.current_keys
        for key in keys_to_press:
            pyautogui.keyDown(key)
            print(f"Pressed: {key.upper()}")
        
        self.current_keys = desired_keys
        
        # Create key state dict for display
        key_states = {
            'w': 'w' in desired_keys,
            'a': 'a' in desired_keys,
            's': 's' in desired_keys,
            'd': 'd' in desired_keys
        }
        
        return desired_keys, key_states
    
    def release_all_keys(self):
        """Release all currently pressed keys"""
        for key in self.current_keys:
            pyautogui.keyUp(key)
        if self.current_keys:
            print(f"Released all keys: {', '.join([k.upper() for k in self.current_keys])}")
        self.current_keys = set()

class TongueController:
    """Tongue detection controller for spray emote (from tongue_tracking.py)"""
    def __init__(self, sensitivity=0.015, debounce_frames=10):
        self.sensitivity = sensitivity
        self.debounce_frames = debounce_frames
        self.frames_held = 0
        self.last_tongue_out = False
        
    def update(self, face_landmarks, control_enabled):
        if not control_enabled or face_landmarks is None:
            self.frames_held = 0
            self.last_tongue_out = False
            return False, "Control Disabled"
        
        tongue_out = detect_mouth_open(face_landmarks)
        
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

class IntegratedControlSystem:
    """Complete integrated CS:GO control system"""
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
        
        print("Integrated CS:GO Control System initialized!")
        print("Head: WASD movement (forward/backward/left/right)")
        print("Right hand: Gun control + shooting")
        print("Left hand: Crouch/jump")
        print("Tongue: Spray emote")
    
    def identify_hands(self, hand_landmarks_list):
        """Identify which hand is left vs right based on position (from dual_hand_tracking.py)"""
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
        print("Integrated CS:GO Control System")
        print("=" * 50)
        print("Controls:")
        print("  't' - Toggle control ON/OFF")
        print("  'q' - Quit")
        print("\nHead Movement (WASD):")
        print("  - Head FORWARD → Press 'S' (move forward)")
        print("  - Head BACKWARD → Press 'W' (move backward)")
        print("  - Head LEFT → Press 'A' (move left)")
        print("  - Head RIGHT → Press 'D' (move right)")
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
        print("\nPerfect for integrated CS:GO control!")
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
                        
                        # Draw face mesh
                        mp_drawing.draw_landmarks(
                            frame, face_landmarks, mp_face_mesh.FACEMESH_CONTOURS,
                            None, mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1)
                        )
                        
                        # Head tracking for WASD
                        head_yaw, head_pitch = calculate_head_pose(face_landmarks, w, h)
                        
                        # Debug output for A/D detection
                        if abs(head_yaw) > 1.5:  # Only print when there's significant yaw movement
                            print(f"DEBUG: Yaw={head_yaw:.1f}, Pitch={head_pitch:.1f}")
                        
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
                        # Draw hand landmarks
                        for hand_landmarks in hand_results.multi_hand_landmarks:
                            mp_drawing.draw_landmarks(
                                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
                                mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=2)
                            )
                        
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
                cv2.imshow('Integrated CS:GO Control System', frame)
                
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
                print("\n🎉 Integrated control system finished!")
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
        
        # WASD status (top left)
        wasd_text = "WASD: "
        for key, active in wasd_states.items():
            if active:
                wasd_text += f"{key.upper()} "
                
        if not any(wasd_states.values()):
            wasd_text += "None"
            
        cv2.putText(frame, wasd_text, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # WASD overlay in top right corner
        overlay_x = w - 150
        overlay_y = 30
        overlay_width = 120
        overlay_height = 80
        
        # Draw background rectangle
        cv2.rectangle(frame, (overlay_x, overlay_y), (overlay_x + overlay_width, overlay_y + overlay_height), (0, 0, 0), -1)
        cv2.rectangle(frame, (overlay_x, overlay_y), (overlay_x + overlay_width, overlay_y + overlay_height), (255, 255, 255), 2)
        
        # Draw key indicators
        key_positions = {
            'w': (overlay_x + 50, overlay_y + 25),
            'a': (overlay_x + 15, overlay_y + 50),
            's': (overlay_x + 50, overlay_y + 50),
            'd': (overlay_x + 85, overlay_y + 50)
        }
        
        for key, (x, y) in key_positions.items():
            color = (0, 255, 0) if wasd_states[key] else (128, 128, 128)
            cv2.circle(frame, (x, y), 15, color, -1)
            cv2.circle(frame, (x, y), 15, (255, 255, 255), 2)
            cv2.putText(frame, key.upper(), (x - 8, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        # Add title
        cv2.putText(frame, "WASD", (overlay_x + 35, overlay_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
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
    system = IntegratedControlSystem()
    system.run()
