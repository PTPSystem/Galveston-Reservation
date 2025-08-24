"""
Calendar Change Detection Service
Detects changes to booking events in Google Calendar and notifies stakeholders
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from app.services.google_calendar import GoogleCalendarService
from app.services.email import EmailService
from app.models import BookingRequest
from app import db

logger = logging.getLogger(__name__)

@dataclass
class CalendarEventChange:
    """Represents a change to a calendar event"""
    booking_id: int
    change_type: str  # 'modified', 'deleted', 'moved'
    old_data: Dict
    new_data: Optional[Dict] = None
    guest_email: str = ''
    guest_name: str = ''

class CalendarChangeDetectionService:
    """Detects changes in Google Calendar events for booking management"""
    
    def __init__(self):
        self.google_service = GoogleCalendarService()
        self.email_service = EmailService()
        
    def detect_booking_changes(self, days_back: int = 7) -> List[CalendarEventChange]:
        """
        Detect changes to booking events in Google Calendar
        
        Args:
            days_back: Number of days to look back for changes
            
        Returns:
            List of detected changes
        """
        changes = []
        
        try:
            logger.info(f"Starting calendar change detection for last {days_back} days...")
            
            # Get all bookings with Google Calendar events
            bookings_with_events = self._get_bookings_with_calendar_events()
            
            if not bookings_with_events:
                logger.info("No bookings with calendar events found")
                return changes
            
            # Get current calendar events
            start_date = datetime.now() - timedelta(days=days_back)
            end_date = datetime.now() + timedelta(days=365)  # Look ahead for future changes
            current_events = self.google_service.get_events(start_date, end_date)
            
            # Create lookup for current events by ID
            current_events_by_id = {event['id']: event for event in current_events if 'id' in event}
            
            # Check each booking for changes
            for booking in bookings_with_events:
                if booking.google_event_id:
                    change = self._check_booking_for_changes(booking, current_events_by_id)
                    if change:
                        changes.append(change)
                        
            logger.info(f"Detected {len(changes)} calendar changes")
            return changes
            
        except Exception as e:
            logger.error(f"Error detecting calendar changes: {e}")
            return changes
    
    def _get_bookings_with_calendar_events(self) -> List[BookingRequest]:
        """Get all bookings that have associated Google Calendar events"""
        try:
            return BookingRequest.query.filter(
                BookingRequest.google_event_id.isnot(None),
                BookingRequest.status == 'approved'
            ).all()
        except Exception as e:
            logger.error(f"Error fetching bookings with calendar events: {e}")
            return []
    
    def _check_booking_for_changes(
        self, 
        booking: BookingRequest, 
        current_events_by_id: Dict[str, Dict]
    ) -> Optional[CalendarEventChange]:
        """
        Check if a specific booking has changes in the calendar
        
        Args:
            booking: The booking to check
            current_events_by_id: Dictionary of current calendar events by ID
            
        Returns:
            CalendarEventChange if changes detected, None otherwise
        """
        try:
            current_event = current_events_by_id.get(booking.google_event_id)
            
            if not current_event:
                # Event was deleted
                return CalendarEventChange(
                    booking_id=booking.id,
                    change_type='deleted',
                    old_data={
                        'start_date': booking.start_date,
                        'end_date': booking.end_date,
                        'summary': f'Guest Booking - {booking.start_date.strftime("%m/%d")} to {booking.end_date.strftime("%m/%d")}'
                    },
                    guest_email=booking.guest_email,
                    guest_name=booking.guest_name
                )
            
            # Check for modifications
            if self._event_was_modified(booking, current_event):
                return CalendarEventChange(
                    booking_id=booking.id,
                    change_type='modified',
                    old_data={
                        'start_date': booking.start_date,
                        'end_date': booking.end_date,
                        'summary': f'Guest Booking - {booking.start_date.strftime("%m/%d")} to {booking.end_date.strftime("%m/%d")}'
                    },
                    new_data=self._extract_event_data(current_event),
                    guest_email=booking.guest_email,
                    guest_name=booking.guest_name
                )
                
            return None
            
        except Exception as e:
            logger.error(f"Error checking booking {booking.id} for changes: {e}")
            return None
    
    def _event_was_modified(self, booking: BookingRequest, current_event: Dict) -> bool:
        """Check if calendar event differs from stored booking"""
        try:
            # Parse current event dates
            current_start = self._parse_event_date(current_event.get('start', {}))
            current_end = self._parse_event_date(current_event.get('end', {}))
            
            if not current_start or not current_end:
                logger.warning(f"Could not parse dates for event {current_event.get('id')}")
                return False
            
            # Compare dates (convert to date only for comparison)
            booking_start = booking.start_date.date()
            booking_end = booking.end_date.date()
            
            current_start_date = current_start.date()
            current_end_date = current_end.date()
            
            return (booking_start != current_start_date or 
                   booking_end != current_end_date)
                   
        except Exception as e:
            logger.error(f"Error comparing booking {booking.id} with calendar event: {e}")
            return False
    
    def _parse_event_date(self, date_obj: Dict) -> Optional[datetime]:
        """Parse Google Calendar event date"""
        try:
            if 'date' in date_obj:
                # All-day event
                return datetime.strptime(date_obj['date'], '%Y-%m-%d')
            elif 'dateTime' in date_obj:
                # Timed event
                dt_str = date_obj['dateTime']
                if dt_str.endswith('Z'):
                    return datetime.fromisoformat(dt_str[:-1])
                else:
                    return datetime.fromisoformat(dt_str.split('+')[0])
            return None
        except Exception as e:
            logger.error(f"Error parsing event date {date_obj}: {e}")
            return None
    
    def _extract_event_data(self, event: Dict) -> Dict:
        """Extract relevant data from calendar event"""
        start_date = self._parse_event_date(event.get('start', {}))
        end_date = self._parse_event_date(event.get('end', {}))
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'summary': event.get('summary', ''),
            'description': event.get('description', '')
        }
    
    def send_change_notifications(self, changes: List[CalendarEventChange]) -> Dict[str, int]:
        """
        Send notifications for detected calendar changes
        
        Args:
            changes: List of detected changes
            
        Returns:
            Summary of notifications sent
        """
        results = {
            'stakeholder_notifications': 0,
            'guest_notifications': 0,
            'errors': 0
        }
        
        for change in changes:
            try:
                # Send stakeholder notification
                if self._send_stakeholder_notification(change):
                    results['stakeholder_notifications'] += 1
                
                # Send guest notification (optional)
                if change.guest_email and self._send_guest_notification(change):
                    results['guest_notifications'] += 1
                    
            except Exception as e:
                logger.error(f"Error sending notifications for change {change.booking_id}: {e}")
                results['errors'] += 1
        
        return results
    
    def _send_stakeholder_notification(self, change: CalendarEventChange) -> bool:
        """Send notification to stakeholders about booking change"""
        try:
            import os
            
            # Use environment-based notification emails
            if os.getenv('FLASK_ENV') == 'staging':
                notification_emails = ['howard.shen@gmail.com']
            else:
                # Production environment - send to all stakeholders
                notification_emails = [
                    'livingbayfront@gmail.com',
                    'info@galvestonislandresortrentals.com', 
                    'michelle.kleensweep@gmail.com',
                    'alicia.kleensweep@gmail.com'
                ]
            
            if change.change_type == 'deleted':
                subject = f"BOOKING CANCELLED - {change.old_data['start_date'].strftime('%m/%d')} to {change.old_data['end_date'].strftime('%m/%d')}"
                message = self._build_deletion_message(change)
            elif change.change_type == 'modified':
                subject = f"BOOKING CHANGED - {change.old_data['start_date'].strftime('%m/%d')} to {change.old_data['end_date'].strftime('%m/%d')}"
                message = self._build_modification_message(change)
            else:
                return False
            
            # Send to stakeholders
            return self.email_service.send_stakeholder_notification(
                subject=subject,
                message=message,
                recipients=notification_emails
            )
            
        except Exception as e:
            logger.error(f"Error sending stakeholder notification: {e}")
            return False
    
    def _send_guest_notification(self, change: CalendarEventChange) -> bool:
        """Send notification to guest about their booking change"""
        try:
            if change.change_type == 'deleted':
                subject = f"Booking Cancellation Confirmed - Galveston Bayfront Retreat"
                message = self._build_guest_cancellation_message(change)
            elif change.change_type == 'modified':
                subject = f"Booking Update - Galveston Bayfront Retreat"
                message = self._build_guest_modification_message(change)
            else:
                return False
            
            return self.email_service.send_guest_notification(
                subject=subject,
                message=message,
                recipient=change.guest_email
            )
            
        except Exception as e:
            logger.error(f"Error sending guest notification: {e}")
            return False
    
    def _build_deletion_message(self, change: CalendarEventChange) -> str:
        """Build message for booking deletion"""
        return f"""
