"""
KRUNKER OPTIMIZED MODE
Special configuration for browser-based FPS games like Krunker.io
Higher sensitivity and more aggressive tracking for browser games
"""

import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time
from pynput.mouse import Controller as MouseController
from Quartz.CoreGraphics import (
    CGEventCreateMouseEvent, 
    CGEventPost, 
    kCGEventMouseMoved,
    kCGEventLeftMouseDown,
    kCGEventLeftMouseUp, 
    kCGHIDEventTap, 
    kCGEventTapOptionDefault,
    CGEventCreate, 
    CGEventGetLocation,
    CGEventSetIntegerValueField,
    kCGMouseEventDeltaX,
    kCGMouseEventDeltaY
)

# CRITICAL: Disable fail-safe for gaming
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

# MediaPipe initialization
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def is_finger_extended(landmarks, finger_tip_id, finger_pip_id, finger_mcp_id):
    tip = [landmarks[finger_tip_id].x, landmarks[finger_tip_id].y]
    pip = [landmarks[finger_pip_id].x, landmarks[finger_pip_id].y]
    mcp = [landmarks[finger_mcp_id].x, landmarks[finger_mcp_id].y]
    
    vector1 = np.array([tip[0] - pip[0], tip[1] - pip[1]])
    vector2 = np.array([mcp[0] - pip[0], mcp[1] - pip[1]])
    cosine = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2) + 1e-6)
    angle = np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))
    return angle > 140

def is_gun_gesture(hand_landmarks):
    """Detect gun gesture (index out, bottom 3 curled)"""
    if hand_landmarks is None:
        return False
    landmarks = hand_landmarks.landmark
    index_extended = is_finger_extended(landmarks, 8, 6, 5)
    middle_curled = not is_finger_extended(landmarks, 12, 10, 9)
    ring_curled = not is_finger_extended(landmarks, 16, 14, 13)
    pinky_curled = not is_finger_extended(landmarks, 20, 18, 17)
    return index_extended and middle_curled and ring_curled and pinky_curled

def is_thumb_down(hand_landmarks):
    """Detect if thumb is pressed down (shooting position)"""
    landmarks = hand_landmarks.landmark
    thumb_tip = landmarks[4]
    thumb_ip = landmarks[3]
    return thumb_tip.y > thumb_ip.y

def are_bottom_fingers_curled(hand_landmarks):
    """Check if bottom 3 fingers are curled"""
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
                print("🔫 Gun LOCKED!")
                return True
            else:
                return False
        else:
            self.lock_frames += 1
            if not bottom_fingers_curled:
                self.is_locked = False
                self.lock_frames = 0
                print("🔫 Gun UNLOCKED!")
                return False
            else:
                return True

class ThumbShootingController:
    def __init__(self):
        self.is_pressed = False
        self.last_thumb_down = False
        
    def update(self, hand_landmarks, gun_active):
        if not gun_active or hand_landmarks is None:
            self.force_release()
            return False, "Gun not active"
        
        thumb_down = is_thumb_down(hand_landmarks)
        
        if thumb_down and not self.last_thumb_down:
            if not self.is_pressed:
                pyautogui.mouseDown()
                self.is_pressed = True
                return True, "FIRING!"
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

