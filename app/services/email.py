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
        # Import config here to avoid circular imports
        from app.config import config
        
        self.admin_email = config.BOOKING_APPROVAL_EMAIL
        self.notification_emails = config.BOOKING_NOTIFICATION_EMAILS
        self.base_url = config.BASE_URL
        
    def _get_serializer(self):
        """Get URL serializer for secure tokens"""
        from app.config import config
        secret_key = config.APPROVAL_TOKEN_SECRET or current_app.config['SECRET_KEY']
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
        
    def send_booking_approval_request(self, booking_request):
        """Send approval request email to admin for new booking"""
        try:
            approval_token = self.generate_approval_token(booking_request.id)
            rejection_token = self.generate_rejection_token(booking_request.id)
            
            approve_url = f"{self.base_url}/api/booking/approve/{approval_token}"
            reject_url = f"{self.base_url}/api/booking/reject/{rejection_token}"
            
            subject = f"BOOKING APPROVAL NEEDED - {booking_request.start_date.strftime('%m/%d')} to {booking_request.end_date.strftime('%m/%d')}"
            
            duration = (booking_request.end_date - booking_request.start_date).days
            
            html_body = f"""
            <h2>🏠 New Booking Request Needs Approval</h2>
            
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3>📅 Booking Details</h3>
                <p><strong>Check-in:</strong> {booking_request.start_date.strftime('%A, %B %d, %Y')} at 3:00 PM</p>
                <p><strong>Check-out:</strong> {booking_request.end_date.strftime('%A, %B %d, %Y')} at 11:00 AM</p>
                <p><strong>Duration:</strong> {duration} nights</p>
                <p><strong>Guests:</strong> {booking_request.num_guests} people</p>
                {f'<p><strong>Special Requests:</strong> {booking_request.special_requests}</p>' if booking_request.special_requests else ''}
            </div>
            
            <div style="background-color: #e9ecef; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3>👤 Guest Contact (Private)</h3>
                <p><strong>Name:</strong> {booking_request.guest_name}</p>
                <p><strong>Email:</strong> {booking_request.guest_email}</p>
                <p><strong>Phone:</strong> {booking_request.guest_phone or 'Not provided'}</p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <h3>⚡ Quick Actions</h3>
                <p>
                    <a href="{approve_url}" 
                       style="background-color: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; margin-right: 15px; display: inline-block; font-weight: bold;">
                       ✅ APPROVE BOOKING
                    </a>
                    
                    <a href="{reject_url}" 
                       style="background-color: #dc3545; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold;">
                       ❌ REJECT BOOKING
                    </a>
                </p>
                <p><small>Links expire in 48 hours</small></p>
            </div>
            
            <p><small>Request ID: {booking_request.id} | Submitted: {booking_request.created_at.strftime('%B %d, %Y at %I:%M %p') if hasattr(booking_request, 'created_at') else 'Just now'}</small></p>
            """
            
            msg = Message(
                subject=subject,
                recipients=['livingbayfront@gmail.com'],
                html=html_body
            )
            
            mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Error sending approval request: {e}")
            return False
    
    def send_booking_notifications(self, booking_request, notification_emails):
        """Send booking notifications to all parties (without guest name for privacy)"""
        try:
            duration = (booking_request.end_date - booking_request.start_date).days
            
            subject = f"Guest Arrival Scheduled - {booking_request.start_date.strftime('%m/%d')} to {booking_request.end_date.strftime('%m/%d')}"
            
            html_body = f"""
            <h2>🏠 Guest Booking Confirmed</h2>
            
            <div style="background-color: #d4edda; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 5px solid #28a745;">
                <h3>📅 Booking Details</h3>
                <p><strong>Check-in:</strong> {booking_request.start_date.strftime('%A, %B %d, %Y')} at 3:00 PM</p>
                <p><strong>Check-out:</strong> {booking_request.end_date.strftime('%A, %B %d, %Y')} at 11:00 AM</p>
                <p><strong>Duration:</strong> {duration} nights</p>
                <p><strong>Number of Guests:</strong> {booking_request.num_guests} people</p>
            </div>
            
            <p><small>Booking ID: {booking_request.id}</small></p>
            """
            
            for email in notification_emails:
                if email.strip():
                    msg = Message(
                        subject=subject,
                        recipients=[email.strip()],
                        html=html_body
                    )
                    mail.send(msg)
            
            return True
            
        except Exception as e:
            print(f"Error sending booking notifications: {e}")
            return False
    
    def send_guest_confirmation(self, booking_request):
        """Send confirmation email to guest"""
        try:
            duration = (booking_request.end_date - booking_request.start_date).days
            
            subject = f"Booking Confirmed! Galveston Bayfront Retreat - {booking_request.start_date.strftime('%m/%d')}"
            
            html_body = f"""
            <h2>🎉 Your Booking is Confirmed!</h2>
            
            <p>Dear {booking_request.guest_name},</p>
            
            <p>Great news! Your booking at the Galveston Bayfront Retreat has been approved and confirmed.</p>
            
            <div style="background-color: #d4edda; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 5px solid #28a745;">
                <h3>📅 Your Reservation Details</h3>
                <p><strong>Property:</strong> Galveston Bayfront Retreat</p>
                <p><strong>Check-in:</strong> {booking_request.start_date.strftime('%A, %B %d, %Y')} at 3:00 PM</p>
                <p><strong>Check-out:</strong> {booking_request.end_date.strftime('%A, %B %d, %Y')} at 11:00 AM</p>
                <p><strong>Duration:</strong> {duration} nights</p>
                <p><strong>Guests:</strong> {booking_request.num_guests} people</p>
            </div>
            
            <div style="background-color: #cce5ff; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 5px solid #007bff;">
                <h3>📍 What's Next?</h3>
                <ul>
                    <li>🔑 <strong>Access Details:</strong> You'll receive check-in instructions 24 hours before arrival</li>
                    <li>📞 <strong>Questions:</strong> Contact us at livingbayfront@gmail.com</li>
                    <li>🏖️ <strong>Local Info:</strong> Galveston tips and recommendations coming soon!</li>
                </ul>
            </div>
            
            <p>We're excited to host you at our beautiful bayfront property! If you have any questions, don't hesitate to reach out.</p>
            
            <p>Best regards,<br>
            The Galveston Bayfront Team</p>
            
            <p><small>Booking Reference: #{booking_request.id}</small></p>
            """
            
            msg = Message(
                subject=subject,
                recipients=[booking_request.guest_email],
                html=html_body
            )
            
            mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Error sending guest confirmation: {e}")
            return False
    
    def send_guest_rejection(self, booking_request):
        """Send rejection email to guest"""
        try:
            subject = f"Booking Update - Galveston Bayfront Retreat"
            
            html_body = f"""
            <h2>Booking Update</h2>
            
            <p>Dear {booking_request.guest_name},</p>
            
            <p>Thank you for your interest in the Galveston Bayfront Retreat.</p>
            
            <div style="background-color: #f8d7da; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 5px solid #dc3545;">
                <p>Unfortunately, we're unable to accommodate your booking request for:</p>
                <ul>
                    <li><strong>Dates:</strong> {booking_request.start_date.strftime('%B %d')} - {booking_request.end_date.strftime('%B %d, %Y')}</li>
                    <li><strong>Guests:</strong> {booking_request.num_guests} people</li>
                </ul>
            </div>
            
            <div style="background-color: #cce5ff; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 5px solid #007bff;">
                <h3>🔄 Alternative Options</h3>
                <ul>
                    <li>📅 <strong>Check our calendar</strong> for available dates at str.ptpsystem.com</li>
                    <li>📞 <strong>Contact us</strong> at livingbayfront@gmail.com for assistance finding alternative dates</li>
                    <li>🔔 <strong>Flexible dates?</strong> Let us know and we can suggest nearby available periods</li>
                </ul>
            </div>
            
            <p>We appreciate your understanding and hope to accommodate you for a future stay!</p>
            
            <p>Best regards,<br>
            The Galveston Bayfront Team</p>
            
            <p><small>Request Reference: #{booking_request.id}</small></p>
            """
            
            msg = Message(
                subject=subject,
                recipients=[booking_request.guest_email],
                html=html_body
            )
            
            mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Error sending guest rejection: {e}")
            return False
