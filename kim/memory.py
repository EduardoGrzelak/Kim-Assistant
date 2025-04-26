import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

class MemoryManager:
    def __init__(self):
        self.memory_dir = os.path.join(os.path.dirname(__file__), 'memory')
        self.profile_path = os.path.join(self.memory_dir, 'profile.json')
        self.conversation_path = os.path.join(self.memory_dir, 'conversation.json')
        self._ensure_memory_directory()
        
        # Initialize with default profile structure
        self.default_profile = {
            "personal": {
                "name": None,
                "preferred_name": None,
                "timezone": "Europe/Berlin"
            },
            "schedule": {
                "work_hours": {
                    "start": "09:00",
                    "end": "18:00",
                    "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
                },
                "break_preferences": {
                    "lunch_time": "12:00-13:00",
                    "short_breaks": ["11:00", "15:00"]
                }
            },
            "preferences": {
                "meeting_duration": 60,  # minutes
                "buffer_time": 15,  # minutes between events
                "preferred_meeting_times": ["10:00-12:00", "14:00-16:00"],
                "default_event_duration": 60  # Added new field
            },
            "responsibilities": []
        }

    def _ensure_memory_directory(self):
        """Create memory directory if it doesn't exist"""
        Path(self.memory_dir).mkdir(exist_ok=True)

    def load_profile(self) -> Dict:
        """Load user profile with default fallback values"""
        try:
            if os.path.exists(self.profile_path):
                with open(self.profile_path, 'r', encoding='utf-8') as f:
                    profile = json.load(f)
                    # Validate loaded profile structure
                    if isinstance(profile, dict):
                        return self._deep_merge(self.default_profile, profile)
        except (json.JSONDecodeError, TypeError, OSError) as e:
            print(f"⚠️ Profile load error: {str(e)}")
        return self.default_profile.copy()

    def load_conversation(self) -> List[Dict]:
        """Load conversation history with validation"""
        try:
            if os.path.exists(self.conversation_path):
                with open(self.conversation_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
                    print("⚠️ Conversation data is not a list, initializing new one")
        except (json.JSONDecodeError, TypeError, OSError) as e:
            print(f"⚠️ Conversation load error: {str(e)}")
        return []

    def save_profile(self, profile: Dict):
        """Save profile with error handling"""
        try:
            with open(self.profile_path, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=4, ensure_ascii=False)
        except (OSError, TypeError) as e:
            print(f"⚠️ Profile save error: {str(e)}")

    def save_conversation(self, conversation: List[Dict]):
        """Save conversation history with validation"""
        try:
            if not isinstance(conversation, list):
                print("⚠️ Conversation data is not a list, not saving")
                return
                
            with open(self.conversation_path, 'w', encoding='utf-8') as f:
                json.dump(conversation, f, indent=4, ensure_ascii=False)
        except (OSError, TypeError) as e:
            print(f"⚠️ Conversation save error: {str(e)}")

    def update_profile_from_conversation(self, user_input: str, current_profile: Dict) -> Dict:
        """Update profile from conversation with better parsing"""
        changes = {}
        input_lower = user_input.lower()
        
        # Enhanced name detection
        if any(phrase in input_lower for phrase in ["my name is", "i'm called", "call me"]):
            for phrase in ["my name is", "i'm called", "call me"]:
                if phrase in input_lower:
                    name = user_input.split(phrase)[-1].strip(" .")
                    if name and name != current_profile["personal"]["name"]:
                        changes["name"] = name
                        current_profile["personal"]["name"] = name
                        break
        
        # Enhanced schedule detection
        schedule_phrases = ["i work", "my hours", "available from"]
        if any(phrase in input_lower for phrase in schedule_phrases):
            time_parts = []
            if "from" in input_lower and "to" in input_lower:
                try:
                    time_part = input_lower.split("from")[-1]
                    start_end = time_part.split("to")
                    if len(start_end) == 2:
                        start = start_end[0].strip()
                        end = start_end[1].split()[0].strip()
                        if start and end:
                            changes["work_hours"] = {"start": start, "end": end}
                            current_profile["schedule"]["work_hours"].update({
                                "start": start,
                                "end": end
                            })
                except (IndexError, AttributeError):
                    pass
        
        # Enhanced responsibility detection
        responsibility_phrases = ["need to", "have to", "must", "should", "i'll", "i will"]
        if any(phrase in input_lower for phrase in responsibility_phrases):
            responsibility = self._extract_responsibility(user_input)
            if responsibility and responsibility not in current_profile["responsibilities"]:
                changes["new_responsibility"] = responsibility
                current_profile["responsibilities"].append(responsibility)
        
        if changes:
            self.save_profile(current_profile)
        
        return current_profile, changes

    def _extract_responsibility(self, text: str) -> Optional[str]:
        """Improved responsibility extraction"""
        phrases = [
            ("need to", 2),
            ("have to", 2),
            ("must", 1),
            ("should", 1),
            ("i'll", 1),
            ("i will", 2)
        ]
        
        for phrase, words in phrases:
            if phrase in text.lower():
                parts = text.lower().split(phrase)
                if len(parts) > 1:
                    responsibility = " ".join(parts[-1].strip().split()[:words])
                    return responsibility.capitalize()
        return None

    def _deep_merge(self, source: Dict, updates: Dict) -> Dict:
        """Safer deep merge implementation"""
        if not isinstance(source, dict) or not isinstance(updates, dict):
            return source
            
        for key, value in updates.items():
            if key in source and isinstance(value, dict) and isinstance(source[key], dict):
                source[key] = self._deep_merge(source[key], value)
            else:
                source[key] = value
        return source

    def get_contextual_prompt(self, profile: Dict, conversation: List[str]) -> str:
        """Generate context prompt with better formatting"""
        prompt_parts = [
            f"User Profile:",
            f"- Name: {profile['personal'].get('name', 'unknown')}",
            f"- Work Hours: {profile['schedule']['work_hours']['start']} to {profile['schedule']['work_hours']['end']}",
            f"- Preferred Meeting Duration: {profile['preferences']['meeting_duration']} minutes"
        ]
        
        # Add responsibilities if relevant
        last_convo = " ".join(conversation[-3:]).lower()
        if any(resp.lower() in last_convo for resp in profile["responsibilities"][-3:]):
            prompt_parts.append(f"- Recent Responsibilities: {', '.join(profile['responsibilities'][-3:])}")
        
        # Add scheduling preferences if discussing timing
        time_phrases = ["when", "time", "schedule", "meet", "appointment"]
        if any(phrase in last_convo for phrase in time_phrases):
            prompt_parts.append(f"- Preferred Times: {profile['preferences']['preferred_meeting_times']}")
        
        return "\n".join(prompt_parts)

    def clear_conversation(self):
        """Clear conversation history"""
        try:
            if os.path.exists(self.conversation_path):
                os.remove(self.conversation_path)
        except OSError as e:
            print(f"⚠️ Failed to clear conversation: {str(e)}")