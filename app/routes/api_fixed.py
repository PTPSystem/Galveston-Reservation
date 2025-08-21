"""
API routes for calendar data and external integrations
"""
from flask import Blueprint, jsonify, request
from app.services.google_calendar import GoogleCalendarService
from app.models import BookingRequest, CalendarEvent
from datetime import datetime, timedelta
import os

api_bp = Blueprint('api', __name__)

@api_bp.route('/calendar/events')
def get_calendar_events():
    """Get calendar events for display"""
    try:
        # Get date range from request
        start_date_str = request.args.get('start')
        end_date_str = request.args.get('end')
        
        if start_date_str and end_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', ''))
            end_date = datetime.fromisoformat(end_date_str.replace('Z', ''))
        else:
            # Default to current month + 6 months
            start_date = datetime.now().replace(day=1)
            end_date = start_date + timedelta(days=180)
        
        calendar_service = GoogleCalendarService()
        events = calendar_service.get_events(start_date, end_date)
        
        # Convert to FullCalendar format
        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            # Ensure consistent date format for FullCalendar
            if start:
                # If it's a date-only format, keep it simple
                if 'T' not in str(start):
                    start_formatted = str(start)
                else:
                    # Convert datetime to date-only for all-day events
                    try:
                        start_dt = datetime.fromisoformat(str(start).replace('Z', '+00:00'))
                        start_formatted = start_dt.strftime('%Y-%m-%d')
                    except:
                        start_formatted = str(start)[:10]
            
            if end:
                # If it's a date-only format, keep it simple
                if 'T' not in str(end):
                    end_formatted = str(end)
                else:
                    # Convert datetime to date-only for all-day events
                    try:
                        end_dt = datetime.fromisoformat(str(end).replace('Z', '+00:00'))
                        end_formatted = end_dt.strftime('%Y-%m-%d')
                    except:
                        end_formatted = str(end)[:10]
            
            formatted_events.append({
                'id': event['id'],
                'title': event.get('summary', 'Property Booked'),
                'start': start_formatted,
                'end': end_formatted,
                'allDay': True,  # Force all-day events for better visibility
                'description': event.get('description', ''),
                'status': event.get('status', 'confirmed'),
                'color': '#dc3545',
                'textColor': '#ffffff',
                'display': 'block'
            })
        
        return jsonify(formatted_events)
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch calendar events',
            'message': str(e)
        }), 500

@api_bp.route('/calendar/test-events')
def get_test_calendar_events():
    """Test endpoint with hard-coded events to verify FullCalendar rendering"""
    test_events = [
        {
            'id': 'test1',
            'title': '🔴 BOOKED - Test Event',
            'start': '2025-08-29',
            'end': '2025-09-02',
            'allDay': True,
            'color': '#dc3545',
            'textColor': '#ffffff',
            'display': 'block'
        },
        {
            'id': 'test2', 
            'title': '🔴 BOOKED - Another Test',
            'start': '2025-09-18',
            'end': '2025-09-29',
            'allDay': True,
            'color': '#dc3545',
            'textColor': '#ffffff',
            'display': 'block'
        }
    ]
    
    return jsonify(test_events)

@api_bp.route('/booking/request', methods=['POST'])
def create_booking_request():
    """Create a new booking request"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'checkin', 'checkout', 'guests']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create booking request
        booking = BookingRequest(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone', ''),
            checkin_date=datetime.fromisoformat(data['checkin']).date(),
            checkout_date=datetime.fromisoformat(data['checkout']).date(),
            guests=data['guests'],
            special_requests=data.get('special_requests', ''),
            status='pending'
        )
        
        # Save to database
        from app import db
        db.session.add(booking)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'booking_id': booking.id,
            'message': 'Booking request submitted successfully'
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to create booking request',
            'message': str(e)
        }), 500

@api_bp.route('/calendar/check-availability')
def check_availability():
    """Check if dates are available for booking"""
    try:
        checkin = request.args.get('checkin')
        checkout = request.args.get('checkout')
        
        if not checkin or not checkout:
            return jsonify({'error': 'Both checkin and checkout dates required'}), 400
        
        checkin_date = datetime.fromisoformat(checkin).date()
        checkout_date = datetime.fromisoformat(checkout).date()
        
        # Get calendar service
        calendar_service = GoogleCalendarService()
        
        # Check for conflicts
        events = calendar_service.get_events(
            datetime.combine(checkin_date, datetime.min.time()),
            datetime.combine(checkout_date, datetime.min.time())
        )
        
        # Check if any events overlap with requested dates
        conflicts = []
        for event in events:
            event_start = event['start'].get('dateTime', event['start'].get('date'))
            event_end = event['end'].get('dateTime', event['end'].get('date'))
            
            # Parse event dates
            if isinstance(event_start, str):
                if 'T' in event_start:
                    event_start_date = datetime.fromisoformat(event_start.replace('Z', '')).date()
                else:
                    event_start_date = datetime.fromisoformat(event_start).date()
            
            if isinstance(event_end, str):
                if 'T' in event_end:
                    event_end_date = datetime.fromisoformat(event_end.replace('Z', '')).date()
                else:
                    event_end_date = datetime.fromisoformat(event_end).date()
            
            # Check for overlap
            if not (checkout_date <= event_start_date or checkin_date >= event_end_date):
                conflicts.append({
                    'title': event.get('summary', 'Booking'),
                    'start': str(event_start_date),
                    'end': str(event_end_date)
                })
        
        return jsonify({
            'available': len(conflicts) == 0,
            'conflicts': conflicts,
            'message': 'Available' if len(conflicts) == 0 else f'{len(conflicts)} conflict(s) found'
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to check availability',
            'message': str(e)
        }), 500
