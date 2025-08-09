"""
Booking routes for handling reservation requests
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app import db
from app.models import BookingRequest
from app.services.email import EmailService
from app.services.google_calendar import GoogleCalendarService
from datetime import datetime
import secrets

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/request', methods=['GET', 'POST'])
def booking_request():
    """Handle booking request form"""
    if request.method == 'GET':
        return render_template('booking_request.html')
    
    try:
        # Extract form data
        guest_name = request.form.get('guest_name', '').strip()
        guest_email = request.form.get('guest_email', '').strip()
        guest_phone = request.form.get('guest_phone', '').strip()
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        num_guests = request.form.get('num_guests', 1, type=int)
        special_requests = request.form.get('special_requests', '').strip()
        
        # Validation
        errors = []
        if not guest_name:
            errors.append('Guest name is required')
        if not guest_email:
            errors.append('Email address is required')
        if not start_date_str:
            errors.append('Check-in date is required')
        if not end_date_str:
            errors.append('Check-out date is required')
        
        # Parse dates
        try:
            start_date = datetime.fromisoformat(start_date_str)
            end_date = datetime.fromisoformat(end_date_str)
        except ValueError:
            errors.append('Invalid date format')
        
        # Date validation
        if not errors:
            if start_date >= end_date:
                errors.append('Check-out date must be after check-in date')
            if start_date < datetime.now():
                errors.append('Check-in date must be in the future')
        
        if errors:
            return jsonify({'errors': errors}), 400
        
        # Check availability
        calendar_service = GoogleCalendarService()
        availability = calendar_service.check_availability(start_date, end_date)
        
        if not availability['available']:
            return jsonify({
                'error': 'Selected dates are not available',
                'conflicts': availability['conflicts']
            }), 409
        
        # Create booking request
        booking = BookingRequest(
            guest_name=guest_name,
            guest_email=guest_email,
            guest_phone=guest_phone,
            start_date=start_date,
            end_date=end_date,
            num_guests=num_guests,
            special_requests=special_requests,
            status='pending',
            approval_token=secrets.token_urlsafe(32)
        )
        
        db.session.add(booking)
        db.session.commit()
        
        # Send notification email to admin
        email_service = EmailService()
        email_sent = email_service.send_booking_request_notification(booking)
        
        if email_sent:
            return jsonify({
                'success': True,
                'message': 'Your booking request has been submitted successfully. You will receive a confirmation email once reviewed.',
                'booking_id': booking.id
            })
        else:
            return jsonify({
                'success': True,
                'message': 'Your booking request has been submitted successfully.',
                'booking_id': booking.id,
                'warning': 'Email notification may have failed'
            })
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'An error occurred processing your request',
            'message': str(e)
        }), 500

@booking_bp.route('/status/<int:booking_id>')
def booking_status(booking_id):
    """Check booking request status"""
    booking = BookingRequest.query.get_or_404(booking_id)
    return jsonify(booking.to_dict())

@booking_bp.route('/confirmation/<int:booking_id>')
def booking_confirmation(booking_id):
    """Show booking confirmation page"""
    booking = BookingRequest.query.get_or_404(booking_id)
    return render_template('booking_confirmation.html', booking=booking)
