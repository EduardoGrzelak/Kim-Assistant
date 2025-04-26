import openai
import os
import json
from dotenv import load_dotenv
from kim import calendar_api  

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def process_message(message, profile):
    prompt = f"""
You are Kim, a personal assistant

Current profile:
{profile}

User said:
"{message}"

Update the profile:
- Fill in and correct existing fields.
- If you notice new relevant information (such as preferred days, new activities, etc) create new categories.
- Remember, the profile is never complete, it evolves over time

Your answer:
"""
    # Usando o método correto para a versão 0.28 da biblioteca
    answer = openai.Completion.create(
        model="gpt-4",  # Modelo atualizado e recomendado
        prompt=prompt,  # Alterado de messages para prompt, pois é a forma correta na versão 0.28
        temperature=0.4
    )
    
    new_profile = answer['choices'][0]['text']  # 'text' ao invés de 'message'
    return new_profile  # Retornamos como string mesmo (não JSON)

def generate_question(current_profile, conversation_so_far):
    prompt = f"""
You are Kim, a very human and gentle personal assistant

Current profile:
{json.dumps(current_profile, indent=2)}

Conversation so far:
"{conversation_so_far}"
Your mission:
- Continuously enrich the user's profile.
- If the profile is empty, ask for basic information such as name, age and occupation.
- If there is data, investigate more: hobbies, interests, work schedule, boundaries, etc.
- In every new exchange, find ways to discover more things.
- Ask engaging questions ("That's awesome, tell me more about...").
- Never finalize the profile; it should grow and evolve along with the user.

Answer next what Kim should say
"""
    # Usando o método correto para a versão 0.28 da biblioteca
    answer = openai.Completion.create(
        model="gpt-4",
        prompt=prompt,  # Alterado de messages para prompt, pois é a forma correta na versão 0.28
        temperature=0.4
    )
    return answer['choices'][0]['text']  # 'text' ao invés de 'message'

def handle_calendar_commands(message, service):
    """
    Detect and handle calendar-related commands based on the user's message.
    """
    message_lower = message.lower()

    if "create event" in message_lower or "schedule event" in message_lower:
        return "To create an event, please provide the title, description, start, and end time."

    if "list events" in message_lower or "show my schedule" in message_lower:
        events = calendar_api.list_events(service)
        if not events:
            return "You have no upcoming events."
        event_list = "\n".join(
            [f"{event['summary']} at {event['start'].get('dateTime', event['start'].get('date'))}" for event in events]
        )
        return event_list

    if "delete event" in message_lower:
        return "Please specify the event ID you want to delete."

    return None
