"""
SIMPLE DUAL HAND TEST
Basic test to see if dual hand tracking works without crashing
"""

import cv2
import mediapipe as mp
import numpy as np

def main():
    print("Starting simple dual hand test...")
    
    # Initialize MediaPipe
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    
    try:
        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,  # Enable dual hand tracking
            min_detection_confidence=0.5,
            min_tracking_confidence=0.3
        )
        print("MediaPipe hands initialized successfully")
    except Exception as e:
        print(f"Error initializing MediaPipe: {e}")
        return
    
    # Initialize camera
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open camera")
            return
        print("Camera opened successfully")
    except Exception as e:
        print(f"Error opening camera: {e}")
        return
    
    frame_count = 0
    
    try:
        while cap.isOpened():
            frame_count += 1
            print(f"Processing frame {frame_count}...")
            
            success, frame = cap.read()
            if not success:
                print("Failed to read frame")
                break
            
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process hands
            try:
                results = hands.process(rgb_frame)
                print(f"Frame {frame_count}: MediaPipe processed successfully")
            except Exception as e:
                print(f"Frame {frame_count}: Error in MediaPipe processing: {e}")
                continue
            
            # Check for hands
            if results.multi_hand_landmarks:
                num_hands = len(results.multi_hand_landmarks)
                print(f"Frame {frame_count}: Detected {num_hands} hand(s)")
                
                # Draw landmarks
                for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    try:
                        mp_drawing.draw_landmarks(
                            frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                            mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2)
                        )
                        print(f"Frame {frame_count}: Drew landmarks for hand {i+1}")
                    except Exception as e:
                        print(f"Frame {frame_count}: Error drawing landmarks for hand {i+1}: {e}")
            else:
                print(f"Frame {frame_count}: No hands detected")
            
            # Display frame
            try:
                cv2.imshow('Simple Dual Hand Test', frame)
            except Exception as e:
                print(f"Frame {frame_count}: Error showing frame: {e}")
                break
            
            # Handle keyboard
            try:
                key = cv2.waitKey(5) & 0xFF
                if key == ord('q'):
                    print("Quit key pressed")
                    break
            except Exception as e:
                print(f"Frame {frame_count}: Error handling keyboard: {e}")
                break
            
            # Safety limit for testing
            if frame_count > 100:
                print("Reached 100 frames, stopping test")
                break
                
    except Exception as e:
        print(f"Error in main loop: {e}")
    
    finally:
        # Cleanup
        try:
            cap.release()
            cv2.destroyAllWindows()
            hands.close()
            print("Cleanup completed")
        except Exception as e:
            print(f"Error during cleanup: {e}")
    
    print("Simple dual hand test completed")

if __name__ == "__main__":
    main()
