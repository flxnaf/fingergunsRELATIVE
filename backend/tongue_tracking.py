"""
TONGUE TRACKING: CS:GO Emote Spray Detection
Goal: Detect when tongue is stuck out and activate emote spray
Expected: 
- Tongue out → Activate emote spray (usually 'T' key)
- Tongue back in → Stop spray emote
- Add debouncing to prevent spam

Controls: 
- Press 'c' to toggle control ON/OFF
- Press 'q' to quit
- Press '+'/'-' to adjust tongue detection sensitivity
"""

import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time

# Safety
pyautogui.PAUSE = 0.01
pyautogui.FAILSAFE = True

class TongueDetector:
    def __init__(self, sensitivity=0.015, debounce_frames=10):
        """
        Initialize mouth opening detector with blue line separation method
        
        Args:
            sensitivity: Threshold for mouth line separation (0.01-0.05)
            debounce_frames: Frames to wait before registering new detection
        """
        self.sensitivity = sensitivity  # Threshold for blue line separation
        self.debounce_frames = debounce_frames
        self.last_tongue_detection = 0
        self.frames_since_last_detection = 0
        self.tongue_out = False
        self.spray_active = False
        self.spray_start_time = 0
        
        # MediaPipe face mesh landmarks for mouth/lip detection
        self.mouth_landmarks = {
            'upper_lip_top': 13,
            'upper_lip_bottom': 14, 
            'lower_lip_top': 17,
            'lower_lip_bottom': 18,
            'mouth_left': 61,
            'mouth_right': 291,
            'tongue_tip': 2,  # Inner mouth landmark
            'mouth_center': 0   # Center of mouth
        }
    
    def detect_mouth_open(self, face_landmarks):
        """
        Detect mouth opening by measuring separation of blue mouth outline lines
        Simple and reliable - just check vertical distance between upper and lower lip lines
        
        Args:
            face_landmarks: MediaPipe face landmarks
            
        Returns:
            bool: True if mouth lines are separated enough
        """
        if not face_landmarks:
            return False
        
        landmarks = face_landmarks.landmark
        
        # Get the key points that form the blue mouth outline
        upper_lip_bottom = landmarks[13]  # Upper lip bottom edge
        lower_lip_top = landmarks[14]     # Lower lip top edge
        
        # Simple calculation: vertical distance between upper and lower lip lines
        lip_separation = lower_lip_top.y - upper_lip_bottom.y
        
        # Just check if the blue lines are separated beyond threshold
        mouth_open = lip_separation > self.sensitivity
        
        return mouth_open
    
    def update(self, face_landmarks, control_enabled):
        """
        Update tongue detection and handle key press
        
        Args:
            face_landmarks: MediaPipe face landmarks
            control_enabled: Whether controls are active
            
        Returns:
            dict: Detection status and action taken
        """
        current_time = time.time()
        
        # Detect mouth opening
        mouth_open = self.detect_mouth_open(face_landmarks)
        
        if not control_enabled:
            return {
                'tongue_detected': False,
                'action': 'Control Disabled',
                'spray_active': False
            }
        
        # Handle T key press on mouth opening with better debouncing
        if mouth_open:
            # Only trigger if enough time has passed since last detection
            if current_time - self.last_tongue_detection > 1.0:  # 1 second debounce
                self.last_tongue_detection = current_time
                pyautogui.press('t')  # Press T key once
                action = "Pressed 'T' key!"
                print(f"Mouth open detected! T key pressed at {current_time:.2f}")
            else:
                time_since_last = current_time - self.last_tongue_detection
                action = f"Mouth open (debounced - {1.0-time_since_last:.1f}s)"
        else:
            # Reset debounce timer when mouth is closed
            if current_time - self.last_tongue_detection > 0.1:  # Small delay to prevent immediate re-trigger
                action = "👄 Ready to open mouth"
            else:
                action = "Mouth closed - waiting..."
        
        return {
            'tongue_detected': mouth_open,
            'action': action,
            'spray_active': False
        }
    
    def adjust_sensitivity(self, delta):
        """Adjust tongue detection sensitivity"""
        self.sensitivity = max(0.005, min(0.1, self.sensitivity + delta))
        print(f"Tongue sensitivity: {self.sensitivity:.3f}")

