"""
Configuration file for CS:GO Gesture Control System
Contains API keys and settings for AI integration
"""

import os
from typing import Dict, Any

class Config:
    """Configuration class for API keys and settings"""
    
    def __init__(self):
        # API Keys - Load from environment variables for security
        self.gemini_api_key = os.getenv('GEMINI_API_KEY', '')
        self.elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY', '')
        
        # Gemini API Settings
        self.gemini_model = 'gemini-1.5-flash'
        self.gemini_temperature = 0.7
        self.gemini_max_tokens = 1000
        
        # ElevenLabs Settings
        self.elevenlabs_voice_id = 'pNInz6obpgDQGcFmaJgB'  # Default Adam voice
        self.elevenlabs_model = 'eleven_monolingual_v1'
        self.elevenlabs_stability = 0.75
        self.elevenlabs_similarity_boost = 0.75
        
        # Tutorial Mode Settings
        self.tutorial_gestures = [
            'gun_gesture',
            'thumb_shooting', 
            'head_movement',
            'body_leaning',
            'tongue_spray',
            'left_hand_crouch',
            'left_hand_jump'
        ]
        
        self.tutorial_difficulty_levels = ['beginner', 'intermediate', 'advanced']
        
        # Backseat Gamer Settings
        self.backseat_commentary_frequency = 10  # seconds between commentary
        self.backseat_character_style = 'anime'
        self.backseat_encouragement_threshold = 0.7  # performance threshold for encouragement
        
        # Audio Settings
        self.audio_volume = 0.8
        self.audio_enabled = True
        
        # Visual Settings
        self.overlay_opacity = 0.8
        self.character_animation_speed = 1.0
        
    def validate_api_keys(self) -> Dict[str, bool]:
        """Validate that required API keys are present"""
        return {
            'gemini': bool(self.gemini_api_key),
            'elevenlabs': bool(self.elevenlabs_api_key)
        }
    
    def get_tutorial_prompts(self) -> Dict[str, str]:
        """Get tutorial prompts for each gesture"""
        return {
            'gun_gesture': "Show me your gun gesture! Extend your index finger and curl the other three fingers.",
            'thumb_shooting': "Great! Now lower your thumb to shoot. Keep your index finger extended for aiming.",
            'head_movement': "Tilt your head forward for 'S', backward for 'W'. Try moving your head up and down.",
            'body_leaning': "Lean your body left for 'A', right for 'D'. Shift your torso to the sides.",
            'tongue_spray': "Stick out your tongue to spray! This will press the 'T' key for emotes.",
            'left_hand_crouch': "Show one finger down on your left hand to crouch (Ctrl key).",
            'left_hand_jump': "Show four fingers down on your left hand to jump (Space key)."
        }
    
    def get_backseat_prompts(self) -> Dict[str, str]:
        """Get backseat gamer commentary prompts"""
        return {
            'encouragement': "Give encouraging commentary about the player's performance",
            'strategy': "Provide tactical advice for CS:GO gameplay",
            'gesture_feedback': "Comment on the player's gesture execution",
            'general_banter': "Provide entertaining backseat gamer commentary"
        }

# Global config instance
config = Config()

# Example usage and setup instructions
if __name__ == "__main__":
    print("CS:GO Gesture Control Configuration")
    print("=" * 40)
    
    # Check API keys
    api_status = config.validate_api_keys()
    print(f"Gemini API Key: {'✓ Set' if api_status['gemini'] else '✗ Missing'}")
    print(f"ElevenLabs API Key: {'✓ Set' if api_status['elevenlabs'] else '✗ Missing'}")
    
    if not all(api_status.values()):
        print("\nTo set up API keys:")
        print("1. Get Gemini API key from: https://makersuite.google.com/app/apikey")
        print("2. Get ElevenLabs API key from: https://elevenlabs.io/")
        print("3. Set environment variables:")
        print("   export GEMINI_API_KEY='your_gemini_key_here'")
        print("   export ELEVENLABS_API_KEY='your_elevenlabs_key_here'")
    
    print(f"\nTutorial gestures: {len(config.tutorial_gestures)}")
    print(f"Character style: {config.backseat_character_style}")
    print(f"Audio enabled: {config.audio_enabled}")
