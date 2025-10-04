"""
Tutorial Mode Implementation
Step-by-step gesture training with AI-powered tips and voice instructions
"""

import time
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
from config import config
from ai_commentary import gemini_commentary
from voice_synthesis import voice_synthesis

class TutorialMode:
    """Tutorial mode for learning gesture controls"""
    
    def __init__(self):
        self.current_lesson = 0
        self.lessons = self._create_lessons()
        self.current_gesture = None
        self.lesson_start_time = 0
        self.gesture_practice_time = 0
        self.success_count = 0
        self.attempt_count = 0
        self.performance_scores = []
        self.last_tip_time = 0
        self.tip_cooldown = 5  # seconds between tips
        
        # Visual feedback
        self.overlay_alpha = 0.7
        self.progress_bar_width = 300
        self.progress_bar_height = 20
        
        print("✓ Tutorial Mode initialized")
    
    def _create_lessons(self) -> List[Dict]:
        """Create the tutorial lessons"""
        return [
            {
                'id': 'gun_gesture',
                'name': 'Gun Gesture',
                'description': 'Learn to make the gun gesture for aiming',
                'instruction': 'Extend your index finger and curl your other three fingers',
                'success_threshold': 0.8,
                'practice_duration': 30,  # seconds
                'tips': [
                    "Keep your index finger straight and firm!",
                    "Make sure your other fingers are curled tight.",
                    "Practice until the gesture feels natural!"
                ]
            },
            {
                'id': 'thumb_shooting',
                'name': 'Thumb Shooting',
                'description': 'Learn to shoot by lowering your thumb',
                'instruction': 'Keep gun gesture, then lower your thumb to shoot',
                'success_threshold': 0.7,
                'practice_duration': 25,
                'tips': [
                    "Lower your thumb slowly for precise shooting!",
                    "Keep your index finger steady while shooting.",
                    "Try to maintain the gun gesture while shooting."
                ]
            },
            {
                'id': 'head_movement',
                'name': 'Head Movement (W/S)',
                'description': 'Learn head tilting for forward/backward movement',
                'instruction': 'Tilt your head forward for S, backward for W',
                'success_threshold': 0.6,
                'practice_duration': 30,
                'tips': [
                    "Move your head smoothly for better control!",
                    "Practice tilting forward and backward.",
                    "Keep your movements controlled and deliberate."
                ]
            },
            {
                'id': 'body_leaning',
                'name': 'Body Leaning (A/D)',
                'description': 'Learn body leaning for left/right movement',
                'instruction': 'Lean your body left for A, right for D',
                'success_threshold': 0.6,
                'practice_duration': 30,
                'tips': [
                    "Lean from your torso, not just your shoulders!",
                    "Practice shifting your weight left and right.",
                    "Keep your movements balanced and controlled."
                ]
            },
            {
                'id': 'tongue_spray',
                'name': 'Tongue Spray',
                'description': 'Learn tongue gesture for spray emotes',
                'instruction': 'Stick out your tongue to trigger spray emote',
                'success_threshold': 0.8,
                'practice_duration': 20,
                'tips': [
                    "Stick out your tongue clearly for the spray!",
                    "Make sure your mouth opens enough to trigger.",
                    "Practice the tongue gesture - it's fun!"
                ]
            },
            {
                'id': 'left_hand_crouch',
                'name': 'Left Hand Crouch',
                'description': 'Learn left hand gesture for crouching',
                'instruction': 'Show one finger down on your left hand',
                'success_threshold': 0.7,
                'practice_duration': 25,
                'tips': [
                    "Show one finger clearly on your left hand!",
                    "Make sure your palm faces the camera.",
                    "Practice switching between gestures quickly."
                ]
            },
            {
                'id': 'left_hand_jump',
                'name': 'Left Hand Jump',
                'description': 'Learn left hand gesture for jumping',
                'instruction': 'Show four fingers down on your left hand',
                'success_threshold': 0.7,
                'practice_duration': 25,
                'tips': [
                    "Show four fingers down for jumping!",
                    "Keep your thumb up when jumping.",
                    "Practice the jump gesture for quick movements."
                ]
            }
        ]
    
    def start_tutorial(self):
        """Start the tutorial mode"""
        self.current_lesson = 0
        self.performance_scores = []
        self.lesson_start_time = time.time()
        self.current_gesture = self.lessons[0]
        
        # Welcome message
        welcome_text = f"Welcome to CS:GO Gesture Control Tutorial! Let's start with {self.current_gesture['name']}."
        print(f"TUTORIAL: {welcome_text}")
        
        if voice_synthesis.is_available():
            voice_synthesis.speak_text(welcome_text)
        
        print(f"Lesson 1/{len(self.lessons)}: {self.current_gesture['name']}")
        print(f"Instruction: {self.current_gesture['instruction']}")
    
    def update_tutorial(self, gesture_data: Dict, frame: np.ndarray) -> Tuple[bool, str]:
        """
        Update tutorial progress based on current gesture performance
        Returns: (tutorial_complete, status_message)
        """
        if self.current_lesson >= len(self.lessons):
            return True, "Tutorial completed!"
        
        current_time = time.time()
        lesson_elapsed = current_time - self.lesson_start_time
        self.gesture_practice_time += 0.033  # Assume 30 FPS
        
        # Check if current gesture is being performed correctly
        gesture_performance = self._evaluate_gesture_performance(gesture_data)
        
        # Update success/attempt counts
        self.attempt_count += 1
        if gesture_performance > self.current_gesture['success_threshold']:
            self.success_count += 1
        
        # Calculate current performance score
        current_score = self.success_count / max(1, self.attempt_count)
        self.performance_scores.append(current_score)
        
        # Provide tips periodically
        if (current_time - self.last_tip_time > self.tip_cooldown and 
            current_score < self.current_gesture['success_threshold']):
            
            tip = gemini_commentary.generate_tutorial_tip(
                self.current_gesture['id'], 
                current_score
            )
            
            print(f"TUTORIAL TIP: {tip}")
            
            if voice_synthesis.is_available():
                voice_synthesis.speak_tutorial_tip(tip)
            
            self.last_tip_time = current_time
        
        # Check if lesson is complete
        lesson_complete = (
            lesson_elapsed >= self.current_gesture['practice_duration'] and
            current_score >= self.current_gesture['success_threshold']
        )
        
        if lesson_complete:
            return self._complete_current_lesson()
        
        # Draw tutorial overlay
        self._draw_tutorial_overlay(frame, current_score, lesson_elapsed)
        
        # Status message
        status = f"Lesson {self.current_lesson + 1}/{len(self.lessons)}: {self.current_gesture['name']} - Progress: {current_score:.1%}"
        
        return False, status
    
    def _evaluate_gesture_performance(self, gesture_data: Dict) -> float:
        """Evaluate how well the current gesture is being performed"""
        gesture_id = self.current_gesture['id']
        
        if gesture_id == 'gun_gesture':
            return self._evaluate_gun_gesture(gesture_data)
        elif gesture_id == 'thumb_shooting':
            return self._evaluate_thumb_shooting(gesture_data)
        elif gesture_id == 'head_movement':
            return self._evaluate_head_movement(gesture_data)
        elif gesture_id == 'body_leaning':
            return self._evaluate_body_leaning(gesture_data)
        elif gesture_id == 'tongue_spray':
            return self._evaluate_tongue_spray(gesture_data)
        elif gesture_id == 'left_hand_crouch':
            return self._evaluate_left_hand_crouch(gesture_data)
        elif gesture_id == 'left_hand_jump':
            return self._evaluate_left_hand_jump(gesture_data)
        
        return 0.0
    
    def _evaluate_gun_gesture(self, gesture_data: Dict) -> float:
        """Evaluate gun gesture performance"""
        if not gesture_data.get('gun_active', False):
            return 0.0
        
        # Simple evaluation - gun is active
        return 1.0
    
    def _evaluate_thumb_shooting(self, gesture_data: Dict) -> float:
        """Evaluate thumb shooting performance"""
        if not gesture_data.get('gun_active', False):
            return 0.0
        
        if gesture_data.get('is_shooting', False):
            return 1.0
        
        return 0.5  # Gun active but not shooting
    
    def _evaluate_head_movement(self, gesture_data: Dict) -> float:
        """Evaluate head movement performance"""
        wasd_states = gesture_data.get('wasd_states', {})
        if wasd_states.get('w', False) or wasd_states.get('s', False):
            return 1.0
        
        head_pitch = gesture_data.get('head_pitch', 0)
        if abs(head_pitch) > 5:  # Some head movement detected
            return 0.5
        
        return 0.0
    
    def _evaluate_body_leaning(self, gesture_data: Dict) -> float:
        """Evaluate body leaning performance"""
        wasd_states = gesture_data.get('wasd_states', {})
        if wasd_states.get('a', False) or wasd_states.get('d', False):
            return 1.0
        
        left_right_lean = gesture_data.get('left_right_lean', 0)
        if abs(left_right_lean) > 2:  # Some body lean detected
            return 0.5
        
        return 0.0
    
    def _evaluate_tongue_spray(self, gesture_data: Dict) -> float:
        """Evaluate tongue spray performance"""
        if gesture_data.get('tongue_out', False):
            return 1.0
        
        return 0.0
    
    def _evaluate_left_hand_crouch(self, gesture_data: Dict) -> float:
        """Evaluate left hand crouch performance"""
        left_action = gesture_data.get('left_action')
        if left_action == 'ctrl':
            return 1.0
        
        return 0.0
    
    def _evaluate_left_hand_jump(self, gesture_data: Dict) -> float:
        """Evaluate left hand jump performance"""
        left_action = gesture_data.get('left_action')
        if left_action == 'space':
            return 1.0
        
        return 0.0
    
    def _complete_current_lesson(self) -> Tuple[bool, str]:
        """Complete the current lesson and move to next"""
        # Save performance score
        final_score = self.success_count / max(1, self.attempt_count)
        
        completion_text = f"Great job! You completed {self.current_gesture['name']} with {final_score:.1%} accuracy!"
        print(f"TUTORIAL: {completion_text}")
        
        if voice_synthesis.is_available():
            voice_synthesis.speak_text(completion_text)
        
        # Move to next lesson
        self.current_lesson += 1
        
        if self.current_lesson >= len(self.lessons):
            return True, "Tutorial completed! You're ready to play!"
        
        # Start next lesson
        self.current_gesture = self.lessons[self.current_lesson]
        self.lesson_start_time = time.time()
        self.gesture_practice_time = 0
        self.success_count = 0
        self.attempt_count = 0
        
        next_lesson_text = f"Next lesson: {self.current_gesture['name']}. {self.current_gesture['instruction']}"
        print(f"TUTORIAL: {next_lesson_text}")
        
        if voice_synthesis.is_available():
            voice_synthesis.speak_text(next_lesson_text)
        
        return False, f"Starting lesson {self.current_lesson + 1}/{len(self.lessons)}: {self.current_gesture['name']}"
    
    def _draw_tutorial_overlay(self, frame: np.ndarray, current_score: float, lesson_elapsed: float):
        """Draw tutorial overlay on the frame"""
        h, w = frame.shape[:2]
        
        # Semi-transparent overlay
        overlay = frame.copy()
        
        # Draw progress bar
        progress_x = w - self.progress_bar_width - 20
        progress_y = 20
        
        # Background
        cv2.rectangle(overlay, 
                     (progress_x, progress_y),
                     (progress_x + self.progress_bar_width, progress_y + self.progress_bar_height),
                     (50, 50, 50), -1)
        
        # Progress fill
        progress_width = int(self.progress_bar_width * current_score)
        color = (0, 255, 0) if current_score >= self.current_gesture['success_threshold'] else (0, 255, 255)
        
        cv2.rectangle(overlay,
                     (progress_x, progress_y),
                     (progress_x + progress_width, progress_y + self.progress_bar_height),
                     color, -1)
        
        # Progress text
        progress_text = f"Progress: {current_score:.1%}"
        cv2.putText(overlay, progress_text, (progress_x, progress_y - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Lesson info
        lesson_text = f"Lesson {self.current_lesson + 1}/{len(self.lessons)}: {self.current_gesture['name']}"
        cv2.putText(overlay, lesson_text, (20, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Instruction
        instruction_text = self.current_gesture['instruction']
        cv2.putText(overlay, instruction_text, (20, 80),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # Time remaining
        time_remaining = max(0, self.current_gesture['practice_duration'] - lesson_elapsed)
        time_text = f"Time remaining: {time_remaining:.1f}s"
        cv2.putText(overlay, time_text, (20, 110),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Success threshold
        threshold_text = f"Target: {self.current_gesture['success_threshold']:.1%}"
        cv2.putText(overlay, threshold_text, (20, 140),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Apply overlay
        cv2.addWeighted(overlay, self.overlay_alpha, frame, 1 - self.overlay_alpha, 0, frame)
    
    def get_current_lesson(self) -> Optional[Dict]:
        """Get current lesson information"""
        if self.current_lesson < len(self.lessons):
            return self.lessons[self.current_lesson]
        return None
    
    def get_tutorial_progress(self) -> Dict:
        """Get tutorial progress information"""
        return {
            'current_lesson': self.current_lesson,
            'total_lessons': len(self.lessons),
            'progress_percent': (self.current_lesson / len(self.lessons)) * 100,
            'performance_scores': self.performance_scores,
            'current_gesture': self.current_gesture
        }
    
    def skip_lesson(self):
        """Skip the current lesson"""
        if self.current_lesson < len(self.lessons) - 1:
            self.current_lesson += 1
            self.current_gesture = self.lessons[self.current_lesson]
            self.lesson_start_time = time.time()
            self.gesture_practice_time = 0
            self.success_count = 0
            self.attempt_count = 0
            
            skip_text = f"Skipped to lesson {self.current_lesson + 1}: {self.current_gesture['name']}"
            print(f"TUTORIAL: {skip_text}")
            
            if voice_synthesis.is_available():
                voice_synthesis.speak_text(skip_text)

# Global instance
tutorial_mode = TutorialMode()
