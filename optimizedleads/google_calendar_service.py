import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json

class GoogleCalendarService:
    def __init__(self, credentials):
        self.credentials = credentials
        self.service = build('calendar', 'v3', credentials=credentials)
    
    def create_event(self, event_data):
        """
        Google Calendar mein event create karta hai
        """
        try:
            event = {
                'summary': event_data['title'],
                'description': event_data['description'],
                'start': {
                    'dateTime': event_data['start_time'],
                    'timeZone': 'Asia/Kolkata',
                },
                'end': {
                    'dateTime': event_data['end_time'],
                    'timeZone': 'Asia/Kolkata',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 30},
                    ],
                },
            }
            
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            return {
                'success': True,
                'event_id': created_event['id'],
                'html_link': created_event.get('htmlLink', ''),
                'event': created_event
            }
            
        except HttpError as error:
            return {
                'success': False,
                'error': f'Google Calendar error: {error}'
            }
    
    def get_events(self, max_results=10):
        """
        Google Calendar se events fetch karta hai
        """
        try:
            now = datetime.datetime.utcnow().isoformat() + 'Z'
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            return {
                'success': True,
                'events': events
            }
            
        except HttpError as error:
            return {
                'success': False,
                'error': f'Google Calendar error: {error}'
            }