"""
AI Commentary System using Gemini API
Provides intelligent commentary and tips for CS:GO gesture control
"""

import google.generativeai as genai
import json
import time
from typing import Dict, List, Optional, Any
from config import config

class GeminiCommentary:
    """Gemini AI-powered commentary system"""
    
    def __init__(self):
        self.model = None
        self.last_commentary_time = 0
        self.commentary_history = []
        
        # Initialize Gemini
        if config.gemini_api_key:
            genai.configure(api_key=config.gemini_api_key)
            self.model = genai.GenerativeModel(config.gemini_model)
            print("✓ Gemini AI initialized successfully")
        else:
            print("✗ Gemini API key not found - commentary disabled")
    
    def generate_tutorial_tip(self, gesture_name: str, performance_score: float) -> str:
        """Generate personalized tutorial tips based on gesture performance"""
        if not self.model:
            return self._get_fallback_tutorial_tip(gesture_name, performance_score)
        
        try:
            prompt = f"""
            You are a CS:GO gesture control tutor. The player is learning the "{gesture_name}" gesture.
            Their performance score is {performance_score:.2f} (0.0 = poor, 1.0 = perfect).
            
            Give a brief, encouraging tip (1-2 sentences) to help them improve this specific gesture.
            Focus on technique and be supportive.
            
            Response format: Just the tip text, no extra formatting.
            """
            
            response = self.model.generate_content(prompt)
            tip = response.text.strip()
            
            # Cache the tip
            self.commentary_history.append({
                'type': 'tutorial_tip',
                'gesture': gesture_name,
                'content': tip,
                'timestamp': time.time()
            })
            
            return tip
            
        except Exception as e:
            print(f"Error generating tutorial tip: {e}")
            return self._get_fallback_tutorial_tip(gesture_name, performance_score)
    
    def generate_backseat_commentary(self, game_state: Dict[str, Any]) -> str:
        """Generate backseat gamer commentary based on current game state"""
        if not self.model:
            return self._get_fallback_backseat_commentary(game_state)
        
        try:
            # Prepare game state context
            context = self._format_game_state(game_state)
            
            prompt = f"""
            You are a funny, enthusiastic backseat gamer watching someone play CS:GO using gesture controls.
            Current game situation: {context}
            
            Give entertaining commentary (1-2 sentences) that's:
            - Funny and engaging
            - Related to gesture control or CS:GO
            - Encouraging but playful
            - Not too long
            
            Response format: Just the commentary text, no extra formatting.
            """
            
            response = self.model.generate_content(prompt)
            commentary = response.text.strip()
            
            # Cache the commentary
            self.commentary_history.append({
                'type': 'backseat_commentary',
                'content': commentary,
                'timestamp': time.time(),
                'game_state': game_state
            })
            
            return commentary
            
        except Exception as e:
            print(f"Error generating backseat commentary: {e}")
            return self._get_fallback_backseat_commentary(game_state)
    
    def generate_strategy_advice(self, game_state: Dict[str, Any]) -> str:
        """Generate tactical CS:GO strategy advice"""
        if not self.model:
            return self._get_fallback_strategy_advice()
        
        try:
            context = self._format_game_state(game_state)
            
            prompt = f"""
            You are a CS:GO strategy expert. Current situation: {context}
            
            Give brief tactical advice (1-2 sentences) for this situation.
            Focus on positioning, economy, or team coordination.
            
            Response format: Just the advice text, no extra formatting.
            """
            
            response = self.model.generate_content(prompt)
            advice = response.text.strip()
            
            self.commentary_history.append({
                'type': 'strategy_advice',
                'content': advice,
                'timestamp': time.time(),
                'game_state': game_state
            })
            
            return advice
            
        except Exception as e:
            print(f"Error generating strategy advice: {e}")
            return self._get_fallback_strategy_advice()
    
    def _format_game_state(self, game_state: Dict[str, Any]) -> str:
        """Format game state for AI prompts"""
        formatted = []
        
        if 'current_action' in game_state:
            formatted.append(f"Player is {game_state['current_action']}")
        
        if 'gesture_accuracy' in game_state:
            accuracy = game_state['gesture_accuracy']
            formatted.append(f"Gesture accuracy: {accuracy:.1%}")
        
        if 'recent_actions' in game_state:
            actions = ', '.join(game_state['recent_actions'][-3:])
            formatted.append(f"Recent actions: {actions}")
        
        if 'performance_score' in game_state:
            score = game_state['performance_score']
            formatted.append(f"Overall performance: {score:.1f}/10")
        
        return '; '.join(formatted) if formatted else "Starting the game"
    
    def _get_fallback_tutorial_tip(self, gesture_name: str, performance_score: float) -> str:
        """Fallback tutorial tips when AI is unavailable"""
        tips = {
            'gun_gesture': [
                "Keep your index finger straight and firm!",
                "Make sure your other fingers are curled tight.",
                "Practice the gun gesture until it feels natural!"
            ],
            'thumb_shooting': [
                "Lower your thumb slowly for precise shooting!",
                "Keep your index finger steady while shooting.",
                "Try to maintain the gun gesture while shooting."
            ],
            'head_movement': [
                "Move your head smoothly for better control!",
                "Practice tilting forward and backward.",
                "Keep your movements controlled and deliberate."
            ],
            'body_leaning': [
                "Lean from your torso, not just your shoulders!",
                "Practice shifting your weight left and right.",
                "Keep your movements balanced and controlled."
            ],
            'tongue_spray': [
                "Stick out your tongue clearly for the spray!",
                "Make sure your mouth opens enough to trigger.",
                "Practice the tongue gesture - it's fun!"
            ],
            'left_hand_crouch': [
                "Show one finger clearly on your left hand!",
                "Make sure your palm faces the camera.",
                "Practice switching between gestures quickly."
            ],
            'left_hand_jump': [
                "Show four fingers down for jumping!",
                "Keep your thumb up when jumping.",
                "Practice the jump gesture for quick movements."
            ]
        }
        
        gesture_tips = tips.get(gesture_name, ["Keep practicing! You're doing great!"])
        
        # Select tip based on performance
        if performance_score < 0.3:
            return gesture_tips[0]  # Basic tip
        elif performance_score < 0.7:
            return gesture_tips[1] if len(gesture_tips) > 1 else gesture_tips[0]  # Intermediate tip
        else:
            return gesture_tips[2] if len(gesture_tips) > 2 else gesture_tips[-1]  # Advanced tip
    
    def _get_fallback_backseat_commentary(self, game_state: Dict[str, Any]) -> str:
        """Fallback backseat commentary when AI is unavailable"""
        commentaries = [
            "Nice gesture control! You're getting the hang of this!",
            "That was a smooth move! Keep it up!",
            "I love watching you play with gesture controls!",
            "Your aim is getting better with each shot!",
            "Great job using those gesture controls!",
            "This is so cool - gesture-controlled CS:GO!",
            "You're mastering the art of gesture gaming!",
            "That was an epic play with gesture controls!",
            "I'm impressed by your gesture accuracy!",
            "Keep practicing - you're doing amazing!"
        ]
        
        import random
        return random.choice(commentaries)
    
    def _get_fallback_strategy_advice(self) -> str:
        """Fallback strategy advice when AI is unavailable"""
        advice = [
            "Try to control the map angles with your gesture movements!",
            "Remember to check your corners with smooth head movements!",
            "Use your gesture controls to maintain good crosshair placement!",
            "Practice your gesture transitions for faster reactions!",
            "Keep your movements controlled and deliberate!",
            "Use your body lean for precise positioning!",
            "Remember to use your left hand gestures for utility!",
            "Practice makes perfect with gesture controls!",
            "Stay focused and keep your gestures smooth!",
            "Your gesture control is your advantage - use it wisely!"
        ]
        
        import random
        return random.choice(advice)
    
    def get_commentary_history(self, limit: int = 10) -> List[Dict]:
        """Get recent commentary history"""
        return self.commentary_history[-limit:]
    
    def clear_history(self):
        """Clear commentary history"""
        self.commentary_history = []
    
    def is_available(self) -> bool:
        """Check if AI commentary is available"""
        return self.model is not None

# Global instance
gemini_commentary = GeminiCommentary()
