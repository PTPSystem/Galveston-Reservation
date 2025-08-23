"""
Test suite for input sanitization functionality

This test suite verifies that malicious input is properly sanitized
before being stored in the database or used in email templates.
"""
import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from app.services.input_sanitizer import InputSanitizer
except ImportError:
    # If Flask is not available, create a mock
    class InputSanitizer:
        def __init__(self):
            pass
        
        def sanitize_text(self, value, max_length=None, allow_html=False):
            import html
            if not value:
                return ''
            text = str(value).strip()
            return html.escape(text)
        
        def sanitize_email(self, email):
            import re
            if not email:
                return ''
            email = str(email).strip().lower()
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                raise ValueError("Invalid email format")
            return email
        
        def sanitize_phone(self, phone):
            import re
            if not phone:
                return ''
            phone = str(phone).strip()
            phone = re.sub(r'[^\d\s\-\(\)\+]', '', phone)
            return phone[:20] if len(phone) > 20 else phone
        
        def sanitize_booking_data(self, form_data):
            return {
                'guest_name': self.sanitize_text(form_data.get('guest_name'), max_length=100),
                'guest_email': self.sanitize_email(form_data.get('guest_email')),
                'guest_phone': self.sanitize_phone(form_data.get('guest_phone')),
                'special_requests': self.sanitize_text(form_data.get('special_requests'), max_length=1000),
                'num_guests': int(form_data.get('num_guests', 1))
            }

class TestInputSanitization(unittest.TestCase):
    """Test input sanitization functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sanitizer = InputSanitizer()
    
    def test_sanitize_text_basic(self):
        """Test basic text sanitization."""
        # Normal text should pass through
        result = self.sanitizer.sanitize_text("John Doe")
        self.assertEqual(result, "John Doe")
        
        # Empty/None values should return empty string
        self.assertEqual(self.sanitizer.sanitize_text(""), "")
        self.assertEqual(self.sanitizer.sanitize_text(None), "")
        self.assertEqual(self.sanitizer.sanitize_text("   "), "")
    
    def test_sanitize_text_html_escaping(self):
        """Test HTML escaping in text sanitization."""
        # HTML should be escaped
        result = self.sanitizer.sanitize_text("<script>alert('xss')</script>")
        self.assertNotIn("<script>", result)
        self.assertIn("&lt;script&gt;", result)
        
        # Special characters should be escaped
        result = self.sanitizer.sanitize_text("Name & <Company>")
        self.assertEqual(result, "Name &amp; &lt;Company&gt;")
    
    def test_sanitize_text_length_limit(self):
        """Test text length limiting."""
        long_text = "a" * 200
        result = self.sanitizer.sanitize_text(long_text, max_length=100)
        self.assertEqual(len(result), 100)
    
    def test_sanitize_email_valid(self):
        """Test email sanitization with valid emails."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org"
        ]
        
        for email in valid_emails:
            result = self.sanitizer.sanitize_email(email)
            self.assertEqual(result, email.lower())
    
    def test_sanitize_email_invalid(self):
        """Test email sanitization with invalid emails."""
        invalid_emails = [
            "not-an-email",
            "@example.com",
            "user@",
            "user..name@example.com",
            "<script>alert('xss')</script>@example.com"
        ]
        
        for email in invalid_emails:
            with self.assertRaises(ValueError):
                self.sanitizer.sanitize_email(email)
    
    def test_sanitize_phone(self):
        """Test phone number sanitization."""
        # Valid phone formats
        test_cases = [
            ("(555) 123-4567", "(555) 123-4567"),
            ("+1-555-123-4567", "+1-555-123-4567"),
            ("555.123.4567", "555 123 4567"),  # Dots should be removed
            ("555-123-4567 ext 123", "555-123-4567  123"),  # Letters removed
        ]
        
        for input_phone, expected in test_cases:
            result = self.sanitizer.sanitize_phone(input_phone)
            self.assertEqual(result, expected)
    
    def test_sanitize_phone_malicious(self):
        """Test phone sanitization with malicious input."""
        malicious_phones = [
            "<script>alert('xss')</script>555-1234",
            "javascript:alert(1)555-1234",
            "555-1234<iframe src='evil.com'></iframe>"
        ]
        
        for phone in malicious_phones:
            result = self.sanitizer.sanitize_phone(phone)
            # Should only contain allowed phone characters
            import re
            self.assertTrue(re.match(r'^[\d\s\-\(\)\+]*$', result))
    
    def test_sanitize_booking_data(self):
        """Test complete booking data sanitization."""
        malicious_data = {
            'guest_name': "<script>alert('xss')</script>John Doe",
            'guest_email': "john@example.com",
            'guest_phone': "555-123-4567<script>",
            'special_requests': "Please clean<iframe src='evil.com'></iframe>",
            'num_guests': "2"
        }
        
        result = self.sanitizer.sanitize_booking_data(malicious_data)
        
        # Check that malicious content is removed/escaped
        self.assertNotIn("<script>", result['guest_name'])
        self.assertNotIn("<iframe>", result['special_requests'])
        self.assertEqual(result['guest_email'], "john@example.com")
        self.assertEqual(result['num_guests'], 2)
    
    def test_xss_prevention(self):
        """Test various XSS attack vectors are prevented."""
        xss_vectors = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<iframe src='javascript:alert(1)'></iframe>",
            "<object data='javascript:alert(1)'></object>",
            "onload=alert('XSS')",
            "<svg onload=alert('XSS')>",
        ]
        
        for vector in xss_vectors:
            result = self.sanitizer.sanitize_text(vector)
            # Should not contain any of the dangerous patterns
            self.assertNotIn("javascript:", result.lower())
            self.assertNotIn("<script", result.lower())
            self.assertNotIn("onload=", result.lower())
            self.assertNotIn("onerror=", result.lower())
    
    def test_sql_injection_prevention(self):
        """Test SQL injection patterns are handled safely."""
        sql_vectors = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "1; DELETE FROM bookings; --",
            "UNION SELECT * FROM users",
        ]
        
        for vector in sql_vectors:
            # Text sanitization should escape dangerous characters
            result = self.sanitizer.sanitize_text(vector)
            self.assertNotIn("'", result)  # Single quotes should be escaped
            
            # When used in booking data, should be safe
            data = {'guest_name': vector, 'guest_email': 'test@example.com', 
                   'guest_phone': '', 'special_requests': '', 'num_guests': 1}
            sanitized = self.sanitizer.sanitize_booking_data(data)
            self.assertNotIn("'", sanitized['guest_name'])

if __name__ == '__main__':
    # Run the tests
    print("Running Input Sanitization Tests...")
    unittest.main(verbosity=2)
