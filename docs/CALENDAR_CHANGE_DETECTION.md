# Google Calendar Change Detection Implementation Plan

## Overview
Detect when events in the livingbayfront@gmail.com Google Calendar are modified or deleted, and automatically notify stakeholders (Galveston Island Resort Rentals and KleenSweep).

## Current Architecture Analysis

### Existing Calendar Integration
- **Calendar Service**: `app/services/google_calendar.py`
- **Event Creation**: When bookings are approved, events are added to Google Calendar
- **Event Storage**: `google_event_id` is stored in the `booking_requests` table
- **Calendar Sync**: Existing sync functionality in `scripts/calendar_sync_cron.py`

## Implementation Approaches

### Approach 1: Google Calendar Push Notifications (Webhooks) ⭐ RECOMMENDED

**How it works:**
1. Register a webhook endpoint with Google Calendar API
2. Google sends push notifications when calendar events change
3. Process notifications and identify booking-related events
4. Send notifications to stakeholders

**Advantages:**
- Real-time notifications
- Efficient (only processes actual changes)
- Official Google API feature

**Implementation:**
```python
# New endpoint: /api/calendar/webhook
@api_bp.route('/calendar/webhook', methods=['POST'])
def calendar_webhook():
    """Handle Google Calendar push notifications"""
    # Verify Google's signature
    # Parse the notification
    # Identify if it's a booking-related event
    # Send stakeholder notifications
```

**Setup Required:**
1. Domain verification with Google
2. Webhook endpoint registration
3. SSL certificate (Google requires HTTPS for webhooks)

### Approach 2: Periodic Calendar Sync with Change Detection ⭐ FEASIBLE NOW

**How it works:**
1. Extend existing calendar sync to detect changes
2. Compare current calendar state with last known state
3. Identify modified/deleted booking events
4. Send notifications for changes

**Advantages:**
- Uses existing infrastructure
- No additional Google setup required
- Can implement immediately

**Implementation:**
```python
# Extend existing calendar sync
def detect_calendar_changes():
    """Compare current calendar with stored events to detect changes"""
    # Get current calendar events
    # Compare with stored booking events
    # Identify modifications/deletions
    # Send stakeholder notifications
```

### Approach 3: Manual Change Notification Interface

**How it works:**
1. Simple email-based change notification
2. You send an email to a special address when changes are made
3. Email parsing triggers stakeholder notifications

**Advantages:**
- Very simple to implement
- No calendar API complexity
- Immediate control

## Recommended Implementation: Approach 2 (Enhanced Calendar Sync)

Since you already have calendar sync infrastructure, this is the most practical immediate solution.

### Implementation Plan

#### Step 1: Enhanced Event Storage
Store calendar event details for comparison:
```sql
-- Add to existing booking_requests table
ALTER TABLE booking_requests ADD COLUMN calendar_event_summary VARCHAR(255);
ALTER TABLE booking_requests ADD COLUMN calendar_event_start_date TIMESTAMP;
ALTER TABLE booking_requests ADD COLUMN calendar_event_end_date TIMESTAMP;
ALTER TABLE booking_requests ADD COLUMN calendar_last_modified TIMESTAMP;
```

#### Step 2: Change Detection Logic
```python
class CalendarChangeDetector:
    """Detect changes in Google Calendar events for bookings"""
    
    def detect_booking_changes(self):
        """Compare current calendar state with stored booking events"""
        changes = {
            'modified': [],
            'deleted': [],
            'moved': []
        }
        
        # Get all current calendar events
        current_events = self.get_calendar_events()
        
        # Get all stored booking events
        stored_bookings = self.get_stored_booking_events()
        
        # Detect changes
        for booking in stored_bookings:
            if booking.google_event_id:
                current_event = self.find_event_by_id(current_events, booking.google_event_id)
                
                if not current_event:
                    # Event was deleted
                    changes['deleted'].append(booking)
                elif self.event_was_modified(booking, current_event):
                    # Event was modified
                    changes['modified'].append((booking, current_event))
        
        return changes
    
    def event_was_modified(self, booking, current_event):
        """Check if calendar event differs from stored booking"""
        # Compare dates, times, descriptions
        stored_start = booking.calendar_event_start_date
        current_start = self.parse_event_date(current_event['start'])
        
        stored_end = booking.calendar_event_end_date
        current_end = self.parse_event_date(current_event['end'])
        
        return (stored_start != current_start or 
                stored_end != current_end or
                booking.calendar_event_summary != current_event.get('summary', ''))
```

#### Step 3: Stakeholder Notification Service
```python
class BookingChangeNotificationService:
    """Handle notifications for booking changes"""
    
    def notify_booking_deleted(self, booking):
        """Notify stakeholders of deleted booking"""
        subject = f"BOOKING CANCELLED - {booking.start_date.strftime('%m/%d')} to {booking.end_date.strftime('%m/%d')}"
        
        # Notify Galveston Island Resort Rentals
        # Notify KleenSweep
        
    def notify_booking_modified(self, booking, new_event):
        """Notify stakeholders of modified booking"""
        subject = f"BOOKING CHANGED - {booking.start_date.strftime('%m/%d')} to {booking.end_date.strftime('%m/%d')}"
        
        # Include old vs new details
        # Notify stakeholders
```

#### Step 4: Integration with Existing Cron Job
```python
# Modify scripts/calendar_sync_cron.py
def enhanced_calendar_sync():
    """Enhanced sync that also detects booking changes"""
    
    # Existing sync logic
    sync_calendar_events()
    
    # New change detection
    change_detector = CalendarChangeDetector()
    changes = change_detector.detect_booking_changes()
    
    # Send notifications
    notification_service = BookingChangeNotificationService()
    
    for deleted_booking in changes['deleted']:
        notification_service.notify_booking_deleted(deleted_booking)
    
    for booking, new_event in changes['modified']:
        notification_service.notify_booking_modified(booking, new_event)
```

## Email Templates for Change Notifications

### Deletion Notification
```
Subject: BOOKING CANCELLED - 09/15 to 09/18

A booking has been cancelled in the calendar:

Original Booking:
• Dates: September 15-18, 2025
• Guests: 4
• Property: Galveston Bayfront Retreat

This booking was removed from the livingbayfront@gmail.com calendar.

Please update your records accordingly.
```

### Modification Notification
```
Subject: BOOKING CHANGED - 09/15 to 09/18

A booking has been modified in the calendar:

Original Booking:
• Dates: September 15-18, 2025
• Duration: 3 nights

Updated Booking:
• Dates: September 16-19, 2025  
• Duration: 3 nights

Property: Galveston Bayfront Retreat

Please update your records accordingly.
```

## Implementation Priority

1. **Phase 1**: Enhance calendar sync with change detection
2. **Phase 2**: Add stakeholder notification emails
3. **Phase 3**: Add database fields for event tracking
4. **Phase 4**: Test with real calendar changes

Would you like me to start implementing the enhanced calendar sync with change detection? This would extend your existing calendar sync functionality to detect when events are modified or deleted and automatically notify the stakeholders.
