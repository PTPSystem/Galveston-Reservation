"""
Main routes for the Galveston Reservation System
"""
from flask import Blueprint, render_template, request, jsonify
from app.services.google_calendar import GoogleCalendarService
from app.models import CalendarEvent
from datetime import datetime, timedelta
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main landing page with booking calendar"""
    return render_template('index.html')

@main_bp.route('/calendar')
def calendar_view():
    """Full calendar view"""
    return render_template('calendar.html')

@main_bp.route('/about')
def about():
    """About the property page"""
    return render_template('about.html')

@main_bp.route('/contact')
def contact():
    """Contact information page"""
    return render_template('contact.html')

@main_bp.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@main_bp.route('/api/availability')
def check_availability():
    """API endpoint to check availability for date range"""
    try:
        start_date = request.args.get('start')
        end_date = request.args.get('end')
        
        if not start_date or not end_date:
            return jsonify({
                'error': 'start and end parameters are required',
                'format': 'YYYY-MM-DD'
            }), 400
        
        # Parse dates
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        # Check with Google Calendar
        calendar_service = GoogleCalendarService()
        availability = calendar_service.check_availability(start_dt, end_dt)
        
        return jsonify(availability)
        
    except ValueError as e:
        return jsonify({
            'error': 'Invalid date format',
            'message': str(e),
            'format': 'YYYY-MM-DD'
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500
