from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime

# 📌 Authenticate with Google Calendar API
def authenticate_google_calendar():
    """
    Authenticates the Google Calendar API using service account credentials.
    Returns the service object to interact with Google Calendar.
    """
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    SERVICE_ACCOUNT_FILE = 'credentials.json'  # Ensure this file exists and contains your credentials

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('calendar', 'v3', credentials=credentials)
    return service

# 📅 List events in the calendar
def list_events(service):
    """
    Lists upcoming events from the Google Calendar starting from the current time.
    Returns a list of events.
    """
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # Current time in ISO 8601 format
    events_result = service.events().list(
        calendarId='primary',  # Using the primary calendar
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    return events

# ➕ Create event in the calendar
def create_event(service, summary, description, start_datetime, end_datetime):
    """
    Creates an event in Google Calendar with the provided details.
    Receives details like title, description, start and end times.
    """
    event = {
        'summary': summary,
        'description': description,
        'start': {'dateTime': start_datetime, 'timeZone': 'America/Sao_Paulo'},
        'end': {'dateTime': end_datetime, 'timeZone': 'America/Sao_Paulo'},
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    return event

# 🔁 Update an existing event
def update_event(service, event_id, new_summary=None, new_description=None, new_start=None, new_end=None):
    """
    Updates an existing event in Google Calendar, if the event has already been created.
    You can change the title, description, start and end times.
    """
    event = service.events().get(calendarId='primary', eventId=event_id).execute()

    if new_summary:
        event['summary'] = new_summary
    if new_description:
        event['description'] = new_description
    if new_start and new_end:
        event['start']['dateTime'] = new_start
        event['end']['dateTime'] = new_end

    updated_event = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
    return updated_event

# ❌ Delete an event
def delete_event(service, event_id):
    """
    Deletes an existing event based on the event ID.
    """
    service.events().delete(calendarId='primary', eventId=event_id).execute()

# 🗓️ Get details of a specific event
def get_event(service, event_id):
    """
    Retrieves the details of an event based on the event ID.
    Returns the event details.
    """
    event = service.events().get(calendarId='primary', eventId=event_id).execute()
    return event
