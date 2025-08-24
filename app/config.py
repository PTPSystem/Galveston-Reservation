"""
Galveston Reservation System Configuration
Centralized configuration for all key settings
"""
import os
from typing import List

class Config:
    """Main configuration class for the Galveston Reservation System"""
    
    # =============================================================================
    # GOOGLE CALENDAR INTEGRATION
    # =============================================================================
    
    # Google Service Account Configuration
    GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', '/run/secrets/service-account.json')
    GOOGLE_CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID', 'livingbayfront@gmail.com')
    
    # =============================================================================
    # PROPERTY MANAGEMENT
    # =============================================================================
    
    # Rental Website URLs
    PROPERTY_MANAGEMENT_URL = os.getenv('PROPERTY_MANAGEMENT_URL', 
        'https://www.galvestonislandresortrentals.com/galveston-vacation-rentals/bayfront-retreat')
    
    # Property Details
    PROPERTY_NAME = os.getenv('PROPERTY_NAME', 'Bayfront Retreat')
    PROPERTY_LOCATION = os.getenv('PROPERTY_LOCATION', 'Galveston, Texas')
    MAX_GUESTS = int(os.getenv('MAX_GUESTS', '10'))
    
    # =============================================================================
    # EMAIL NOTIFICATIONS
    # =============================================================================
    
    # Booking Approval Email (who approves bookings)
    BOOKING_APPROVAL_EMAIL = os.getenv('BOOKING_APPROVAL_EMAIL', 'livingbayfront@gmail.com')
    
    # Booking Notification Emails (who gets notified of new bookings)
    BOOKING_NOTIFICATION_EMAILS = os.getenv('BOOKING_NOTIFICATION_EMAILS', 
        'livingbayfront@gmail.com').split(',')
    
    # Administrative Contact
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'livingbayfront@gmail.com')
    
    # Default sender for system emails
    SYSTEM_EMAIL_SENDER = os.getenv('SYSTEM_EMAIL_SENDER', 'livingbayfront@gmail.com')
    
    # =============================================================================
    # APPLICATION SETTINGS
    # =============================================================================
    
    # Application URLs
    APP_URL = os.getenv('APP_URL', 'https://str.ptpsystem.com')
    DOMAIN_NAME = os.getenv('DOMAIN_NAME', 'str.ptpsystem.com')
    
    # BASE_URL can be overridden independently from APP_URL (for staging)
    BASE_URL = os.getenv('BASE_URL', APP_URL)
    
    # Booking Configuration
    BOOKING_ADVANCE_DAYS = int(os.getenv('BOOKING_ADVANCE_DAYS', '365'))  # How far ahead bookings can be made
    MIN_STAY_NIGHTS = int(os.getenv('MIN_STAY_NIGHTS', '2'))
    MAX_STAY_NIGHTS = int(os.getenv('MAX_STAY_NIGHTS', '30'))
    
    # Calendar Sync Settings
    CALENDAR_SYNC_MONTHS_AHEAD = int(os.getenv('CALENDAR_SYNC_MONTHS_AHEAD', '6'))
    CALENDAR_SYNC_INTERVAL_HOURS = int(os.getenv('CALENDAR_SYNC_INTERVAL_HOURS', '2'))
    
    # =============================================================================
    # SECURITY & TOKENS
    # =============================================================================
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-super-secret-key-here-change-this')
    
    # Booking Approval Tokens
    APPROVAL_TOKEN_SECRET = os.getenv('APPROVAL_TOKEN_SECRET', 'NfjpI79JUbvtVe6VgqQOwig6RrE0XYmUdzJ7K0DU9wo')
    TOKEN_EXPIRATION_HOURS = int(os.getenv('TOKEN_EXPIRATION_HOURS', '48'))
    
    # =============================================================================
    # DATABASE CONFIGURATION
    # =============================================================================
    
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+psycopg2://app:app_pass@db:5432/galveston')
    
    # =============================================================================
    # EMAIL SERVER CONFIGURATION
    # =============================================================================
    
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'your_email@gmail.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'your_app_password')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'your_email@gmail.com')
    
    # =============================================================================
    # ENVIRONMENT & DEBUG
    # =============================================================================
    
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # =============================================================================
    # HELPER METHODS
    # =============================================================================
    
    @classmethod
    def get_notification_emails(cls) -> List[str]:
        """Get all notification emails as a clean list"""
        emails = []
        for email in cls.BOOKING_NOTIFICATION_EMAILS:
            email = email.strip()
            if email and '@' in email:
                emails.append(email)
        return emails
    
    @classmethod
    def get_all_admin_emails(cls) -> List[str]:
        """Get all admin-related emails (approval + notifications + admin)"""
        emails = set()
        emails.add(cls.BOOKING_APPROVAL_EMAIL)
        emails.add(cls.ADMIN_EMAIL)
        emails.update(cls.get_notification_emails())
        return [email for email in emails if email and '@' in email]
    
    @classmethod
    def validate_config(cls) -> List[str]:
        """Validate configuration and return any issues"""
        issues = []
        
        # Check required emails
        if not cls.BOOKING_APPROVAL_EMAIL or '@' not in cls.BOOKING_APPROVAL_EMAIL:
            issues.append("BOOKING_APPROVAL_EMAIL is not properly configured")
        
        if not cls.GOOGLE_CALENDAR_ID or '@' not in cls.GOOGLE_CALENDAR_ID:
            issues.append("GOOGLE_CALENDAR_ID is not properly configured")
        
        if not cls.get_notification_emails():
            issues.append("BOOKING_NOTIFICATION_EMAILS is not properly configured")
        
        # Check URLs
        if not cls.PROPERTY_MANAGEMENT_URL.startswith('http'):
            issues.append("PROPERTY_MANAGEMENT_URL must be a valid HTTP/HTTPS URL")
        
        if not cls.APP_URL.startswith('http'):
            issues.append("APP_URL must be a valid HTTP/HTTPS URL")
        
        # Check credentials path
        if not os.path.exists(cls.GOOGLE_CREDENTIALS_PATH):
            issues.append(f"Google credentials file not found: {cls.GOOGLE_CREDENTIALS_PATH}")
        
        return issues
    
    @classmethod
    def print_config_summary(cls):
        """Print a summary of the current configuration (without sensitive data)"""
        print("=== Galveston Reservation System Configuration ===")
        print(f"Property: {cls.PROPERTY_NAME} in {cls.PROPERTY_LOCATION}")
        print(f"Max Guests: {cls.MAX_GUESTS}")
        print(f"App URL: {cls.APP_URL}")
        print(f"Property Management URL: {cls.PROPERTY_MANAGEMENT_URL}")
        print(f"Google Calendar: {cls.GOOGLE_CALENDAR_ID}")
        print(f"Approval Email: {cls.BOOKING_APPROVAL_EMAIL}")
        print(f"Notification Emails: {', '.join(cls.get_notification_emails())}")
        print(f"Admin Email: {cls.ADMIN_EMAIL}")
        print(f"Calendar Sync: Every {cls.CALENDAR_SYNC_INTERVAL_HOURS} hours, {cls.CALENDAR_SYNC_MONTHS_AHEAD} months ahead")
        print(f"Environment: {cls.FLASK_ENV}")
        
        # Validation
        issues = cls.validate_config()
        if issues:
            print("\n⚠️  Configuration Issues:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("\n✅ Configuration is valid!")
        print("=" * 50)
    
    def get_full_property_url(self):
        """Get the full property management URL"""
        return self.PROPERTY_MANAGEMENT_URL
    
    def get_notification_email_list(self):
        """Get the list of notification emails"""
        return self.get_notification_emails()
    
    def validate_required_settings(self):
        """Validate that all required settings are present (instance method)"""
        issues = self.validate_config()
        return {
            'valid': len(issues) == 0,
            'missing': issues
        }

# Create a default instance for easy importing
config = Config()
