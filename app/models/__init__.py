"""
Database Models for Galveston Reservation System
"""
from datetime import datetime
from app import db

class BookingRequest(db.Model):
    """Model for booking requests submitted by users"""
    __tablename__ = 'booking_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Guest Information
    guest_name = db.Column(db.String(100), nullable=False)
    guest_email = db.Column(db.String(120), nullable=False)
    guest_phone = db.Column(db.String(20), nullable=True)
    
    # Booking Details
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    num_guests = db.Column(db.Integer, default=1)
    special_requests = db.Column(db.Text, nullable=True)
    
    # Status and Workflow
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, confirmed, cancelled
    approval_token = db.Column(db.String(255), unique=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = db.Column(db.DateTime, nullable=True)
    rejected_at = db.Column(db.DateTime, nullable=True)
    
    # Google Calendar Integration
    google_event_id = db.Column(db.String(255), nullable=True)
    
    def __repr__(self):
        return f'<BookingRequest {self.guest_name} {self.start_date} - {self.end_date}>'
    
    @property
    def duration_days(self):
        """Calculate the number of days for the booking"""
        return (self.end_date - self.start_date).days
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'guest_name': self.guest_name,
            'guest_email': self.guest_email,
            'guest_phone': self.guest_phone,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'num_guests': self.num_guests,
            'special_requests': self.special_requests,
            'status': self.status,
            'duration_days': self.duration_days,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class CalendarEvent(db.Model):
    """Model to cache Google Calendar events for availability checking"""
    __tablename__ = 'calendar_events'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Google Calendar Details
    google_event_id = db.Column(db.String(255), unique=True, nullable=False)
    summary = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    # Event Timing
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    
    # Event Properties
    status = db.Column(db.String(20), nullable=True)  # confirmed, tentative, cancelled
    source = db.Column(db.String(20), default='google')  # google, external, manual
    
    # Booking Association
    booking_request_id = db.Column(db.Integer, db.ForeignKey('booking_requests.id'), nullable=True)
    booking_request = db.relationship('BookingRequest', backref='calendar_event')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_synced = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CalendarEvent {self.summary} {self.start_datetime} - {self.end_datetime}>'
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'google_event_id': self.google_event_id,
            'summary': self.summary,
            'description': self.description,
            'start_datetime': self.start_datetime.isoformat(),
            'end_datetime': self.end_datetime.isoformat(),
            'status': self.status,
            'source': self.source,
            'booking_request_id': self.booking_request_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class SyncLog(db.Model):
    """Model to track calendar synchronization runs"""
    __tablename__ = 'sync_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Sync Details
    sync_type = db.Column(db.String(50), nullable=False)  # calendar_sync, external_check
    status = db.Column(db.String(20), nullable=False)     # success, error, warning
    
    # Results
    events_processed = db.Column(db.Integer, default=0)
    events_added = db.Column(db.Integer, default=0)
    events_updated = db.Column(db.Integer, default=0)
    events_removed = db.Column(db.Integer, default=0)
    discrepancies_found = db.Column(db.Integer, default=0)
    
    # Messages and Errors
    message = db.Column(db.Text, nullable=True)
    error_details = db.Column(db.Text, nullable=True)
    
    # Timestamps
    started_at = db.Column(db.DateTime, nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SyncLog {self.sync_type} {self.status} {self.started_at}>'
