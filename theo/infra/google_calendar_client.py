from datetime import datetime, timezone, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

class GoogleCalendarClient:
    def __init__(self, creds_path: str):
        self.creds_path = creds_path
        self.scopes = ['https://www.googleapis.com/auth/calendar.readonly']
        self._service = None

    @property
    def service(self):
        if self._service is None:
            if not os.path.exists(self.creds_path):
                raise FileNotFoundError(f"Google credentials file not found at: {self.creds_path}")
            
            creds = service_account.Credentials.from_service_account_file(
                self.creds_path, scopes=self.scopes
            )
            self._service = build('calendar', 'v3', credentials=creds)
        return self._service

    def get_events_for_today(self, calendar_id: str) -> list:
        """Fetches events for the current day from the specified calendar."""
        from zoneinfo import ZoneInfo
        tz = ZoneInfo("Africa/Lagos")
        now = datetime.now(tz)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat()

        events_result = self.service.events().list(
            calendarId=calendar_id,
            timeMin=start_of_day,
            timeMax=end_of_day,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        return events_result.get('items', [])