class KrunkerMouseController:
    """Optimized for Krunker - smooth interpolation + native macOS mouse events"""
    def __init__(self, sensitivity=3.5, smoothing_frames=3):
        self.sensitivity = sensitivity
        self.smoothing_frames = smoothing_frames  # Frames to smooth over when re-establishing
        self.last_x = None
        self.last_y = None
        self.debug_counter = 0
        self.move_counter = 0  # Separate counter for movement verification
        self.gun_was_active = False
        self.interpolation_queue = []  # Queue for smooth movement
        print(f"🎮 Krunker Mouse Controller - Native macOS events | Sensitivity: {self.sensitivity}")
        
    def _move_mouse_native(self, delta_x, delta_y):
        """Use native macOS CGEvent with delta fields for browser compatibility"""
        try:
            # Get current mouse position
            event = CGEventCreate(None)
            current_pos = CGEventGetLocation(event)
            
            # Calculate new position
            new_x = current_pos.x + delta_x
            new_y = current_pos.y + delta_y
            
            # Create mouse move event
            move_event = CGEventCreateMouseEvent(None, kCGEventMouseMoved, (new_x, new_y), 0)
            
            # CRITICAL FOR BROWSERS: Set the delta fields explicitly
            # This makes browsers see it as relative movement (like a real mouse)
            CGEventSetIntegerValueField(move_event, kCGMouseEventDeltaX, int(delta_x))
            CGEventSetIntegerValueField(move_event, kCGMouseEventDeltaY, int(delta_y))
            
            # Post the event
            CGEventPost(kCGHIDEventTap, move_event)
            
            # Verify the movement (debug)
            self.move_counter += 1
            if self.move_counter % 60 == 0:
                print(f"🖱️  CGEvent posted with delta: ({int(delta_x)}, {int(delta_y)})")
            
        except Exception as e:
            print(f"❌ Native mouse error: {e}")
        
    def update(self, hand_landmarks, gun_active):
        if not gun_active or hand_landmarks is None:
            self.gun_was_active = False
            return
            
        try:
            index_tip = hand_landmarks.landmark[8]
            
            # Convert to pixels for tracking
            current_x = index_tip.x * 1920
            current_y = index_tip.y * 1080
            
            # Process any queued interpolation movements FIRST
            if self.interpolation_queue:
                step_dx, step_dy = self.interpolation_queue.pop(0)
                self._move_mouse_native(int(step_dx), int(step_dy))
                print(f"📊 Interpolating: dx={int(step_dx)}, dy={int(step_dy)} ({len(self.interpolation_queue)} steps remaining)")
                # Don't update last position yet - keep interpolating
                return
            
            # Check if this is first frame after gun activation
            if not self.gun_was_active:
                # First frame - check if we need to interpolate (gap in tracking)
                if self.last_x is not None and self.last_y is not None:
                    # Calculate total delta from last known position
                    total_dx = current_x - self.last_x
                    total_dy = current_y - self.last_y
                    distance = (total_dx**2 + total_dy**2)**0.5
                    
                    # If the gap is large, queue up smooth interpolated movements
                    if distance > 30:  # Lowered threshold to catch more gaps
                        print(f"🔄 Smoothing gap: dx={int(total_dx)}, dy={int(total_dy)}, distance={int(distance)}px")
                        # Create interpolation steps (spread movement over multiple frames)
                        for i in range(1, self.smoothing_frames + 1):
                            fraction = i / self.smoothing_frames
                            step_dx = (total_dx * fraction / self.smoothing_frames) * self.sensitivity
                            step_dy = (total_dy * fraction / self.smoothing_frames) * self.sensitivity
                            self.interpolation_queue.append((step_dx, step_dy))
                    else:
                        print(f"🔄 Small gap: {int(distance)}px - no smoothing needed")
                else:
                    print("🔄 Position tracking established (first time)")
                    
            elif self.last_x is not None and self.last_y is not None:
                # Normal tracking - calculate and apply delta movement
                delta_x = (current_x - self.last_x) * self.sensitivity
                delta_y = (current_y - self.last_y) * self.sensitivity
                
                # Apply movement using native macOS events
                if abs(delta_x) > 0.5 or abs(delta_y) > 0.5:
                    self._move_mouse_native(int(delta_x), int(delta_y))
                
                # Debug output
                self.debug_counter += 1
                if self.debug_counter % 30 == 0:
                    print(f"📍 Mouse: dx={int(delta_x)}, dy={int(delta_y)}")
            
            # Always update last position for next frame
            self.last_x = current_x
            self.last_y = current_y
            self.gun_was_active = True
            
        except Exception as e:
            print(f"❌ Mouse error: {e}")

