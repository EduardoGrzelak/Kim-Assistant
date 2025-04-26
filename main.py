import time
from datetime import datetime
from typing import List, Dict
from kim.brain import CalendarBrain
from kim.memory import MemoryManager
from kim.voice_input import recognize_speech_from_microphone
from zoneinfo import ZoneInfo
import speech_recognition as sr

class KimAssistant:
    def __init__(self):
        try:
            self.memory = MemoryManager()
            self.brain = CalendarBrain()
            self.profile = self._safe_load_profile()
            self.conversation_history = self._safe_load_conversation()
            self.recognizer = sr.Recognizer()
            print("🔊 Kim initialized and ready!")
        except Exception as e:
            print(f"Initialization failed: {str(e)}")
            raise

    def _safe_load_profile(self) -> Dict:
        try:
            profile = self.memory.load_profile()
            return profile if isinstance(profile, dict) else {}
        except Exception as e:
            print(f"Profile load error: {str(e)}")
            return {}

    def _safe_load_conversation(self) -> List[Dict]:
        try:
            conv = self.memory.load_conversation()
            return conv if isinstance(conv, list) else []
        except Exception as e:
            print(f"Conversation load error: {str(e)}")
            return []

    def process_input(self, user_input: str) -> str:
        if not user_input:
            return "I didn't catch that. Could you repeat?"
        
        if self.brain.awaiting_confirmation:
            if "yes" in user_input.lower():
                result = self.brain.create_event_from_context()
                response = result if "✅" in result else "Event scheduled!"
            else:
                response = "Okay, let's start over."
                self.brain.conversation_context = {}
            
            self._update_conversation("user", user_input)
            self._update_conversation("assistant", response)
            return response
        
        response_data = self.brain.process_conversation(user_input)
        response = response_data.get("message", "How can I help?")
        
        self._update_conversation("user", user_input)
        self._update_conversation("assistant", response)
        return response

    def _update_conversation(self, role: str, content: str):
        try:
            self.conversation_history.append({
                "role": role,
                "content": content,
                "timestamp": datetime.now(ZoneInfo("Europe/Berlin")).isoformat()
            })
            self.memory.save_conversation(self.conversation_history[-10:])
        except Exception as e:
            print(f"Conversation update error: {str(e)}")

    def save_state(self):
        try:
            self.memory.save_profile(self.profile)
        except Exception as e:
            print(f"State save error: {str(e)}")

def main():
    assistant = KimAssistant()
    
    try:
        while True:
            print("\nListening... (say 'exit' to quit)")
            
            try:
                user_input = recognize_speech_from_microphone()
                if not user_input:
                    print("Kim: I didn't catch that. Could you repeat?")
                    continue
                    
                if any(exit_cmd in user_input.lower() for exit_cmd in ["exit", "quit"]):
                    print("Kim: Goodbye! Have a great day!")
                    break
                    
                print(f"You: {user_input}")
                response = assistant.process_input(user_input)
                print(f"Kim: {response}")
                
            except sr.UnknownValueError:
                print("Kim: I didn't understand that. Could you repeat?")
            except sr.RequestError as e:
                print(f"Kim: Speech recognition error: {str(e)}")
            except Exception as e:
                print(f"Kim: Error: {str(e)}")
                
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        assistant.save_state()

if __name__ == "__main__":
    main()