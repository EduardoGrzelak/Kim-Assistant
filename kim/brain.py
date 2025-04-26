import openai
import os
import json
from dotenv import load_dotenv

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
    answer = openai.ChatCompletion.create(
        model="gpt-4.0-turbo",  # Modelo que você quer usar
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    
    # Agora pegamos a resposta como uma string normal (não JSON)
    new_profile = answer['choices'][0]['message']['content']
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
    answer = openai.ChatCompletion.create(
        model="gpt-4.0-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    return answer['choices'][0]['message']['content']