# Initialize
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_FPS, 60)  # Higher FPS for better tracking

gun_detector = StickyGunDetector(grace_period=30)
shooting_controller = ThumbShootingController()
mouse_controller = KrunkerMouseController(sensitivity=3.5)  # Higher for Krunker

control_enabled = False

print("=" * 70)
print("🎯 KRUNKER OPTIMIZED MODE")
print("=" * 70)
print("Controls:")
print("  'g' - Toggle control ON/OFF")
print("  'q' - Quit")
print("  '+' - Increase sensitivity")
print("  '-' - Decrease sensitivity")
print("\nSetup for Krunker:")
print("  1. Open Krunker.io in your browser")
print("  2. Start a game (go into pointer lock mode)")
print("  3. Alt+Tab back here and press 'g' to enable")
print("  4. Alt+Tab back to Krunker")
print("  5. Make gun gesture and start playing!")
print("\nGestures:")
print("  - Gun: Index finger out, other 3 fingers curled")
print("  - Shoot: Thumb DOWN")
print("  - Stop: Thumb UP")
print("=" * 70)

frame_count = 0
last_frame_time = time.time()

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.01)
            continue
        
        frame_count += 1
        if frame_count % 60 == 0:
            fps = 60 / (time.time() - last_frame_time) if time.time() > last_frame_time else 0
            print(f"🎮 FPS: {fps:.1f} | Control: {'ON' if control_enabled else 'OFF'}")
            last_frame_time = time.time()
        
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        results = hands.process(rgb_frame)
        
        gun_active = False
        is_shooting = False
        shoot_status = "No hand"
        
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Draw landmarks
            mp_drawing.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2)
            )
            
            if control_enabled:
                gun_active = gun_detector.update(hand_landmarks)
                
                if gun_active:
                    is_shooting, shoot_status = shooting_controller.update(hand_landmarks, gun_active)
                    mouse_controller.update(hand_landmarks, gun_active)
                else:
                    shooting_controller.force_release()
        
        # Display status
        status = "CONTROL: ON ✓" if control_enabled else "CONTROL: OFF (press 'g')"
        color = (0, 255, 0) if control_enabled else (0, 0, 255)
        cv2.putText(frame, status, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)
        
        gun_color = (0, 255, 0) if gun_active else (128, 128, 128)
        cv2.putText(frame, f"Gun: {'ACTIVE' if gun_active else 'Make gesture'}", (10, 80), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, gun_color, 2)
        
        if is_shooting:
            cv2.putText(frame, "🔥 FIRING! 🔥", (10, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        cv2.putText(frame, f"Sensitivity: {mouse_controller.sensitivity:.1f}", (10, h - 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, "Press '+'/'-' to adjust | 'g' toggle | 'q' quit", (10, h - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.imshow('Krunker Mode', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break
        elif key == ord('g'):
            control_enabled = not control_enabled
            if not control_enabled:
                shooting_controller.force_release()
            print(f"\n{'='*50}")
            print(f"🎮 Control {'ENABLED ✓' if control_enabled else 'DISABLED ✗'}")
            print(f"{'='*50}\n")
        elif key == ord('+') or key == ord('='):
            mouse_controller.sensitivity += 0.5
            print(f"📈 Sensitivity increased to {mouse_controller.sensitivity:.1f}")
        elif key == ord('-') or key == ord('_'):
            mouse_controller.sensitivity = max(0.5, mouse_controller.sensitivity - 0.5)
            print(f"📉 Sensitivity decreased to {mouse_controller.sensitivity:.1f}")

except KeyboardInterrupt:
    print("\n⏹️  Interrupted")
finally:
    print("🧹 Cleaning up...")
    shooting_controller.force_release()
    cap.release()
    cv2.destroyAllWindows()
    hands.close()
    print("✅ Done!")

