"""
Google Calendar Integration Service
"""
import os
import json
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz

class GoogleCalendarService:
    """Service for interacting with Google Calendar API"""
    
    # Scopes required for calendar access
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self):
        # Import config here to avoid circular imports
        from app.config import config
        
        self.service = None
        self.calendar_id = config.GOOGLE_CALENDAR_ID
        self.credentials_path = config.GOOGLE_CREDENTIALS_PATH
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Calendar API using service account"""
        try:
            if not os.path.exists(self.credentials_path):
                raise FileNotFoundError(
                    f"Google service account file not found at {self.credentials_path}. "
                    "Please ensure the service-account.json file is in the secrets folder."
                )
            
            # Load service account credentials
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path, scopes=self.SCOPES)
            
            # Build the service
            self.service = build('calendar', 'v3', credentials=credentials)
            
        except Exception as e:
            raise Exception(f"Failed to authenticate with Google Calendar: {e}")
    
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
            
            # Ensure we're working with UTC and proper RFC3339 format
            if start_date.tzinfo is None:
                start_date = start_date.replace(tzinfo=pytz.UTC)
            if end_date.tzinfo is None:
                end_date = end_date.replace(tzinfo=pytz.UTC)
            
            # Convert to UTC and format properly
            start_date_utc = start_date.astimezone(pytz.UTC)
            end_date_utc = end_date.astimezone(pytz.UTC)
            
            time_min = start_date_utc.strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-3] + 'Z'
            time_max = end_date_utc.strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-3] + 'Z'
            
            print(f"Requesting calendar events from {time_min} to {time_max}")
            
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            print(f"Found {len(events)} events")
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
    
    def create_event_from_dict(self, event_dict):
        """
        Create an event from a dictionary (for simple event creation)
        
        Args:
            event_dict: Dictionary containing event details
        
        Returns:
            Created event object or None if failed
        """
        try:
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event_dict
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
    
    def sync_events(self, days_ahead=30):
        """
        Sync events from Google Calendar
        
        Args:
            days_ahead: Number of days ahead to sync
            
        Returns:
            List of synced events
        """
        try:
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=days_ahead)
            
            events = self.get_events(start_date, end_date)
            return events if events else []
            
        except Exception as error:
            print(f'Error syncing events: {error}')
            return []