class TongueTrackingController:
    def __init__(self):
        self.tongue_detector = TongueDetector(sensitivity=0.02, debounce_frames=10)
        self.control_enabled = False
        
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        
        print("CS:GO Emote Spray controller initialized!")
        print("Press 'c' to toggle control, 'q' to quit")
        print("Press '+/-' to adjust sensitivity")
    
    def run(self):
        """Main tongue tracking loop"""
        print("=" * 70)
        print("TONGUE TRACKING: T Key Press Detection")
        print("=" * 70)
        print("Controls:")
        print("  'c' - Toggle control ON/OFF")
        print("  'q' - Quit")
        print("  '+'/'-' - Adjust tongue detection sensitivity")
        print("\nHow to use:")
        print("  1. Make sure your face is visible")
        print("  2. Press 'c' to enable control")
        print("  3. Open mouth to separate the blue lines")
        print("  4. When blue lines separate enough = 'T' key pressed")
        print("  5. Use '+/-' to adjust line separation threshold")
        print("\nPerfect for CS:GO spray emotes!")
        print("=" * 70)
        
        while self.cap.isOpened():
            success, frame = self.cap.read()
            if not success:
                break
            
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process face mesh
            results = self.face_mesh.process(rgb_frame)
            
            face_landmarks = None
            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
            
            # Update tongue detection
            detection_result = self.tongue_detector.update(face_landmarks, self.control_enabled)
            
            # Draw face landmarks if detected
            if face_landmarks:
                self.draw_face_landmarks(frame, face_landmarks)
                self.draw_mouth_landmarks(frame, face_landmarks)
            
            # Display status
            self.display_status(frame, detection_result, w, h)
            
            # Show frame
            cv2.imshow('Tongue Tracking: T Key Detection', frame)
            
            # Handle keyboard input
            key = cv2.waitKey(5) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c'):
                self.control_enabled = not self.control_enabled
                if not self.control_enabled:
                    # Release key if control disabled
                    if self.tongue_detector.t_key_pressed:
                        pyautogui.keyUp('t')
                        self.tongue_detector.t_key_pressed = False
                print(f"\n{'='*50}")
                print(f"Control {'ENABLED ✓' if self.control_enabled else 'DISABLED ✗'}")
                print(f"{'='*50}\n")
            elif key == ord('+') or key == ord('='):
                self.tongue_detector.adjust_sensitivity(0.005)
            elif key == ord('-'):
                self.tongue_detector.adjust_sensitivity(-0.005)
        
        # Cleanup
        self.cleanup()
    
    def draw_face_landmarks(self, frame, face_landmarks):
        """Draw face mesh landmarks"""
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing.draw_landmarks(
            frame, face_landmarks, self.mp_face_mesh.FACEMESH_CONTOURS,
            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1),
            mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1)
        )
    
    def draw_mouth_landmarks(self, frame, face_landmarks):
        """Highlight mouth area landmarks"""
        h, w, _ = frame.shape
        landmarks = face_landmarks.landmark
        
        # Draw mouth landmarks
        mouth_landmarks = [13, 14, 17, 18, 61, 291]
        for landmark_id in mouth_landmarks:
            if landmark_id < len(landmarks):
                x = int(landmarks[landmark_id].x * w)
                y = int(landmarks[landmark_id].y * h)
                cv2.circle(frame, (x, y), 3, (0, 0, 255), -1)
        
        # Draw mouth outline
        mouth_points = []
        for landmark_id in [61, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318, 13, 82, 81, 80, 78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308, 291]:
            if landmark_id < len(landmarks):
                x = int(landmarks[landmark_id].x * w)
                y = int(landmarks[landmark_id].y * h)
                mouth_points.append([x, y])
        
        if len(mouth_points) > 2:
            mouth_points = np.array(mouth_points, np.int32)
            cv2.polylines(frame, [mouth_points], True, (255, 0, 0), 2)
    
    def display_status(self, frame, detection_result, w, h):
        """Display status information on frame"""
        # Control status
        control_status = "CONTROL: ON ✓" if self.control_enabled else "CONTROL: OFF (press 'c')"
        control_color = (0, 255, 0) if self.control_enabled else (0, 0, 255)
        cv2.putText(frame, control_status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, control_color, 2)
        
        # Mouth opening status
        if detection_result['tongue_detected']:
            status = "👄 MOUTH OPEN!"
            color = (0, 0, 255)  # Red
            # Add red flash effect
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 255), -1)
            frame = cv2.addWeighted(frame, 0.8, overlay, 0.2, 0)
        else:
            status = "Mouth closed - Ready"
            color = (255, 255, 255)  # White
        
        cv2.putText(frame, status, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        # Action status
        action = detection_result['action']
        action_color = (0, 255, 255) if detection_result['tongue_detected'] else (255, 255, 255)
        cv2.putText(frame, action, (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, action_color, 2)
        
        # Sensitivity
        cv2.putText(frame, f"Sensitivity: {self.tongue_detector.sensitivity:.3f} (+/-)", 
                   (10, h - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        
        # Instructions
        cv2.putText(frame, "Press 'c' to toggle | 'q' to quit", (10, h - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    def cleanup(self):
        """Clean up resources"""
        self.cap.release()
        cv2.destroyAllWindows()
        self.face_mesh.close()
        
        # No need to release key since we're using press() instead of keyDown()
        
        print("\n🎉 Tongue tracking complete! Ready for CS:GO spray emotes!")

if __name__ == "__main__":
    controller = TongueTrackingController()
    controller.run()
