"""
TEST 5: Thumb-Based Shooting (Full Auto!)
Goal: Press thumb down to shoot, hold for continuous fire
Expected: 
- Gun locked with thumb up = ready
- Press thumb down = FIRE (holds mouse button)
- Release thumb = stop firing
Controls: 
- Press 'c' to toggle control ON/OFF
- Press 'q' to quit
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
    # Don't require thumb position for initial detection
    is_gun = index_extended and middle_curled and ring_curled and pinky_curled
    return is_gun

def is_thumb_down(hand_landmarks):
    """
    Detect if thumb is pressed down (closer to palm)
    Returns True if thumb is DOWN (shooting position)
    """
    landmarks = hand_landmarks.landmark
    
    # Thumb tip (4) vs Index MCP (5)
    thumb_tip = landmarks[4]
    index_mcp = landmarks[5]
    wrist = landmarks[0]
    
    # Method 1: Y-position - thumb below index base = pressed down
    thumb_below = thumb_tip.y > index_mcp.y
    
    # Method 2: Distance from wrist - thumb close to wrist = pressed down
    thumb_to_wrist = ((thumb_tip.x - wrist.x)**2 + (thumb_tip.y - wrist.y)**2)**0.5
    index_to_wrist = ((index_mcp.x - wrist.x)**2 + (index_mcp.y - wrist.y)**2)**0.5
    thumb_close = thumb_to_wrist < index_to_wrist * 0.8
    
    # Thumb is down if either condition is met
    return thumb_below or thumb_close

def are_bottom_fingers_curled(hand_landmarks):
    """Check if bottom 3 fingers are curled (rotation-proof)"""
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
        """
        Handle mouse button based on thumb state
        Returns: (is_shooting, action_taken)
        """
        if not control_enabled:
            # If control disabled, release mouse if currently held
            if self.is_shooting:
                pyautogui.mouseUp()
                self.is_shooting = False
            return False, "Control Disabled"
        
        if thumb_is_down and not self.is_shooting:
            # Thumb pressed down - start shooting
            pyautogui.mouseDown()
            self.is_shooting = True
            return True, "Started Shooting!"
        elif not thumb_is_down and self.is_shooting:
            # Thumb released - stop shooting
            pyautogui.mouseUp()
            self.is_shooting = False
            return False, "Stopped Shooting"
        elif self.is_shooting:
            # Continue shooting
            return True, "Shooting..."
        else:
            # Not shooting
            return False, "Ready"
    
    def force_release(self):
        """Emergency release"""
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
        screen_x = int(finger_x * self.screen_width)  # Removed inversion
        screen_y = int(finger_y * self.screen_height)
        
        if self.prev_x is not None:
            screen_x = int(self.smoothing_factor * self.prev_x + (1 - self.smoothing_factor) * screen_x)
            screen_y = int(self.smoothing_factor * self.prev_y + (1 - self.smoothing_factor) * screen_y)
        
        self.prev_x = screen_x
        self.prev_y = screen_y
        
        return screen_x, screen_y
    
    def move_mouse(self, screen_x, screen_y):
        pyautogui.moveTo(screen_x, screen_y)

# Initialize
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.3
)

cap = cv2.VideoCapture(0)

gun_detector = StickyGunDetector(grace_period=30)
shooting_controller = ThumbShootingController()
mouse_controller = SmoothMouseController(smoothing_factor=0.5)

control_enabled = False

print("=" * 70)
print("TEST 5: Thumb-Based Shooting")
print("=" * 70)
print("Controls:")
print("  'c' - Toggle control ON/OFF")
print("  'q' - Quit")
print("\nHow to use:")
print("  1. Make gun gesture (index out, bottom 3 curled)")
print("  2. Thumb UP = ready to shoot")
print("  3. Press THUMB DOWN = START FIRING (holds mouse)")
print("  4. Release THUMB UP = STOP FIRING")
print("  5. Index finger controls cursor")
print("\nPerfect for CS:GO spray control!")
print("=" * 70)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break
    
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    
    hand_landmarks = None
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        mp_drawing.draw_landmarks(
            frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
            mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2)
        )
    
    gun_active = gun_detector.update(hand_landmarks)
    is_shooting = False
    shoot_status = "Ready"
    thumb_down = False
    
    if gun_active and hand_landmarks:
        # Get index finger for aiming
        index_tip = hand_landmarks.landmark[8]
        
        # Move mouse cursor
        if control_enabled:
            screen_x, screen_y = mouse_controller.update(index_tip.x, index_tip.y)
            mouse_controller.move_mouse(screen_x, screen_y)
        
        # Check thumb position for shooting
        thumb_down = is_thumb_down(hand_landmarks)
        is_shooting, shoot_status = shooting_controller.update(thumb_down, control_enabled)
        
        # Debug output
        if thumb_down and control_enabled and is_shooting:
            print(f"SHOOTING! Thumb down, mouse button held")
        
        # Visual indicators for thumb
        thumb_tip = hand_landmarks.landmark[4]
        tx = int(thumb_tip.x * w)
        ty = int(thumb_tip.y * h)
        thumb_color = (0, 0, 255) if thumb_down else (0, 255, 255)
        cv2.circle(frame, (tx, ty), 12, thumb_color, -1)
        cv2.putText(frame, "THUMB", (tx + 15, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.6, thumb_color, 2)
    else:
        # Gun not active - release mouse if held
        shooting_controller.force_release()
    
    # Control status
    control_status = "CONTROL: ON ✓" if control_enabled else "CONTROL: OFF (press 'c')"
    control_color = (0, 255, 0) if control_enabled else (0, 0, 255)
    cv2.putText(frame, control_status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, control_color, 2)
    
    # Gun status
    if gun_active:
        status = "🔒 GUN LOCKED"
        color = (0, 255, 0)
    else:
        status = "Make Gun Gesture"
        color = (0, 0, 255)
    
    cv2.putText(frame, status, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    
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
        if gun_active:
            shoot_text = f"Thumb: {'DOWN ⬇' if thumb_down else 'UP ⬆'}"
            if thumb_down and not control_enabled:
                shoot_text += " (Enable control with 'c'!)"
                shoot_color = (0, 255, 255)
        else:
            shoot_text = "Make gun gesture first"
    
    cv2.putText(frame, shoot_text, (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, shoot_color, 2)
    
    # Instructions
    if gun_active:
        cv2.putText(frame, "Press thumb DOWN to shoot!", (10, h - 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    
    cv2.putText(frame, "Press 'c' to toggle | 'q' to quit", (10, h - 20), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    cv2.imshow('TEST 5: Thumb Shooting', frame)
    
    key = cv2.waitKey(5) & 0xFF
    if key == ord('q'):
        shooting_controller.force_release()  # Make sure mouse is released
        break
    elif key == ord('c'):
        control_enabled = not control_enabled
        if not control_enabled:
            shooting_controller.force_release()
        print(f"\n{'='*50}")
        print(f"Control {'ENABLED ✓' if control_enabled else 'DISABLED ✗'}")
        print(f"{'='*50}\n")

cap.release()
cv2.destroyAllWindows()
hands.close()
shooting_controller.force_release()
print("\n🎉 Thumb shooting ready for CS:GO!")

