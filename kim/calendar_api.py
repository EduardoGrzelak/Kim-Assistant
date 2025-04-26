from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime
from typing import Dict, List, Optional

DEFAULT_TIMEZONE = 'Europe/Berlin'

def authenticate_google_calendar():
    """Authenticate with Google Calendar API with better error handling"""
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    SERVICE_ACCOUNT_FILE = 'credentials.json'

    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        return build('calendar', 'v3', credentials=credentials)
    except Exception as e:
        print(f"⚠️ Calendar authentication failed: {str(e)}")
        raise

def create_event(
    service,
    summary: str,
    start_datetime: str,
    end_datetime: str,
    description: str = "",
    timezone: str = DEFAULT_TIMEZONE
) -> Dict:
    """Create event with robust error handling"""
    try:
        # Validate time format
        if 'T' not in start_datetime or 'T' not in end_datetime:
            raise ValueError("Invalid time format - must include date and time")
            
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_datetime,
                'timeZone': timezone
            },
            'end': {
                'dateTime': end_datetime,
                'timeZone': timezone
            },
        }
        
        created_event = service.events().insert(
            calendarId='primary',
            body=event
        ).execute()
        
        return created_event
        
    except HttpError as e:
        print(f"⚠️ Google API error: {str(e)}")
        raise
    except Exception as e:
        print(f"⚠️ Event creation error: {str(e)}")
        raise

def list_events(service, max_results: int = 10) -> List[Dict]:
    """List events with error handling"""
    try:
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        return events_result.get('items', [])
    except Exception as e:
        print(f"⚠️ Event listing error: {str(e)}")
        return []

def update_event(
    service,
    event_id: str,
    summary: Optional[str] = None,
    start_datetime: Optional[str] = None,
    end_datetime: Optional[str] = None,
    description: Optional[str] = None,
    timezone: str = DEFAULT_TIMEZONE
) -> Dict:
    """Update an existing event"""
    try:
        # First get the existing event
        event = service.events().get(
            calendarId='primary',
            eventId=event_id
        ).execute()

        # Update only the fields that were provided
        if summary is not None:
            event['summary'] = summary
        if description is not None:
            event['description'] = description
        if start_datetime is not None:
            event['start'] = {
                'dateTime': start_datetime,
                'timeZone': timezone
            }
        if end_datetime is not None:
            event['end'] = {
                'dateTime': end_datetime,
                'timeZone': timezone
            }

        updated_event = service.events().update(
            calendarId='primary',
            eventId=event_id,
            body=event
        ).execute()

        return updated_event

    except HttpError as e:
        print(f"⚠️ Google API error: {str(e)}")
        raise
    except Exception as e:
        print(f"⚠️ Event update error: {str(e)}")
        raise

def delete_event(service, event_id: str) -> bool:
    """Delete an event"""
    try:
        service.events().delete(
            calendarId='primary',
            eventId=event_id
        ).execute()
        return True
    except HttpError as e:
        print(f"⚠️ Google API error: {str(e)}")
        raise
    except Exception as e:
        print(f"⚠️ Event deletion error: {str(e)}")
        raise

def get_event(service, event_id: str) -> Dict:
    """Get a specific event"""
    try:
        event = service.events().get(
            calendarId='primary',
            eventId=event_id
        ).execute()
        return event
    except HttpError as e:
        print(f"⚠️ Google API error: {str(e)}")
        raise
    except Exception as e:
        print(f"⚠️ Event retrieval error: {str(e)}")
        raise