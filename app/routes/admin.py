"""
Admin routes for managing bookings and approvals
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app import db
from app.models import BookingRequest, CalendarEvent
from app.services.email import EmailService
from app.services.google_calendar import GoogleCalendarService
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
def dashboard():
    """Admin dashboard with pending requests and recent activity"""
    # Get pending booking requests
    pending_requests = BookingRequest.query.filter_by(status='pending').order_by(BookingRequest.created_at.desc()).all()
    
    # Get recent approved/rejected requests
    recent_requests = BookingRequest.query.filter(
        BookingRequest.status.in_(['approved', 'rejected', 'confirmed'])
    ).order_by(BookingRequest.updated_at.desc()).limit(20).all()
    
    return render_template('admin/dashboard.html', 
                         pending_requests=pending_requests, 
                         recent_requests=recent_requests)

@admin_bp.route('/approve/<token>')
def approve_booking(token):
    """Approve a booking request via email link"""
    try:
        email_service = EmailService()
        token_data = email_service.verify_token(token)
        
        if not token_data or token_data.get('action') != 'approve':
            flash('Invalid or expired approval link', 'error')
            return redirect(url_for('admin.dashboard'))
        
        booking_id = token_data['booking_id']
        booking = BookingRequest.query.get_or_404(booking_id)
        
        if booking.status != 'pending':
            flash(f'Booking is already {booking.status}', 'warning')
            return redirect(url_for('admin.dashboard'))
        
        # Double-check availability
        calendar_service = GoogleCalendarService()
        availability = calendar_service.check_availability(booking.start_date, booking.end_date)
        
        if not availability['available']:
            flash('Booking dates are no longer available', 'error')
            return render_template('admin/approve_conflict.html', 
                                 booking=booking, 
                                 conflicts=availability['conflicts'])
        
        # Create Google Calendar event
        event_summary = f"Rental: {booking.guest_name}"
        event_description = f"""
Booking via Galveston Reservation System

Guest: {booking.guest_name}
Email: {booking.guest_email}
Phone: {booking.guest_phone or 'Not provided'}
Guests: {booking.num_guests}

Special Requests: {booking.special_requests or 'None'}

Booking ID: {booking.id}
        """.strip()
        
        google_event = calendar_service.create_event(
            summary=event_summary,
            start_datetime=booking.start_date,
            end_datetime=booking.end_date,
            description=event_description,
            attendees=[booking.guest_email]
        )
        
        if google_event:
            # Update booking status
            booking.status = 'confirmed'
            booking.approved_at = datetime.utcnow()
            booking.google_event_id = google_event['id']
            
            # Create local calendar event record
            calendar_event = CalendarEvent(
                google_event_id=google_event['id'],
                summary=event_summary,
                description=event_description,
                start_datetime=booking.start_date,
                end_datetime=booking.end_date,
                status='confirmed',
                source='booking_system',
                booking_request_id=booking.id
            )
            
            db.session.add(calendar_event)
            db.session.commit()
            
            # Send confirmation emails
            email_service.send_approval_confirmation(booking)
            email_service.send_booking_confirmed_notification(booking)
            
            flash(f'Booking approved and added to calendar for {booking.guest_name}', 'success')
        else:
            flash('Booking approved but failed to create calendar event', 'warning')
            booking.status = 'approved'
            booking.approved_at = datetime.utcnow()
            db.session.commit()
        
        return redirect(url_for('admin.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error approving booking: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/reject/<token>')
def reject_booking(token):
    """Reject a booking request via email link"""
    try:
        email_service = EmailService()
        token_data = email_service.verify_token(token)
        
        if not token_data or token_data.get('action') != 'reject':
            flash('Invalid or expired rejection link', 'error')
            return redirect(url_for('admin.dashboard'))
        
        booking_id = token_data['booking_id']
        booking = BookingRequest.query.get_or_404(booking_id)
        
        if booking.status != 'pending':
            flash(f'Booking is already {booking.status}', 'warning')
            return redirect(url_for('admin.dashboard'))
        
        return render_template('admin/reject_form.html', booking=booking, token=token)
        
    except Exception as e:
        flash(f'Error processing rejection: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/reject/<token>', methods=['POST'])
def process_rejection(token):
    """Process booking rejection with reason"""
    try:
        email_service = EmailService()
        token_data = email_service.verify_token(token)
        
        if not token_data or token_data.get('action') != 'reject':
            flash('Invalid or expired rejection link', 'error')
            return redirect(url_for('admin.dashboard'))
        
        booking_id = token_data['booking_id']
        booking = BookingRequest.query.get_or_404(booking_id)
        
        rejection_reason = request.form.get('reason', '').strip()
        
        # Update booking status
        booking.status = 'rejected'
        booking.rejected_at = datetime.utcnow()
        booking.rejection_reason = rejection_reason
        
        db.session.commit()
        
        # Send rejection email to guest
        email_service.send_rejection_notification(booking, rejection_reason)
        
        flash(f'Booking rejected for {booking.guest_name}', 'success')
        return redirect(url_for('admin.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error rejecting booking: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/bookings')
def list_bookings():
    """List all booking requests with filtering"""
    status = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    
    query = BookingRequest.query
    
    if status != 'all':
        query = query.filter_by(status=status)
    
    bookings = query.order_by(BookingRequest.created_at.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    
    return render_template('admin/bookings.html', bookings=bookings, current_status=status)

@admin_bp.route('/sync-calendar')
def sync_calendar():
    """Manually trigger calendar synchronization"""
    try:
        calendar_service = GoogleCalendarService()
        events = calendar_service.get_events()
        
        # Update local calendar cache
        # This would be expanded with full sync logic
        
        flash(f'Calendar synced successfully. Found {len(events)} events.', 'success')
        
    except Exception as e:
        flash(f'Calendar sync failed: {str(e)}', 'error')
    
    return redirect(url_for('admin.dashboard'))
