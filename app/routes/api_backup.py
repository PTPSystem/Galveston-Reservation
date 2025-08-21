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

@api.route('/calendar/test-events')
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
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch calendar events',
            'message': str(e)
        }), 500

@api_bp.route('/availability/range')
def check_availability_range():
    """Check availability for a date range (for calendar display)"""
    try:
        start_date_str = request.args.get('start')
        end_date_str = request.args.get('end')
        
        if not start_date_str or not end_date_str:
            return jsonify({'error': 'start and end dates required'}), 400
        
        start_date = datetime.fromisoformat(start_date_str)
        end_date = datetime.fromisoformat(end_date_str)
        
        calendar_service = GoogleCalendarService()
        events = calendar_service.get_events(start_date, end_date)
        
        # Create availability map
        availability = {}
        current_date = start_date.date()
        end_date_only = end_date.date()
        
        # Initialize all dates as available
        while current_date <= end_date_only:
            availability[current_date.isoformat()] = {
                'available': True,
                'events': []
            }
            current_date += timedelta(days=1)
        
        # Mark dates with events as unavailable
        for event in events:
            event_start = event['start'].get('dateTime', event['start'].get('date'))
            event_end = event['end'].get('dateTime', event['end'].get('date'))
            
            # Parse dates
            if 'T' in event_start:
                event_start_date = datetime.fromisoformat(event_start.replace('Z', '+00:00')).date()
                event_end_date = datetime.fromisoformat(event_end.replace('Z', '+00:00')).date()
            else:
                event_start_date = datetime.fromisoformat(event_start).date()
                event_end_date = datetime.fromisoformat(event_end).date()
            
            # Mark dates as unavailable
            current_event_date = event_start_date
            while current_event_date < event_end_date:
                date_str = current_event_date.isoformat()
                if date_str in availability:
                    availability[date_str]['available'] = False
                    availability[date_str]['events'].append({
                        'title': event.get('summary', 'Booking'),
                        'start': event_start,
                        'end': event_end
                    })
                current_event_date += timedelta(days=1)
        
        return jsonify(availability)
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to check availability',
            'message': str(e)
        }), 500

@api_bp.route('/bookings/stats')
def booking_stats():
    """Get booking statistics for dashboard"""
    try:
        stats = {
            'pending': BookingRequest.query.filter_by(status='pending').count(),
            'approved': BookingRequest.query.filter_by(status='approved').count(),
            'confirmed': BookingRequest.query.filter_by(status='confirmed').count(),
            'rejected': BookingRequest.query.filter_by(status='rejected').count(),
            'total': BookingRequest.query.count()
        }
        
        # Recent activity (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_bookings = BookingRequest.query.filter(
            BookingRequest.created_at >= thirty_days_ago
        ).count()
        
        stats['recent'] = recent_bookings
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get booking stats',
            'message': str(e)
        }), 500

@api_bp.route('/sync/external')
def sync_external_calendar():
    """Sync with external calendar source"""
    # This would implement the external calendar sync logic
    # as described in the README for checking against booking platforms
    
    return jsonify({
        'message': 'External calendar sync not yet implemented',
        'status': 'todo'
    })

@api_bp.route('/webhook/booking', methods=['POST'])
def booking_webhook():
    """Webhook endpoint for external booking notifications"""
    # This would handle webhooks from booking platforms
    # to automatically create events in Google Calendar
    
    return jsonify({
        'message': 'Webhook endpoint ready',
        'status': 'received'
    })