A booking has been cancelled in the calendar:

CANCELLED BOOKING:
• Dates: {change.old_data['start_date'].strftime('%B %d')} - {change.old_data['end_date'].strftime('%B %d, %Y')}
• Property: Galveston Bayfront Retreat
• Calendar Event: {change.old_data.get('summary', 'Guest Booking')}

This booking was removed from the livingbayfront@gmail.com calendar.

Please update your records accordingly.

---
Automated notification from Galveston Reservation System
"""
    
    def _build_modification_message(self, change: CalendarEventChange) -> str:
        """Build message for booking modification"""
        old_data = change.old_data
        new_data = change.new_data
        
        return f"""
A booking has been modified in the calendar:

ORIGINAL BOOKING:
• Dates: {old_data['start_date'].strftime('%B %d')} - {old_data['end_date'].strftime('%B %d, %Y')}

UPDATED BOOKING:
• Dates: {new_data['start_date'].strftime('%B %d')} - {new_data['end_date'].strftime('%B %d, %Y')}

Property: Galveston Bayfront Retreat

Please update your records accordingly.

---
Automated notification from Galveston Reservation System
"""
    
    def _build_guest_cancellation_message(self, change: CalendarEventChange) -> str:
        """Build cancellation message for guest"""
        return f"""
Your booking has been cancelled:

CANCELLED BOOKING:
• Dates: {change.old_data['start_date'].strftime('%B %d')} - {change.old_data['end_date'].strftime('%B %d, %Y')}
• Property: Galveston Bayfront Retreat

If you have any questions about this cancellation, please contact us.

---
Galveston Bayfront Retreat
"""
    
    def _build_guest_modification_message(self, change: CalendarEventChange) -> str:
        """Build modification message for guest"""
        old_data = change.old_data
        new_data = change.new_data
        
        return f"""
Your booking has been updated:

ORIGINAL DATES:
{old_data['start_date'].strftime('%B %d')} - {old_data['end_date'].strftime('%B %d, %Y')}

NEW DATES:
{new_data['start_date'].strftime('%B %d')} - {new_data['end_date'].strftime('%B %d, %Y')}

Property: Galveston Bayfront Retreat

If you have any questions about this change, please contact us.

---
Galveston Bayfront Retreat
"""
