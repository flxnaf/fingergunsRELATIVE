"""
Simple test script to demonstrate relative mouse positioning
This shows how the system remembers the last position and moves relatively
"""

import cv2
import mediapipe as mp
import pyautogui
import time

# Disable fail-safe for gaming
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

# Simple relative mouse controller
class RelativeMouseController:
    def __init__(self, sensitivity=1.5):
        self.sensitivity = sensitivity
        self.last_x = None
        self.last_y = None
        self.screen_width, self.screen_height = pyautogui.size()
        print(f"Screen resolution: {self.screen_width}x{self.screen_height}")
        
    def update_and_move(self, finger_x, finger_y):
        """Update position and move mouse relatively"""
        # Convert normalized coordinates to pixels
        current_x = finger_x * self.screen_width
        current_y = finger_y * self.screen_height
        
        delta_x = 0
        delta_y = 0
        
        # Calculate delta if we have previous position
        if self.last_x is not None and self.last_y is not None:
            delta_x = (current_x - self.last_x) * self.sensitivity
            delta_y = (current_y - self.last_y) * self.sensitivity
            
            # Move mouse relatively
            if delta_x != 0 or delta_y != 0:
                pyautogui.moveRel(int(delta_x), int(delta_y))
        
        # Store current position for next frame
        self.last_x = current_x
        self.last_y = current_y
        
        return int(delta_x), int(delta_y)
    
    def reset(self):
        """Reset tracking - cursor stays where it is"""
        self.last_x = None
        self.last_y = None
        print("Position tracking reset")

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.3
)

# Initialize camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Initialize controller
mouse_controller = RelativeMouseController(sensitivity=1.5)
tracking_active = False

print("=" * 70)
print("RELATIVE POSITIONING TEST")
print("=" * 70)
print("Controls:")
print("  't' - Toggle tracking ON/OFF")
print("  'q' - Quit")
print("\nHow to test:")
print("  1. Press 't' to enable tracking")
print("  2. Point with your index finger")
print("  3. Move your hand - cursor moves relatively")
print("  4. Press 't' to disable - cursor stays in place")
print("  5. Press 't' again - tracking resumes from current position")
print("\nNotice: When you re-enable tracking, the cursor doesn't jump!")
print("This is the key feature for FPS games.")
print("=" * 70)

frame_count = 0

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        time.sleep(0.1)
        continue
    
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process hands
    results = hands.process(rgb_frame)
    
    delta_x, delta_y = 0, 0
    
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        
        # Draw hand landmarks
        mp_drawing.draw_landmarks(
            frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
            mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2)
        )
        
        # Get index finger tip
        index_tip = hand_landmarks.landmark[8]
        
        # Draw index finger position
        ix = int(index_tip.x * w)
        iy = int(index_tip.y * h)
        cv2.circle(frame, (ix, iy), 15, (0, 255, 255), -1)
        cv2.putText(frame, "INDEX", (ix + 20, iy), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # Update mouse position if tracking is active
        if tracking_active:
            delta_x, delta_y = mouse_controller.update_and_move(index_tip.x, index_tip.y)
    
    # Display status
    status = "TRACKING: ON ✓" if tracking_active else "TRACKING: OFF (press 't')"
    color = (0, 255, 0) if tracking_active else (0, 0, 255)
    cv2.putText(frame, status, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)
    
    # Display delta movement
    if tracking_active:
        cv2.putText(frame, f"Delta: X={delta_x} Y={delta_y}", (10, 80), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Instructions
    cv2.putText(frame, "Point with index finger", (10, h - 60), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    cv2.putText(frame, "Press 't' to toggle | 'q' to quit", (10, h - 20), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    # Show frame
    cv2.imshow('Relative Positioning Test', frame)
    
    # Handle keyboard
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('t'):
        tracking_active = not tracking_active
        if not tracking_active:
            mouse_controller.reset()
        print(f"\n{'='*50}")
        print(f"Tracking {'ENABLED ✓' if tracking_active else 'DISABLED ✗'}")
        print(f"{'='*50}\n")
    
    frame_count += 1

# Cleanup
cap.release()
cv2.destroyAllWindows()
hands.close()
print("\n✅ Test completed!")
print("Notice: The cursor stayed in place when you disabled/enabled tracking!")
print("This is perfect for FPS games where you need continuous mouse control.")

