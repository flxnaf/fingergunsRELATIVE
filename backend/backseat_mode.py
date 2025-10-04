"""
Backseat Gamer Mode Implementation
Virtual character that provides live commentary and tactical advice
"""

import time
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
from config import config
from ai_commentary import gemini_commentary
from voice_synthesis import voice_synthesis
from character_overlay import character_overlay

class BackseatGamerMode:
    """Backseat gamer mode with AI-powered commentary"""
    
    def __init__(self):
        self.is_active = False
        self.commentary_frequency = config.backseat_commentary_frequency
        self.last_commentary_time = 0
        self.encouragement_threshold = config.backseat_encouragement_threshold
        
        # Performance tracking
        self.performance_history = []
        self.gesture_accuracy_history = []
        self.recent_actions = []
        self.action_timestamps = []
        
        # Commentary types and their frequencies
        self.commentary_types = {
            'encouragement': 0.3,  # 30% encouragement
            'strategy': 0.25,      # 25% strategy advice
            'gesture_feedback': 0.25,  # 25% gesture feedback
            'general_banter': 0.2   # 20% general banter
        }
        
        # Character state
        self.character_mood = 'neutral'
        self.mood_change_time = 0
        
        print("✓ Backseat Gamer Mode initialized")
    
    def start_backseat_mode(self):
        """Start backseat gamer mode"""
        self.is_active = True
        self.last_commentary_time = time.time()
        self.performance_history = []
        self.gesture_accuracy_history = []
        self.recent_actions = []
        self.action_timestamps = []
        self.character_mood = 'excited'
        
        # Welcome message
        welcome_text = "Hey there! I'm your backseat gamer! Ready to help you dominate with gesture controls!"
        print(f"BACKSEAT GAMER: {welcome_text}")
        
        # Show character with excited expression
        character_overlay.set_expression('excited', 3.0)
        character_overlay.show_speech_bubble(welcome_text, 4.0)
        
        if voice_synthesis.is_available():
            voice_synthesis.speak_backseat_commentary(welcome_text)
        
        print("Backseat Gamer Mode activated! Your AI coach is ready to help!")
    
    def stop_backseat_mode(self):
        """Stop backseat gamer mode"""
        self.is_active = False
        
        # Farewell message
        farewell_text = "Great playing with you! Your gesture control skills are getting better!"
        print(f"BACKSEAT GAMER: {farewell_text}")
        
        character_overlay.set_expression('excited', 2.0)
        character_overlay.show_speech_bubble(farewell_text, 3.0)
        
        if voice_synthesis.is_available():
            voice_synthesis.speak_backseat_commentary(farewell_text)
        
        print("Backseat Gamer Mode deactivated.")
    
    def update_backseat_mode(self, gesture_data: Dict, frame: np.ndarray) -> str:
        """
        Update backseat gamer mode based on current game state
        Returns: status message
        """
        if not self.is_active:
            return "Backseat mode inactive"
        
        current_time = time.time()
        
        # Update performance tracking
        self._update_performance_tracking(gesture_data, current_time)
        
        # Generate game state for AI
        game_state = self._generate_game_state(gesture_data)
        
        # Update character based on performance
        self._update_character_mood(game_state)
        
        # Generate commentary if it's time
        commentary = ""
        if current_time - self.last_commentary_time >= self.commentary_frequency:
            commentary = self._generate_commentary(game_state)
            self.last_commentary_time = current_time
        
        # Update character overlay
        character_overlay.update_character(game_state, commentary)
        
        # Draw character on frame
        character_overlay.draw_character(frame)
        
        # Status message
        performance_score = game_state.get('performance_score', 0.0)
        mood_text = f"Mood: {self.character_mood}"
        performance_text = f"Performance: {performance_score:.1f}/10"
        
        return f"Backseat Active | {mood_text} | {performance_text}"
    
    def _update_performance_tracking(self, gesture_data: Dict, current_time: float):
        """Update performance tracking metrics"""
        # Track recent actions
        current_action = self._determine_current_action(gesture_data)
        if current_action and current_action != 'idle':
            self.recent_actions.append(current_action)
            self.action_timestamps.append(current_time)
        
        # Keep only recent actions (last 30 seconds)
        cutoff_time = current_time - 30
        filtered_actions = []
        filtered_timestamps = []
        
        for action, timestamp in zip(self.recent_actions, self.action_timestamps):
            if timestamp > cutoff_time:
                filtered_actions.append(action)
                filtered_timestamps.append(timestamp)
        
        self.recent_actions = filtered_actions
        self.action_timestamps = filtered_timestamps
        
        # Calculate gesture accuracy
        gesture_accuracy = self._calculate_gesture_accuracy(gesture_data)
        self.gesture_accuracy_history.append(gesture_accuracy)
        
        # Keep only last 100 measurements
        if len(self.gesture_accuracy_history) > 100:
            self.gesture_accuracy_history = self.gesture_accuracy_history[-100:]
        
        # Calculate overall performance score
        performance_score = self._calculate_performance_score(gesture_data)
        self.performance_history.append(performance_score)
        
        if len(self.performance_history) > 50:
            self.performance_history = self.performance_history[-50:]
    
    def _determine_current_action(self, gesture_data: Dict) -> str:
        """Determine current player action based on gesture data"""
        wasd_states = gesture_data.get('wasd_states', {})
        gun_active = gesture_data.get('gun_active', False)
        is_shooting = gesture_data.get('is_shooting', False)
        tongue_out = gesture_data.get('tongue_out', False)
        left_action = gesture_data.get('left_action')
        
        if is_shooting and gun_active:
            return 'shooting'
        elif gun_active:
            return 'aiming'
        elif any(wasd_states.values()):
            return 'moving'
        elif tongue_out:
            return 'spraying'
        elif left_action == 'ctrl':
            return 'crouching'
        elif left_action == 'space':
            return 'jumping'
        else:
            return 'idle'
    
    def _calculate_gesture_accuracy(self, gesture_data: Dict) -> float:
        """Calculate current gesture accuracy"""
        accuracy_components = []
        
        # Gun gesture accuracy
        gun_active = gesture_data.get('gun_active', False)
        if gun_active:
            accuracy_components.append(1.0)
        else:
            accuracy_components.append(0.0)
        
        # WASD accuracy (smooth movement)
        wasd_states = gesture_data.get('wasd_states', {})
        if any(wasd_states.values()):
            # Check for smooth transitions
            accuracy_components.append(0.8)
        else:
            accuracy_components.append(0.5)  # Neutral state
        
        # Tongue detection accuracy
        tongue_out = gesture_data.get('tongue_out', False)
        if tongue_out:
            accuracy_components.append(1.0)
        else:
            accuracy_components.append(0.5)
        
        return sum(accuracy_components) / len(accuracy_components)
    
    def _calculate_performance_score(self, gesture_data: Dict) -> float:
        """Calculate overall performance score (0-10)"""
        score = 5.0  # Base score
        
        # Gesture accuracy component
        avg_accuracy = sum(self.gesture_accuracy_history[-10:]) / min(10, len(self.gesture_accuracy_history))
        score += avg_accuracy * 2.0
        
        # Action variety component
        unique_actions = len(set(self.recent_actions[-10:]))
        score += min(unique_actions * 0.5, 2.0)
        
        # Smoothness component (based on action transitions)
        if len(self.recent_actions) > 1:
            transitions = len(set(zip(self.recent_actions[:-1], self.recent_actions[1:])))
            score += min(transitions * 0.2, 1.0)
        
        return min(max(score, 0.0), 10.0)
    
    def _generate_game_state(self, gesture_data: Dict) -> Dict:
        """Generate game state for AI commentary"""
        current_action = self._determine_current_action(gesture_data)
        performance_score = self._calculate_performance_score(gesture_data)
        gesture_accuracy = self._calculate_gesture_accuracy(gesture_data)
        
        return {
            'current_action': current_action,
            'performance_score': performance_score,
            'gesture_accuracy': gesture_accuracy,
            'recent_actions': self.recent_actions[-5:],  # Last 5 actions
            'wasd_states': gesture_data.get('wasd_states', {}),
            'gun_active': gesture_data.get('gun_active', False),
            'is_shooting': gesture_data.get('is_shooting', False),
            'character_mood': self.character_mood
        }
    
    def _update_character_mood(self, game_state: Dict):
        """Update character mood based on performance"""
        performance_score = game_state.get('performance_score', 5.0)
        gesture_accuracy = game_state.get('gesture_accuracy', 0.5)
        
        new_mood = 'neutral'
        
        if performance_score > 8.0 or gesture_accuracy > 0.9:
            new_mood = 'excited'
        elif performance_score > 6.0 or gesture_accuracy > 0.7:
            new_mood = 'happy'
        elif performance_score < 3.0 or gesture_accuracy < 0.4:
            new_mood = 'concerned'
        else:
            new_mood = 'neutral'
        
        if new_mood != self.character_mood:
            self.character_mood = new_mood
            character_overlay.set_expression(new_mood, 2.0)
    
    def _generate_commentary(self, game_state: Dict) -> str:
        """Generate AI commentary based on game state"""
        # Choose commentary type based on probabilities
        commentary_type = self._choose_commentary_type(game_state)
        
        if commentary_type == 'encouragement':
            return self._generate_encouragement_commentary(game_state)
        elif commentary_type == 'strategy':
            return self._generate_strategy_commentary(game_state)
        elif commentary_type == 'gesture_feedback':
            return self._generate_gesture_feedback_commentary(game_state)
        else:  # general_banter
            return self._generate_general_banter_commentary(game_state)
    
    def _choose_commentary_type(self, game_state: Dict) -> str:
        """Choose commentary type based on probabilities and context"""
        import random
        
        # Adjust probabilities based on game state
        probabilities = self.commentary_types.copy()
        
        performance_score = game_state.get('performance_score', 5.0)
        
        if performance_score > 8.0:
            # High performance - more encouragement
            probabilities['encouragement'] = 0.5
            probabilities['general_banter'] = 0.3
        elif performance_score < 4.0:
            # Low performance - more strategy advice
            probabilities['strategy'] = 0.4
            probabilities['gesture_feedback'] = 0.3
        
        # Choose based on weighted probabilities
        types = list(probabilities.keys())
        weights = list(probabilities.values())
        
        return random.choices(types, weights=weights)[0]
    
    def _generate_encouragement_commentary(self, game_state: Dict) -> str:
        """Generate encouraging commentary"""
        if gemini_commentary.is_available():
            return gemini_commentary.generate_backseat_commentary(game_state)
        else:
            return self._get_fallback_encouragement()
    
    def _generate_strategy_commentary(self, game_state: Dict) -> str:
        """Generate strategy advice"""
        if gemini_commentary.is_available():
            return gemini_commentary.generate_strategy_advice(game_state)
        else:
            return self._get_fallback_strategy()
    
    def _generate_gesture_feedback_commentary(self, game_state: Dict) -> str:
        """Generate gesture feedback commentary"""
        gesture_accuracy = game_state.get('gesture_accuracy', 0.5)
        current_action = game_state.get('current_action', 'idle')
        
        if gesture_accuracy > 0.8:
            return f"Nice {current_action}! Your gesture control is spot on!"
        elif gesture_accuracy > 0.6:
            return f"Good {current_action}! Keep practicing those gestures!"
        else:
            return f"Try to make your {current_action} gesture more deliberate!"
    
    def _generate_general_banter_commentary(self, game_state: Dict) -> str:
        """Generate general banter commentary"""
        if gemini_commentary.is_available():
            return gemini_commentary.generate_backseat_commentary(game_state)
        else:
            return self._get_fallback_banter()
    
    def _get_fallback_encouragement(self) -> str:
        """Fallback encouragement when AI is unavailable"""
        import random
        encouragements = [
            "You're doing great with those gesture controls!",
            "Nice moves! Your skills are improving!",
            "Keep it up! You're mastering gesture gaming!",
            "Awesome! I love watching you play!",
            "Your gesture control is getting really smooth!",
            "Excellent! You're becoming a gesture control pro!"
        ]
        return random.choice(encouragements)
    
    def _get_fallback_strategy(self) -> str:
        """Fallback strategy advice when AI is unavailable"""
        import random
        strategies = [
            "Try using your head movements for better positioning!",
            "Remember to use your body lean for quick strafing!",
            "Your gesture controls give you an advantage - use them!",
            "Practice smooth transitions between gestures!",
            "Use your left hand gestures for tactical advantages!",
            "Your gesture control lets you react faster than keyboard users!"
        ]
        return random.choice(strategies)
    
    def _get_fallback_banter(self) -> str:
        """Fallback banter when AI is unavailable"""
        import random
        banter = [
            "This gesture control setup is so cool!",
            "I wish I could play like this!",
            "You're making gesture gaming look easy!",
            "This is the future of gaming right here!",
            "I love watching you play with gesture controls!",
            "You're a gesture control pioneer!"
        ]
        return random.choice(banter)
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics"""
        if not self.performance_history:
            return {}
        
        avg_performance = sum(self.performance_history) / len(self.performance_history)
        avg_accuracy = sum(self.gesture_accuracy_history) / len(self.gesture_accuracy_history)
        
        return {
            'average_performance': avg_performance,
            'average_accuracy': avg_accuracy,
            'total_actions': len(self.recent_actions),
            'unique_actions': len(set(self.recent_actions)),
            'character_mood': self.character_mood,
            'session_duration': time.time() - self.last_commentary_time + self.commentary_frequency
        }
    
    def is_active_mode(self) -> bool:
        """Check if backseat mode is active"""
        return self.is_active

# Global instance
backseat_mode = BackseatGamerMode()
