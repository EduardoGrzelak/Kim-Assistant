import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from openai import OpenAI
from typing import Dict, Optional, Union, List
from zoneinfo import ZoneInfo
from .calendar_api import (
    authenticate_google_calendar,
    list_events,
    create_event,
    update_event,
    delete_event,
    get_event
)

load_dotenv()

class CalendarBrain:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.calendar_service = authenticate_google_calendar()
        self.model = "gpt-4o"
        self.default_timezone = "Europe/Berlin"
        self.conversation_context = {}
        self.awaiting_confirmation = False
        self.system_prompt = f"""
        You are Kim, an AI calendar assistant. Follow these rules:
        
        1. For scheduling requests:
           - Extract ALL event details from natural language
           - Required fields: title, date, start_time, end_time
           - If any field is missing, respond with ONLY that missing field
           - Maintain context between messages
           - Default duration is 1 hour if end_time not specified
           - Timezone: {self.default_timezone}

        2. Title extraction examples:
           - "Meeting about project tomorrow 2pm" → title: "Project Meeting"
           - "Lunch with John Friday" → title: "Lunch with John"
           - "Team sync next week" → title: "Team Sync"

        3. Always return JSON with:
           {{
             "intent": "create|confirm|clarify|general",
             "message": "response text",
             "missing_fields": ["field1", "field2"],
             "data": {{
               "title": "extracted title",
               "date": "YYYY-MM-DD",
               "start": "HH:MM",
               "end": "HH:MM"
             }}
           }}
        """

    def process_conversation(self, user_input: str) -> Dict:
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                *self._get_conversation_context(),
                {"role": "user", "content": user_input}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            parsed = json.loads(response.choices[0].message.content)
            self._update_context(parsed, user_input)
            
            if parsed.get("intent") == "create":
                if parsed.get("missing_fields"):
                    missing = ", ".join(parsed["missing_fields"])
                    parsed["message"] = f"Could you please provide: {missing}?"
                else:
                    parsed["message"] = (
                        f"Confirm: Schedule '{parsed['data']['title']}' on "
                        f"{parsed['data']['date']} from {parsed['data']['start']} "
                        f"to {parsed['data']['end']}?"
                    )
                    self.awaiting_confirmation = True
            
            return parsed
            
        except Exception as e:
            print(f"Processing error: {str(e)}")
            return {
                "intent": "error",
                "message": "Sorry, I encountered an error. Please try again."
            }

    def _get_conversation_context(self) -> List[Dict]:
        context = []
        if self.conversation_context.get("title"):
            context.append(f"Current title: {self.conversation_context['title']}")
        if self.conversation_context.get("date"):
            context.append(f"Current date: {self.conversation_context['date']}")
        if self.conversation_context.get("start"):
            context.append(f"Current start time: {self.conversation_context['start']}")
        if self.conversation_context.get("end"):
            context.append(f"Current end time: {self.conversation_context['end']}")
        
        if context:
            return [{"role": "system", "content": "Current context:\n" + "\n".join(context)}]
        return []

    def _update_context(self, parsed: Dict, user_input: str):
        if parsed.get("intent") in ["create", "confirm"]:
            if "data" in parsed:
                for field in ["title", "date", "start", "end"]:
                    if field in parsed["data"]:
                        self.conversation_context[field] = parsed["data"][field]
                
                if "start" in parsed["data"] and "end" not in parsed["data"]:
                    try:
                        start = datetime.strptime(parsed["data"]["start"], "%H:%M")
                        end = (start + timedelta(hours=1)).strftime("%H:%M")
                        self.conversation_context["end"] = end
                    except ValueError:
                        pass

    def create_event_from_context(self) -> str:
        try:
            if not all(k in self.conversation_context for k in ["title", "date", "start", "end"]):
                return "❌ Missing information to schedule the event"
                
            start_time = self._convert_time_format(self.conversation_context["start"])
            end_time = self._convert_time_format(self.conversation_context["end"])
            
            start_dt = f"{self.conversation_context['date']}T{start_time}:00"
            end_dt = f"{self.conversation_context['date']}T{end_time}:00"
            
            event = create_event(
                service=self.calendar_service,
                summary=self.conversation_context["title"],
                start_datetime=start_dt,
                end_datetime=end_dt,
                timezone=self.default_timezone
            )
            
            self.conversation_context = {}
            self.awaiting_confirmation = False
            return f"✅ Scheduled: {event['summary']} on {event['start']['dateTime']}"
            
        except Exception as e:
            print(f"Event creation failed: {str(e)}")
            return "❌ Failed to create event. Please try again."

    def _convert_time_format(self, time_str: str) -> str:
        try:
            dt = datetime.strptime(time_str, "%I:%M %p")
            return dt.strftime("%H:%M")
        except ValueError:
            return time_str

    def handle_general_conversation(self, user_input: str) -> str:
        greetings = ["hi", "hello", "hey"]
        farewells = ["bye", "goodbye", "see you"]
        
        if any(g in user_input.lower() for g in greetings):
            return "Hello! How can I help with your calendar today?"
        elif any(f in user_input.lower() for f in farewells):
            return "Goodbye! Let me know if you need help later."
        return "I'm happy to help with your schedule. What would you like to do?"