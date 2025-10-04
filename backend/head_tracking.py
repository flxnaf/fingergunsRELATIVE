"""
HEAD TEST 3: WASD Movement Control
Goal: Control WASD keys with head tilts (for CS:GO movement)
Expected: 
- Tilt LEFT → Press 'A' (move left)
- Tilt RIGHT → Press 'D' (move right)
- Tilt UP → Press 'W' (move forward)
- Tilt DOWN → Press 'S' (move backward)

Controls: 
- Press 'c' to toggle control ON/OFF
- Press 'q' to quit
- Press '+'/'-' to adjust yaw threshold
- Press '['/']' to adjust pitch threshold
"""

import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time

# Safety
pyautogui.PAUSE = 0.01

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

class WASDController:
    def __init__(self, yaw_threshold=5, pitch_threshold=8, pitch_threshold_back=12, hysteresis=0.7):
        self.yaw_threshold = yaw_threshold
        self.pitch_threshold = pitch_threshold  # For W (forward/look down)
        self.pitch_threshold_back = pitch_threshold_back  # For S (backward/look up) - LESS SENSITIVE
        self.hysteresis = hysteresis  # Multiplier for release threshold (0.7 = release at 70% of press threshold)
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
            # Already pressing A - only release if we move back towards center
            if yaw > -yaw_release:
                pass  # Release A (don't add to desired_keys)
            else:
                desired_keys.add('a')  # Keep pressing A
        elif yaw < -self.yaw_threshold:
            desired_keys.add('a')  # Start pressing A
            
        if 'd' in self.current_keys:
            # Already pressing D
            if yaw < yaw_release:
                pass  # Release D
            else:
                desired_keys.add('d')  # Keep pressing D
        elif yaw > self.yaw_threshold:
            desired_keys.add('d')  # Start pressing D
            
        # Up/Down
        if 'w' in self.current_keys:
            # Already pressing W
            if pitch > -pitch_release:
                pass  # Release W
            else:
                desired_keys.add('w')  # Keep pressing W
        elif pitch < -self.pitch_threshold:
            desired_keys.add('w')  # Start pressing W (look down = forward)
            
        if 's' in self.current_keys:
            # Already pressing S
            if pitch < pitch_release_back:
                pass  # Release S
            else:
                desired_keys.add('s')  # Keep pressing S
        elif pitch > self.pitch_threshold_back:
            desired_keys.add('s')  # Start pressing S (look up = backward) - LESS SENSITIVE
        
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

# Initialize MediaPipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

cap = cv2.VideoCapture(0)

wasd_controller = WASDController(yaw_threshold=3, pitch_threshold=5, pitch_threshold_back=12)  # S is less sensitive
control_enabled = False

