"""
Virtual Character Overlay System
Creates animated character overlays for Backseat Gamer mode
"""

import cv2
import numpy as np
import math
import time
from typing import Dict, List, Tuple, Optional
from config import config

class CharacterOverlay:
    """Virtual character overlay for backseat gamer mode"""
    
    def __init__(self):
        self.character_style = config.backseat_character_style
        self.animation_speed = config.character_animation_speed
        self.opacity = config.overlay_opacity
        
        # Character properties
        self.character_size = 150
        self.character_x = 50
        self.character_y = 200
        self.current_animation = 'idle'
        self.animation_frame = 0
        self.animation_start_time = time.time()
        
        # Character expressions
        self.current_expression = 'neutral'
        self.expression_duration = 0
        self.expression_start_time = time.time()
        
        # Character colors (anime style)
        self.colors = {
            'skin': (255, 220, 177),
            'hair': (101, 67, 33),
            'eyes': (0, 100, 200),
            'mouth': (200, 100, 100),
            'shirt': (100, 150, 255),
            'pants': (50, 50, 150),
            'shoes': (30, 30, 30)
        }
        
        # Animation states
        self.animations = {
            'idle': {'duration': 2.0, 'frames': 20},
            'excited': {'duration': 1.0, 'frames': 15},
            'thinking': {'duration': 3.0, 'frames': 30},
            'celebrating': {'duration': 1.5, 'frames': 25},
            'disappointed': {'duration': 2.0, 'frames': 20}
        }
        
        # Speech bubble
        self.speech_bubble = {
            'visible': False,
            'text': '',
            'start_time': 0,
            'duration': 3.0
        }
        
        print("✓ Character Overlay initialized")
    
    def update_character(self, game_state: Dict[str, any], commentary: str = ""):
        """Update character based on game state and commentary"""
        current_time = time.time()
        
        # Update animation
        self._update_animation()
        
        # Update expression based on game state
        self._update_expression(game_state)
        
        # Update speech bubble
        self._update_speech_bubble(commentary, current_time)
    
    def _update_animation(self):
        """Update character animation frame"""
        current_time = time.time()
        elapsed = current_time - self.animation_start_time
        
        animation = self.animations[self.current_animation]
        frame_duration = animation['duration'] / animation['frames']
        
        self.animation_frame = int(elapsed / frame_duration) % animation['frames']
    
    def _update_expression(self, game_state: Dict[str, any]):
        """Update character expression based on game state"""
        current_time = time.time()
        
        # Determine expression based on performance
        performance_score = game_state.get('performance_score', 0.5)
        gesture_accuracy = game_state.get('gesture_accuracy', 0.5)
        
        if performance_score > 0.8 or gesture_accuracy > 0.9:
            new_expression = 'excited'
            new_animation = 'celebrating'
        elif performance_score < 0.3 or gesture_accuracy < 0.4:
            new_expression = 'disappointed'
            new_animation = 'disappointed'
        elif game_state.get('current_action') == 'thinking':
            new_expression = 'thinking'
            new_animation = 'thinking'
        else:
            new_expression = 'neutral'
            new_animation = 'idle'
        
        # Change expression if needed
        if new_expression != self.current_expression:
            self.current_expression = new_expression
            self.current_animation = new_animation
            self.animation_start_time = current_time
            self.expression_start_time = current_time
    
    def _update_speech_bubble(self, commentary: str, current_time: float):
        """Update speech bubble display"""
        if commentary and commentary != self.speech_bubble['text']:
            self.speech_bubble['visible'] = True
            self.speech_bubble['text'] = commentary
            self.speech_bubble['start_time'] = current_time
        
        # Hide bubble after duration
        if (self.speech_bubble['visible'] and 
            current_time - self.speech_bubble['start_time'] > self.speech_bubble['duration']):
            self.speech_bubble['visible'] = False
    
    def draw_character(self, frame: np.ndarray):
        """Draw the character overlay on the frame"""
        h, w = frame.shape[:2]
        
        # Create character overlay
        overlay = np.zeros_like(frame)
        
        # Draw character based on style
        if self.character_style == 'anime':
            self._draw_anime_character(overlay)
        else:
            self._draw_simple_character(overlay)
        
        # Draw speech bubble
        if self.speech_bubble['visible']:
            self._draw_speech_bubble(overlay)
        
        # Apply overlay to frame
        cv2.addWeighted(overlay, self.opacity, frame, 1 - self.opacity, 0, frame)
    
    def _draw_anime_character(self, overlay: np.ndarray):
        """Draw anime-style character"""
        x, y = self.character_x, self.character_y
        size = self.character_size
        
        # Animation effects
        bounce = math.sin(self.animation_frame * 0.3) * 5
        eye_blink = 1 if (self.animation_frame // 10) % 2 else 0.7
        
        # Body (shirt)
        cv2.rectangle(overlay, 
                     (x + size//4, y + size//3 + int(bounce)),
                     (x + 3*size//4, y + 2*size//3 + int(bounce)),
                     self.colors['shirt'], -1)
        
        # Head (circle)
        head_center = (x + size//2, y + size//4 + int(bounce))
        cv2.circle(overlay, head_center, size//4, self.colors['skin'], -1)
        
        # Hair
        hair_points = np.array([
            [x + size//4, y + size//4 + int(bounce)],
            [x + size//2, y + size//8 + int(bounce)],
            [x + 3*size//4, y + size//4 + int(bounce)],
            [x + 3*size//4, y + size//3 + int(bounce)],
            [x + size//4, y + size//3 + int(bounce)]
        ], np.int32)
        cv2.fillPoly(overlay, [hair_points], self.colors['hair'])
        
        # Eyes
        eye_size = size//20
        left_eye = (x + size//2 - size//8, y + size//4 - size//16 + int(bounce))
        right_eye = (x + size//2 + size//8, y + size//4 - size//16 + int(bounce))
        
        # Eye expression
        if self.current_expression == 'excited':
            cv2.circle(overlay, left_eye, eye_size, self.colors['eyes'], -1)
            cv2.circle(overlay, right_eye, eye_size, self.colors['eyes'], -1)
            # Sparkles
            cv2.circle(overlay, (left_eye[0] + eye_size, left_eye[1] - eye_size), 3, (255, 255, 0), -1)
            cv2.circle(overlay, (right_eye[0] + eye_size, right_eye[1] - eye_size), 3, (255, 255, 0), -1)
        elif self.current_expression == 'disappointed':
            # Sad eyes
            cv2.ellipse(overlay, left_eye, (eye_size, eye_size//2), 0, 0, 180, self.colors['eyes'], -1)
            cv2.ellipse(overlay, right_eye, (eye_size, eye_size//2), 0, 0, 180, self.colors['eyes'], -1)
        elif self.current_expression == 'thinking':
            # Thinking pose
            cv2.circle(overlay, left_eye, eye_size, self.colors['eyes'], -1)
            cv2.circle(overlay, right_eye, eye_size, self.colors['eyes'], -1)
            # Question mark
            cv2.putText(overlay, "?", (x + size + 10, y + int(bounce)), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        else:
            # Normal eyes
            cv2.circle(overlay, left_eye, int(eye_size * eye_blink), self.colors['eyes'], -1)
            cv2.circle(overlay, right_eye, int(eye_size * eye_blink), self.colors['eyes'], -1)
        
        # Mouth
        mouth_center = (x + size//2, y + size//4 + size//16 + int(bounce))
        if self.current_expression == 'excited':
            # Happy mouth
            cv2.ellipse(overlay, mouth_center, (size//16, size//20), 0, 0, 180, self.colors['mouth'], -1)
        elif self.current_expression == 'disappointed':
            # Sad mouth
            cv2.ellipse(overlay, mouth_center, (size//16, size//20), 0, 180, 360, self.colors['mouth'], -1)
        else:
            # Neutral mouth
            cv2.line(overlay, 
                    (mouth_center[0] - size//16, mouth_center[1]),
                    (mouth_center[0] + size//16, mouth_center[1]),
                    self.colors['mouth'], 2)
        
        # Arms (based on animation)
        if self.current_animation == 'celebrating':
            # Raised arms
            cv2.line(overlay, (x + size//4, y + size//3 + int(bounce)),
                    (x + size//8, y + size//8 + int(bounce)), self.colors['skin'], 8)
            cv2.line(overlay, (x + 3*size//4, y + size//3 + int(bounce)),
                    (x + 7*size//8, y + size//8 + int(bounce)), self.colors['skin'], 8)
        else:
            # Normal arms
            cv2.line(overlay, (x + size//4, y + size//3 + int(bounce)),
                    (x + size//6, y + 2*size//3 + int(bounce)), self.colors['skin'], 8)
            cv2.line(overlay, (x + 3*size//4, y + size//3 + int(bounce)),
                    (x + 5*size//6, y + 2*size//3 + int(bounce)), self.colors['skin'], 8)
        
        # Legs
        cv2.rectangle(overlay,
                     (x + size//3, y + 2*size//3 + int(bounce)),
                     (x + 2*size//3, y + size + int(bounce)),
                     self.colors['pants'], -1)
        
        # Shoes
        cv2.rectangle(overlay,
                     (x + size//4, y + size + int(bounce)),
                     (x + 3*size//4, y + size + size//8 + int(bounce)),
                     self.colors['shoes'], -1)
    
    def _draw_simple_character(self, overlay: np.ndarray):
        """Draw simple character"""
        x, y = self.character_x, self.character_y
        size = self.character_size
        
        # Simple stick figure
        # Head
        cv2.circle(overlay, (x + size//2, y + size//4), size//8, (255, 255, 255), -1)
        
        # Body
        cv2.line(overlay, (x + size//2, y + size//4 + size//8),
                (x + size//2, y + 2*size//3), (255, 255, 255), 4)
        
        # Arms
        cv2.line(overlay, (x + size//2, y + size//3),
                (x + size//4, y + 2*size//3), (255, 255, 255), 3)
        cv2.line(overlay, (x + size//2, y + size//3),
                (x + 3*size//4, y + 2*size//3), (255, 255, 255), 3)
        
        # Legs
        cv2.line(overlay, (x + size//2, y + 2*size//3),
                (x + size//3, y + size), (255, 255, 255), 3)
        cv2.line(overlay, (x + size//2, y + 2*size//3),
                (x + 2*size//3, y + size), (255, 255, 255), 3)
    
    def _draw_speech_bubble(self, overlay: np.ndarray):
        """Draw speech bubble with text"""
        if not self.speech_bubble['visible']:
            return
        
        text = self.speech_bubble['text']
        bubble_x = self.character_x + self.character_size + 20
        bubble_y = self.character_y - 50
        
        # Calculate text size
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2
        (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
        
        # Speech bubble background
        padding = 10
        bubble_width = text_width + 2 * padding
        bubble_height = text_height + 2 * padding
        
        # Bubble rectangle
        cv2.rectangle(overlay,
                     (bubble_x, bubble_y - bubble_height),
                     (bubble_x + bubble_width, bubble_y),
                     (255, 255, 255), -1)
        
        # Bubble border
        cv2.rectangle(overlay,
                     (bubble_x, bubble_y - bubble_height),
                     (bubble_x + bubble_width, bubble_y),
                     (0, 0, 0), 2)
        
        # Speech bubble tail
        tail_points = np.array([
            [bubble_x, bubble_y],
            [bubble_x - 15, bubble_y + 10],
            [bubble_x + 15, bubble_y + 10]
        ], np.int32)
        cv2.fillPoly(overlay, [tail_points], (255, 255, 255))
        cv2.polylines(overlay, [tail_points], True, (0, 0, 0), 2)
        
        # Text
        text_x = bubble_x + padding
        text_y = bubble_y - padding
        cv2.putText(overlay, text, (text_x, text_y), font, font_scale, (0, 0, 0), thickness)
    
    def set_character_position(self, x: int, y: int):
        """Set character position"""
        self.character_x = x
        self.character_y = y
    
    def set_character_size(self, size: int):
        """Set character size"""
        self.character_size = size
    
    def set_expression(self, expression: str, duration: float = 2.0):
        """Manually set character expression"""
        self.current_expression = expression
        self.expression_start_time = time.time()
        self.expression_duration = duration
    
    def show_speech_bubble(self, text: str, duration: float = 3.0):
        """Show speech bubble with text"""
        self.speech_bubble['visible'] = True
        self.speech_bubble['text'] = text
        self.speech_bubble['start_time'] = time.time()
        self.speech_bubble['duration'] = duration
    
    def hide_speech_bubble(self):
        """Hide speech bubble"""
        self.speech_bubble['visible'] = False
    
    def get_character_info(self) -> Dict:
        """Get current character information"""
        return {
            'position': (self.character_x, self.character_y),
            'size': self.character_size,
            'current_animation': self.current_animation,
            'current_expression': self.current_expression,
            'speech_bubble_visible': self.speech_bubble['visible'],
            'speech_bubble_text': self.speech_bubble['text']
        }

# Global instance
character_overlay = CharacterOverlay()
