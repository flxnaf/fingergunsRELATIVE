"""
Voice Synthesis using ElevenLabs API
Converts AI-generated text to speech for tutorial and backseat gamer modes
"""

import requests
import pygame
import io
import threading
import time
from typing import Optional, Callable
from config import config

class VoiceSynthesis:
    """ElevenLabs voice synthesis system"""
    
    def __init__(self):
        self.api_key = config.elevenlabs_api_key
        self.voice_id = config.elevenlabs_voice_id
        self.base_url = "https://api.elevenlabs.io/v1"
        
        # Initialize pygame mixer for audio playback
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.audio_available = True
            print("✓ Audio system initialized")
        except Exception as e:
            print(f"✗ Audio initialization failed: {e}")
            self.audio_available = False
        
        # Audio queue for managing multiple voice clips
        self.audio_queue = []
        self.is_playing = False
        self.current_audio = None
        
        # Check API availability
        if self.api_key:
            print("✓ ElevenLabs API key configured")
        else:
            print("✗ ElevenLabs API key not found - voice synthesis disabled")
    
    def speak_text(self, text: str, voice_id: Optional[str] = None, callback: Optional[Callable] = None):
        """Convert text to speech and play it"""
        if not self.audio_available or not self.api_key:
            print(f"Voice: {text}")  # Fallback to console output
            if callback:
                callback()
            return
        
        # Use provided voice_id or default
        voice = voice_id or self.voice_id
        
        # Add to queue for processing
        audio_request = {
            'text': text,
            'voice_id': voice,
            'callback': callback
        }
        
        self.audio_queue.append(audio_request)
        
        # Start processing if not already playing
        if not self.is_playing:
            self._process_audio_queue()
    
    def _process_audio_queue(self):
        """Process the audio queue in a separate thread"""
        if not self.audio_queue:
            return
        
        self.is_playing = True
        
        def process_queue():
            while self.audio_queue:
                audio_request = self.audio_queue.pop(0)
                
                try:
                    # Generate audio from ElevenLabs
                    audio_data = self._generate_audio(
                        audio_request['text'],
                        audio_request['voice_id']
                    )
                    
                    if audio_data:
                        # Play the audio
                        self._play_audio(audio_data)
                        
                        # Call callback if provided
                        if audio_request['callback']:
                            audio_request['callback']()
                    
                except Exception as e:
                    print(f"Error processing audio: {e}")
                    # Fallback to console output
                    print(f"Voice: {audio_request['text']}")
            
            self.is_playing = False
        
        # Start processing in background thread
        thread = threading.Thread(target=process_queue, daemon=True)
        thread.start()
    
    def _generate_audio(self, text: str, voice_id: str) -> Optional[bytes]:
        """Generate audio from text using ElevenLabs API"""
        try:
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            data = {
                "text": text,
                "model_id": config.elevenlabs_model,
                "voice_settings": {
                    "stability": config.elevenlabs_stability,
                    "similarity_boost": config.elevenlabs_similarity_boost
                }
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return response.content
            else:
                print(f"ElevenLabs API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error generating audio: {e}")
            return None
    
    def _play_audio(self, audio_data: bytes):
        """Play audio data using pygame"""
        try:
            # Create audio stream from bytes
            audio_stream = io.BytesIO(audio_data)
            
            # Load and play audio
            sound = pygame.mixer.Sound(audio_stream)
            sound.set_volume(config.audio_volume)
            
            # Play and wait for completion
            channel = sound.play()
            
            # Wait for audio to finish playing
            while channel.get_busy():
                time.sleep(0.1)
                
        except Exception as e:
            print(f"Error playing audio: {e}")
    
    def speak_tutorial_tip(self, tip: str):
        """Speak a tutorial tip with appropriate voice settings"""
        self.speak_text(tip, callback=lambda: print("Tutorial tip delivered"))
    
    def speak_backseat_commentary(self, commentary: str):
        """Speak backseat gamer commentary with appropriate voice settings"""
        self.speak_text(commentary, callback=lambda: print("Backseat commentary delivered"))
    
    def speak_strategy_advice(self, advice: str):
        """Speak strategy advice with appropriate voice settings"""
        self.speak_text(advice, callback=lambda: print("Strategy advice delivered"))
    
    def stop_all_audio(self):
        """Stop all current audio playback"""
        try:
            pygame.mixer.stop()
            self.audio_queue.clear()
            self.is_playing = False
        except Exception as e:
            print(f"Error stopping audio: {e}")
    
    def set_volume(self, volume: float):
        """Set audio volume (0.0 to 1.0)"""
        config.audio_volume = max(0.0, min(1.0, volume))
    
    def is_available(self) -> bool:
        """Check if voice synthesis is available"""
        return self.audio_available and bool(self.api_key)
    
    def get_available_voices(self) -> list:
        """Get list of available voices from ElevenLabs"""
        if not self.api_key:
            return []
        
        try:
            url = f"{self.base_url}/voices"
            headers = {"xi-api-key": self.api_key}
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                voices_data = response.json()
                return voices_data.get('voices', [])
            else:
                print(f"Error fetching voices: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error fetching available voices: {e}")
            return []
    
    def test_voice(self, text: str = "Hello! This is a test of the voice synthesis system."):
        """Test the voice synthesis system"""
        print("Testing voice synthesis...")
        self.speak_text(text, callback=lambda: print("Voice test completed"))

# Global instance
voice_synthesis = VoiceSynthesis()

# Example usage
if __name__ == "__main__":
    voice = VoiceSynthesis()
    
    if voice.is_available():
        print("Voice synthesis is available!")
        voice.test_voice()
        
        # Test different types of messages
        time.sleep(2)
        voice.speak_tutorial_tip("Keep your index finger straight for the gun gesture!")
        
        time.sleep(3)
        voice.speak_backseat_commentary("Nice shot! Your gesture control is improving!")
        
    else:
        print("Voice synthesis is not available. Check your API key and audio system.")
