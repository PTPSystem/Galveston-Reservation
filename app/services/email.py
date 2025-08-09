"""
Email Service for Galveston Reservation System
"""
import os
from flask import current_app, render_template_string
from flask_mail import Message
from app import mail
import secrets
from itsdangerous import URLSafeTimedSerializer

class EmailService:
    """Service for sending emails and managing email workflows"""
    
    def __init__(self):
        self.admin_email = os.getenv('ADMIN_EMAIL', 'admin@ptpsystem.com')
        self.notification_emails = os.getenv('NOTIFICATION_EMAILS', '').split(',')
        self.base_url = os.getenv('BASE_URL', 'https://str.ptpsystem.com')
        
    def _get_serializer(self):
        """Get URL serializer for secure tokens"""
        secret_key = os.getenv('APPROVAL_TOKEN_SECRET', current_app.config['SECRET_KEY'])
        return URLSafeTimedSerializer(secret_key)
    
    def generate_approval_token(self, booking_id):
        """Generate a secure token for booking approval/rejection"""
        serializer = self._get_serializer()
        return serializer.dumps({'booking_id': booking_id, 'action': 'approve'})
    
    def generate_rejection_token(self, booking_id):
        """Generate a secure token for booking rejection"""
        serializer = self._get_serializer()
        return serializer.dumps({'booking_id': booking_id, 'action': 'reject'})
    
    def verify_token(self, token, max_age=48*3600):  # 48 hours default
        """Verify and decode a token"""
        try:
            serializer = self._get_serializer()
            return serializer.loads(token, max_age=max_age)
        except Exception:
            return None
    
    def send_booking_request_notification(self, booking_request):
        """Send notification to admin about new booking request"""
        try:
            approval_token = self.generate_approval_token(booking_request.id)
            rejection_token = self.generate_rejection_token(booking_request.id)
            
            approve_url = f"{self.base_url}/admin/approve/{approval_token}"
            reject_url = f"{self.base_url}/admin/reject/{rejection_token}"
            
            subject = f"New Booking Request - {booking_request.guest_name}"
            
            html_body = f"""
            <h2>New Booking Request</h2>
            
            <h3>Guest Information</h3>
            <p><strong>Name:</strong> {booking_request.guest_name}</p>
            <p><strong>Email:</strong> {booking_request.guest_email}</p>
            <p><strong>Phone:</strong> {booking_request.guest_phone or 'Not provided'}</p>
            
            <h3>Booking Details</h3>
            <p><strong>Check-in:</strong> {booking_request.start_date.strftime('%B %d, %Y at %I:%M %p')}</p>
            <p><strong>Check-out:</strong> {booking_request.end_date.strftime('%B %d, %Y at %I:%M %p')}</p>
            <p><strong>Duration:</strong> {booking_request.duration_days} days</p>
            <p><strong>Number of Guests:</strong> {booking_request.num_guests}</p>
            
            {f'<p><strong>Special Requests:</strong> {booking_request.special_requests}</p>' if booking_request.special_requests else ''}
            
            <h3>Actions</h3>
            <p>
                <a href="{approve_url}" 
                   style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-right: 10px;">
                   ✅ APPROVE BOOKING
                </a>
                
                <a href="{reject_url}" 
                   style="background-color: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                   ❌ REJECT BOOKING
                </a>
            </p>
            
            <p><small>Request ID: {booking_request.id} | Submitted: {booking_request.created_at.strftime('%B %d, %Y at %I:%M %p')}</small></p>
            """
            
            msg = Message(
                subject=subject,
                recipients=[self.admin_email],
                html=html_body
            )
            
            mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Error sending booking notification: {e}")
            return False
    
    def send_approval_confirmation(self, booking_request):
        """Send confirmation email to guest when booking is approved"""
        try:
            subject = f"Booking Approved - Galveston Rental"
            
            html_body = f"""
            <h2>🎉 Your Booking Has Been Approved!</h2>
            
            <p>Hello {booking_request.guest_name},</p>
            
            <p>Great news! Your booking request has been approved.</p>
            
            <h3>Booking Details</h3>
            <p><strong>Check-in:</strong> {booking_request.start_date.strftime('%B %d, %Y at %I:%M %p')}</p>
            <p><strong>Check-out:</strong> {booking_request.end_date.strftime('%B %d, %Y at %I:%M %p')}</p>
            <p><strong>Duration:</strong> {booking_request.duration_days} days</p>
            <p><strong>Number of Guests:</strong> {booking_request.num_guests}</p>
            
            <h3>Next Steps</h3>
            <p>You will receive additional information about check-in procedures, property access, and local recommendations closer to your arrival date.</p>
            
            <h3>Contact Information</h3>
            <p>If you have any questions, please reply to this email or contact us at {self.admin_email}</p>
            
            <p>We look forward to hosting you in Galveston!</p>
            
            <p><small>Booking ID: {booking_request.id}</small></p>
            """
            
            msg = Message(
                subject=subject,
                recipients=[booking_request.guest_email],
                html=html_body
            )
            
            mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Error sending approval confirmation: {e}")
            return False
    
    def send_rejection_notification(self, booking_request, reason=None):
        """Send rejection email to guest when booking is rejected"""
        try:
            subject = f"Booking Request Update - Galveston Rental"
            
            reason_text = f"<p><strong>Reason:</strong> {reason}</p>" if reason else ""
            
            html_body = f"""
            <h2>Booking Request Update</h2>
            
            <p>Hello {booking_request.guest_name},</p>
            
            <p>Thank you for your interest in our Galveston rental property. Unfortunately, we are unable to accommodate your booking request for the following dates:</p>
            
            <p><strong>Requested Dates:</strong> {booking_request.start_date.strftime('%B %d, %Y')} - {booking_request.end_date.strftime('%B %d, %Y')}</p>
            
            {reason_text}
            
            <p>We encourage you to check our availability calendar at <a href="{self.base_url}">str.ptpsystem.com</a> for alternative dates that might work for your stay.</p>
            
            <p>If you have any questions or would like to discuss other options, please don't hesitate to contact us.</p>
            
            <p>Thank you for considering our property, and we hope to host you in the future!</p>
            
            <p>Best regards,<br>Galveston Rental Team</p>
            
            <p><small>Booking ID: {booking_request.id}</small></p>
            """
            
            msg = Message(
                subject=subject,
                recipients=[booking_request.guest_email],
                html=html_body
            )
            
            mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Error sending rejection notification: {e}")
            return False
    
    def send_booking_confirmed_notification(self, booking_request):
        """Send notification to team members when booking is confirmed in Google Calendar"""
        try:
            subject = f"Booking Confirmed in Calendar - {booking_request.guest_name}"
            
            html_body = f"""
            <h2>📅 Booking Added to Google Calendar</h2>
            
            <p>A new booking has been confirmed and added to the BayfrontLiving@gmail.com calendar:</p>
            
            <h3>Guest Information</h3>
            <p><strong>Name:</strong> {booking_request.guest_name}</p>
            <p><strong>Email:</strong> {booking_request.guest_email}</p>
            <p><strong>Phone:</strong> {booking_request.guest_phone or 'Not provided'}</p>
            
            <h3>Booking Details</h3>
            <p><strong>Check-in:</strong> {booking_request.start_date.strftime('%B %d, %Y at %I:%M %p')}</p>
            <p><strong>Check-out:</strong> {booking_request.end_date.strftime('%B %d, %Y at %I:%M %p')}</p>
            <p><strong>Duration:</strong> {booking_request.duration_days} days</p>
            <p><strong>Number of Guests:</strong> {booking_request.num_guests}</p>
            
            {f'<p><strong>Special Requests:</strong> {booking_request.special_requests}</p>' if booking_request.special_requests else ''}
            
            <h3>Workflow Actions Needed</h3>
            <ul>
                <li>Schedule pre-arrival preparation</li>
                <li>Prepare welcome package and instructions</li>
                <li>Coordinate cleaning and turnover schedule</li>
            </ul>
            
            <p><small>Booking ID: {booking_request.id} | Google Event ID: {booking_request.google_event_id}</small></p>
            """
            
            # Send to all notification recipients
            for email in self.notification_emails:
                if email.strip():  # Skip empty emails
                    msg = Message(
                        subject=subject,
                        recipients=[email.strip()],
                        html=html_body
                    )
                    mail.send(msg)
            
            return True
            
        except Exception as e:
            print(f"Error sending booking confirmation notification: {e}")
            return False
    
    def send_sync_alert(self, discrepancies):
        """Send alert about calendar synchronization discrepancies"""
        try:
            subject = f"Calendar Sync Alert - {len(discrepancies)} Discrepancies Found"
            
            discrepancy_list = ""
            for disc in discrepancies[:10]:  # Limit to first 10
                discrepancy_list += f"<li>{disc.get('description', 'Unknown discrepancy')}</li>"
            
            if len(discrepancies) > 10:
                discrepancy_list += f"<li>... and {len(discrepancies) - 10} more</li>"
            
            html_body = f"""
            <h2>⚠️ Calendar Synchronization Alert</h2>
            
            <p>The calendar synchronization process has detected discrepancies between Google Calendar and the external booking source:</p>
            
            <h3>Discrepancies Found ({len(discrepancies)})</h3>
            <ul>
                {discrepancy_list}
            </ul>
            
            <h3>Recommended Actions</h3>
            <ul>
                <li>Review the discrepancies manually</li>
                <li>Update Google Calendar if external bookings are missing</li>
                <li>Verify booking platform synchronization is working</li>
                <li>Check for any cancelled or modified bookings</li>
            </ul>
            
            <p>Please review these discrepancies as soon as possible to ensure accurate availability.</p>
            """
            
            msg = Message(
                subject=subject,
                recipients=[self.admin_email],
                html=html_body
            )
            
            mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Error sending sync alert: {e}")
            return False
