# GitHub Copilot Instructions for Galveston Reservation System

## Project Overview
This is a Flask-based vacation rental booking system for Galveston properties. The system handles booking requests, calendar synchronization with Google Calendar, email notifications, and admin approval workflows.

## Core Principles

### 1. Maintainability First
- Write self-documenting code with clear variable and function names
- Use type hints for all function parameters and return values
- Include comprehensive docstrings following Google style
- Prefer explicit over implicit code
- Keep functions small and focused (max 20-25 lines)
- Use dependency injection for better testability

### 2. Industry Standard Packages
Always prefer established, well-maintained packages:

**Core Framework & Extensions:**
- `Flask` - Web framework
- `Flask-SQLAlchemy` - Database ORM
- `Flask-Mail` - Email handling
- `Flask-WTF` - Form handling and CSRF protection
- `Flask-Login` - Authentication
- `Flask-Migrate` - Database migrations

**Security & Validation:**
- `itsdangerous` - Secure token generation (already in use)
- `WTForms` - Form validation
- `marshmallow` - Data serialization/validation
- `bcrypt` - Password hashing
- `python-dotenv` - Environment variable management

**API & External Services:**
- `google-api-python-client` - Google Calendar integration
- `requests` - HTTP client
- `pydantic` - Data validation and settings management

**Utilities:**
- `python-dateutil` - Date/time handling
- `pytz` - Timezone handling
- `celery` - Background task processing
- `redis` - Caching and session storage

### 3. Code Structure Standards

#### Class Design
```python
class EmailService:
    """Service for handling all email operations.
    
    This class encapsulates email sending, template rendering,
    and security token generation for the booking system.
    """
    
    def __init__(self, config: Config, mail: Mail) -> None:
        self._config = config
        self._mail = mail
        self._validate_configuration()
    
    def send_booking_notification(
        self, 
        booking: BookingRequest,
        admin_email: str
    ) -> bool:
        """Send booking notification to admin.
        
        Args:
            booking: The booking request to notify about
            admin_email: Admin email address
            
        Returns:
            True if email sent successfully, False otherwise
            
        Raises:
            ValidationError: If booking data is invalid
        """
        # Implementation here
```

#### Error Handling
```python
# Use specific exceptions
class BookingValidationError(ValueError):
    """Raised when booking data fails validation."""
    pass

class EmailDeliveryError(Exception):
    """Raised when email cannot be delivered."""
    pass

# Handle errors explicitly
try:
    booking = self._validate_booking(booking_data)
    self._send_notification(booking)
except BookingValidationError as e:
    logger.error(f"Invalid booking data: {e}")
    return False, str(e)
except EmailDeliveryError as e:
    logger.error(f"Email delivery failed: {e}")
    return False, "Failed to send notification"
```

#### Configuration Management
```python
# Use environment variables with defaults
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class EmailConfig:
    """Email service configuration."""
    smtp_server: str = os.getenv('SMTP_SERVER', 'localhost')
    smtp_port: int = int(os.getenv('SMTP_PORT', '587'))
    username: Optional[str] = os.getenv('SMTP_USERNAME')
    password: Optional[str] = os.getenv('SMTP_PASSWORD')
    use_tls: bool = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
    
    def __post_init__(self):
        if not self.username or not self.password:
            raise ValueError("SMTP credentials must be provided")
```

### 4. Security Best Practices

#### Input Validation
```python
from marshmallow import Schema, fields, validate

class BookingRequestSchema(Schema):
    """Schema for validating booking requests."""
    guest_name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100)
    )
    guest_email = fields.Email(required=True)
    start_date = fields.DateTime(required=True)
    end_date = fields.DateTime(required=True)
    num_guests = fields.Int(
        required=True,
        validate=validate.Range(min=1, max=20)
    )
    special_requests = fields.Str(
        validate=validate.Length(max=1000),
        allow_none=True
    )
```

#### Secure Token Handling
```python
from itsdangerous import URLSafeTimedSerializer, BadSignature
import secrets

class TokenService:
    """Service for managing secure tokens."""
    
    def __init__(self, secret_key: str) -> None:
        if len(secret_key) < 32:
            raise ValueError("Secret key must be at least 32 characters")
        self._serializer = URLSafeTimedSerializer(secret_key)
    
    def generate_token(self, data: dict, salt: str = None) -> str:
        """Generate a secure token for the given data."""
        return self._serializer.dumps(data, salt=salt)
    
    def verify_token(
        self, 
        token: str, 
        max_age: int = 3600,
        salt: str = None
    ) -> Optional[dict]:
        """Verify and decode a token."""
        try:
            return self._serializer.loads(token, max_age=max_age, salt=salt)
        except BadSignature:
            return None
```

### 5. Testing Standards

#### Unit Tests
```python
import pytest
from unittest.mock import Mock, patch

class TestEmailService:
    """Test suite for EmailService."""
    
    @pytest.fixture
    def email_service(self):
        """Create EmailService instance for testing."""
        config = Mock()
        config.SMTP_SERVER = 'smtp.test.com'
        mail = Mock()
        return EmailService(config, mail)
    
    def test_send_booking_notification_success(self, email_service):
        """Test successful booking notification sending."""
        booking = Mock()
        booking.guest_name = "John Doe"
        booking.guest_email = "john@example.com"
        
        result = email_service.send_booking_notification(booking, "admin@test.com")
        
        assert result is True
        email_service._mail.send.assert_called_once()
```

### 6. Database Best Practices

#### Model Design
```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from typing import Optional

db = SQLAlchemy()

class BookingRequest(db.Model):
    """Model for booking requests."""
    
    __tablename__ = 'booking_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    guest_name = db.Column(db.String(100), nullable=False)
    guest_email = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    num_guests = db.Column(db.Integer, nullable=False)
    special_requests = db.Column(db.Text)
    status = db.Column(
        db.Enum('pending', 'approved', 'rejected', name='booking_status'),
        default='pending'
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    
    def __repr__(self) -> str:
        return f"<BookingRequest {self.id}: {self.guest_name}>"
    
    @property
    def duration_days(self) -> int:
        """Calculate booking duration in days."""
        return (self.end_date - self.start_date).days
```

### 7. Logging Standards

```python
import logging
import json
from datetime import datetime
from typing import Any, Dict

class StructuredLogger:
    """Structured logger for consistent log formatting."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log_event(
        self, 
        level: str, 
        event: str, 
        **kwargs: Any
    ) -> None:
        """Log a structured event."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'event': event,
            **kwargs
        }
        
        getattr(self.logger, level.lower())(json.dumps(log_data))
```

## Code Review Checklist

When suggesting code changes, ensure:

- [ ] Type hints are present and accurate
- [ ] Docstrings follow Google style guide
- [ ] Error handling is explicit and appropriate
- [ ] Security considerations are addressed
- [ ] Code is testable (dependency injection used)
- [ ] Industry standard packages are preferred
- [ ] Configuration is externalized
- [ ] Logging is structured and meaningful
- [ ] Database queries are optimized
- [ ] Input validation is comprehensive

## Performance Considerations

- Use database indexes for frequently queried fields
- Implement caching for expensive operations
- Use background tasks for time-consuming operations
- Optimize database queries (avoid N+1 problems)
- Use pagination for large result sets

## Security Reminders

- Never commit secrets to version control
- Validate all user input
- Use parameterized queries
- Implement rate limiting
- Use HTTPS in production
- Keep dependencies updated
- Follow principle of least privilege

---

*This instruction set should guide all code suggestions to maintain consistency, security, and maintainability across the Galveston Reservation System.*