print("=" * 70)
print("HEAD TEST 3: WASD Movement Control")
print("=" * 70)
print("Controls:")
print("  'c' - Toggle control ON/OFF")
print("  'q' - Quit")
print("  '+'/'-' - Adjust yaw (left/right) sensitivity")
print("  '['/']' - Adjust pitch (up/down) sensitivity")
print("\nHead movements:")
print("  Tilt LEFT → A key (strafe left)")
print("  Tilt RIGHT → D key (strafe right)")
print("  Tilt UP (look up) → W key (forward)")
print("  Tilt DOWN (look down) → S key (backward)")
print("\nSAFETY: Control starts DISABLED. Press 'c' to enable.")
print("=" * 70)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break
    
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)
    
    yaw = 0
    pitch = 0
    key_states = {'w': False, 'a': False, 's': False, 'd': False}
    
    if results.multi_face_landmarks:
        face_landmarks = results.multi_face_landmarks[0]
        
        # Calculate head pose
        yaw, pitch = calculate_head_pose(face_landmarks, w, h)
        
        # Update WASD control
        active_keys, key_states = wasd_controller.update(yaw, pitch, control_enabled)
    else:
        # No face detected - release all keys
        wasd_controller.release_all_keys()
        key_states = {'w': False, 'a': False, 's': False, 'd': False}
    
    # Control status
    control_status = "CONTROL: ON ✓" if control_enabled else "CONTROL: OFF (press 'c')"
    control_color = (0, 255, 0) if control_enabled else (0, 0, 255)
    cv2.putText(frame, control_status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, control_color, 2)
    
    # Face detection status
    if results.multi_face_landmarks:
        status = "Face Detected ✓"
        color = (0, 255, 0)
    else:
        status = "No Face Detected"
        color = (0, 0, 255)
    
    cv2.putText(frame, status, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    # Display angles
    cv2.putText(frame, f"Yaw: {yaw:.1f}", (10, 90), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(frame, f"Pitch: {pitch:.1f}", (10, 115), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # WASD visual indicator (like a keyboard)
    indicator_x = w - 180
    indicator_y = 80
    key_size = 50
    gap = 10
    
    # W key (top)
    w_color = (0, 255, 0) if key_states['w'] else (100, 100, 100)
    cv2.rectangle(frame, (indicator_x + key_size + gap, indicator_y), 
                 (indicator_x + key_size*2 + gap, indicator_y + key_size), w_color, -1)
    cv2.putText(frame, "W", (indicator_x + key_size + gap + 15, indicator_y + 35), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    # A key (left)
    a_color = (0, 255, 0) if key_states['a'] else (100, 100, 100)
    cv2.rectangle(frame, (indicator_x, indicator_y + key_size + gap), 
                 (indicator_x + key_size, indicator_y + key_size*2 + gap), a_color, -1)
    cv2.putText(frame, "A", (indicator_x + 15, indicator_y + key_size + gap + 35), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    # S key (bottom)
    s_color = (0, 255, 0) if key_states['s'] else (100, 100, 100)
    cv2.rectangle(frame, (indicator_x + key_size + gap, indicator_y + key_size + gap), 
                 (indicator_x + key_size*2 + gap, indicator_y + key_size*2 + gap), s_color, -1)
    cv2.putText(frame, "S", (indicator_x + key_size + gap + 15, indicator_y + key_size + gap + 35), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    # D key (right)
    d_color = (0, 255, 0) if key_states['d'] else (100, 100, 100)
    cv2.rectangle(frame, (indicator_x + key_size*2 + gap*2, indicator_y + key_size + gap), 
                 (indicator_x + key_size*3 + gap*2, indicator_y + key_size*2 + gap), d_color, -1)
    cv2.putText(frame, "D", (indicator_x + key_size*2 + gap*2 + 15, indicator_y + key_size + gap + 35), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    # Thresholds
    cv2.putText(frame, f"Yaw threshold: {wasd_controller.yaw_threshold} (+/-)", 
               (10, h - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
    cv2.putText(frame, f"Pitch threshold: {wasd_controller.pitch_threshold} ([/])", 
               (10, h - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
    cv2.putText(frame, "Press 'c' to toggle | 'q' to quit", 
               (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    cv2.imshow('HEAD TEST 3: WASD Control', frame)
    
    key = cv2.waitKey(5) & 0xFF
    if key == ord('q'):
        wasd_controller.release_all_keys()
        break
    elif key == ord('c'):
        control_enabled = not control_enabled
        if not control_enabled:
            wasd_controller.release_all_keys()
        print(f"\n{'='*50}")
        print(f"Control {'ENABLED ✓' if control_enabled else 'DISABLED ✗'}")
        print(f"{'='*50}\n")
    elif key == ord('+') or key == ord('='):
        wasd_controller.yaw_threshold += 1
        print(f"Yaw threshold: {wasd_controller.yaw_threshold}")
    elif key == ord('-'):
        wasd_controller.yaw_threshold = max(1, wasd_controller.yaw_threshold - 1)
        print(f"Yaw threshold: {wasd_controller.yaw_threshold}")
    elif key == ord(']'):
        wasd_controller.pitch_threshold += 1
        print(f"Pitch threshold: {wasd_controller.pitch_threshold}")
    elif key == ord('['):
        wasd_controller.pitch_threshold = max(1, wasd_controller.pitch_threshold - 1)
        print(f"Pitch threshold: {wasd_controller.pitch_threshold}")

cap.release()
cv2.destroyAllWindows()
face_mesh.close()
wasd_controller.release_all_keys()
print("\n🎉 Head test 3 complete! Ready for CS:GO movement!")

