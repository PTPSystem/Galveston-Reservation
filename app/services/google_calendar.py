"""
Google Calendar Integration Service
"""
import os
import pickle
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz

class GoogleCalendarService:
    """Service for interacting with Google Calendar API"""
    
    # Scopes required for calendar access
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self):
        self.service = None
        self.calendar_id = os.getenv('GOOGLE_CALENDAR_ID', 'bayfrontliving@gmail.com')
        self.credentials_path = os.getenv('GOOGLE_CLIENT_SECRETS_PATH', './secrets/client_secrets.json')
        self.token_path = './secrets/token.pickle'
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no (valid) credentials available, request authorization
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Google credentials file not found at {self.credentials_path}. "
                        "Please download client_secrets.json from Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('calendar', 'v3', credentials=creds)
    
    def get_events(self, start_date=None, end_date=None, max_results=100):
        """
        Retrieve events from Google Calendar
        
        Args:
            start_date: Start date for event query (datetime)
            end_date: End date for event query (datetime)
            max_results: Maximum number of events to return
        
        Returns:
            List of calendar events
        """
        try:
            # Default to next 6 months if no dates provided
            if not start_date:
                start_date = datetime.utcnow()
            if not end_date:
                end_date = start_date + timedelta(days=180)
            
            # Convert to RFC3339 format
            time_min = start_date.isoformat() + 'Z'
            time_max = end_date.isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            return events
            
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
    
    def create_event(self, summary, start_datetime, end_datetime, description=None, 
                    attendees=None, location=None):
        """
        Create a new event in Google Calendar
        
        Args:
            summary: Event title
            start_datetime: Event start time (datetime)
            end_datetime: Event end time (datetime)
            description: Event description
            attendees: List of attendee email addresses
            location: Event location
        
        Returns:
            Created event object or None if failed
        """
        try:
            # Ensure timezone awareness
            timezone = 'America/Chicago'  # Galveston timezone
            
            event = {
                'summary': summary,
                'location': location or 'Galveston Rental Property',
                'description': description or 'Booking via Galveston Reservation System',
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': timezone,
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': timezone,
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                        {'method': 'popup', 'minutes': 60},       # 1 hour before
                    ],
                },
            }
            
            # Add attendees if provided
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            
            return created_event
            
        except HttpError as error:
            print(f'An error occurred creating event: {error}')
            return None
    
    def update_event(self, event_id, **kwargs):
        """
        Update an existing event in Google Calendar
        
        Args:
            event_id: Google Calendar event ID
            **kwargs: Fields to update
        
        Returns:
            Updated event object or None if failed
        """
        try:
            # Get existing event
            existing_event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            # Update fields
            for key, value in kwargs.items():
                if key in existing_event:
                    existing_event[key] = value
            
            updated_event = self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=existing_event
            ).execute()
            
            return updated_event
            
        except HttpError as error:
            print(f'An error occurred updating event: {error}')
            return None
    
    def delete_event(self, event_id):
        """
        Delete an event from Google Calendar
        
        Args:
            event_id: Google Calendar event ID
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            return True
            
        except HttpError as error:
            print(f'An error occurred deleting event: {error}')
            return False
    
    def check_availability(self, start_datetime, end_datetime):
        """
        Check if a time slot is available (no conflicting events)
        
        Args:
            start_datetime: Requested start time
            end_datetime: Requested end time
        
        Returns:
            Dictionary with availability info
        """
        try:
            # Get events in the requested time range
            events = self.get_events(start_datetime, end_datetime)
            
            conflicts = []
            for event in events:
                event_start = event['start'].get('dateTime', event['start'].get('date'))
                event_end = event['end'].get('dateTime', event['end'].get('date'))
                
                # Parse datetime strings
                if 'T' in event_start:  # DateTime format
                    event_start_dt = datetime.fromisoformat(event_start.replace('Z', '+00:00'))
                    event_end_dt = datetime.fromisoformat(event_end.replace('Z', '+00:00'))
                else:  # Date format
                    event_start_dt = datetime.fromisoformat(event_start)
                    event_end_dt = datetime.fromisoformat(event_end)
                
                # Check for overlap
                if (start_datetime < event_end_dt and end_datetime > event_start_dt):
                    conflicts.append({
                        'id': event['id'],
                        'summary': event.get('summary', 'No title'),
                        'start': event_start_dt,
                        'end': event_end_dt
                    })
            
            return {
                'available': len(conflicts) == 0,
                'conflicts': conflicts,
                'message': 'Available' if len(conflicts) == 0 else f'{len(conflicts)} conflicting events found'
            }
            
        except Exception as error:
            print(f'Error checking availability: {error}')
            return {
                'available': False,
                'conflicts': [],
                'message': 'Error checking availability'
            }
