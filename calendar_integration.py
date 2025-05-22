# calendar_integration.py
# Integrate Google Calendar with DigitalDog using Google Calendar API
# Features: fetch events, add events, update events, delete events
# Requires: pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

import os
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar']
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json'  # User must provide this from Google Cloud Console

class CalendarIntegration:
    def __init__(self):
        self.creds = None
        self.service = None
        self.authenticate()

    def authenticate(self):
        if os.path.exists(TOKEN_FILE):
            self.creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, 'w') as token:
                token.write(self.creds.to_json())
        self.service = build('calendar', 'v3', credentials=self.creds)

    def get_upcoming_events(self, max_results=10):
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = self.service.events().list(
            calendarId='primary', timeMin=now,
            maxResults=max_results, singleEvents=True,
            orderBy='startTime').execute()
        return events_result.get('items', [])

    def add_event(self, summary, start_dt, end_dt, description=None):
        event = {
            'summary': summary,
            'description': description or '',
            'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'UTC'},
            'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'UTC'},
        }
        created_event = self.service.events().insert(calendarId='primary', body=event).execute()
        return created_event

    def update_event(self, event_id, **kwargs):
        event = self.service.events().get(calendarId='primary', eventId=event_id).execute()
        for key, value in kwargs.items():
            event[key] = value
        updated_event = self.service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
        return updated_event

    def delete_event(self, event_id):
        self.service.events().delete(calendarId='primary', eventId=event_id).execute()

# Usage example (to be called from DigitalDog or dashboard):
# cal = CalendarIntegration()
# events = cal.get_upcoming_events()
# cal.add_event('Test Event', datetime.datetime(2025,5,22,15,0), datetime.datetime(2025,5,22,16,0))
