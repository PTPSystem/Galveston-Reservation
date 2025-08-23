"""
Test cases for email input sanitization to prevent XSS vulnerabilities.
"""
import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.email import EmailService


class TestEmailInputSanitization(unittest.TestCase):
    """Test input sanitization in email service"""
    
    def setUp(self):
        """Set up test fixtures"""
        with patch('app.services.email.mail'):
            self.email_service = EmailService()
    
    def test_sanitize_input_basic(self):
        """Test basic HTML escaping"""
        # Test normal input
        result = self.email_service._sanitize_input("John Doe")
        self.assertEqual(result, "John Doe")
        
        # Test empty input
        result = self.email_service._sanitize_input("")
        self.assertEqual(result, "")
        
        # Test None input
        result = self.email_service._sanitize_input(None)
        self.assertEqual(result, "")
    
    def test_sanitize_input_html_injection(self):
        """Test HTML injection prevention"""
        malicious_inputs = [
            "<script>alert('XSS')</script>",
            "<img src='x' onerror='alert(1)'>",
            "<svg onload='alert(1)'>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(1)'></iframe>",
            "'>alert('XSS')<'",
            "& <script>alert('XSS')</script>",
        ]
        
        expected_outputs = [
            "&lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;",
            "&lt;img src=&#x27;x&#x27; onerror=&#x27;alert(1)&#x27;&gt;",
            "&lt;svg onload=&#x27;alert(1)&#x27;&gt;",
            "javascript:alert(&#x27;XSS&#x27;)",
            "&lt;iframe src=&#x27;javascript:alert(1)&#x27;&gt;&lt;/iframe&gt;",
            "&#x27;&gt;alert(&#x27;XSS&#x27;)&lt;&#x27;",
            "&amp; &lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;",
        ]
        
        for malicious_input, expected in zip(malicious_inputs, expected_outputs):
            with self.subTest(input=malicious_input):
                result = self.email_service._sanitize_input(malicious_input)
                self.assertEqual(result, expected)
                # Ensure no script tags remain
                self.assertNotIn("<script", result.lower())
                self.assertNotIn("javascript:", result.lower())
    
    def test_sanitize_booking_data(self):
        """Test sanitization of booking request data"""
        # Create mock booking request with malicious data
        mock_booking = Mock()
        mock_booking.guest_name = "<script>alert('XSS')</script>John"
        mock_booking.guest_email = "test@example.com<script>alert(1)</script>"
        mock_booking.guest_phone = "123-456-7890<img src='x' onerror='alert(1)'>"
        mock_booking.special_requests = "Nice view<script>document.cookie='stolen'</script>"
        
        sanitized = self.email_service._sanitize_booking_data(mock_booking)
        
        # Check that all fields are sanitized
        self.assertEqual(
            sanitized['guest_name'], 
            "&lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;John"
        )
        self.assertEqual(
            sanitized['guest_email'],
            "test@example.com&lt;script&gt;alert(1)&lt;/script&gt;"
        )
        self.assertEqual(
            sanitized['guest_phone'],
            "123-456-7890&lt;img src=&#x27;x&#x27; onerror=&#x27;alert(1)&#x27;&gt;"
        )
        self.assertEqual(
            sanitized['special_requests'],
            "Nice view&lt;script&gt;document.cookie=&#x27;stolen&#x27;&lt;/script&gt;"
        )
        
        # Ensure no dangerous content remains
        for field_name, field_value in sanitized.items():
            self.assertNotIn("<script", field_value.lower())
            self.assertNotIn("javascript:", field_value.lower())
            self.assertNotIn("onerror=", field_value.lower())
    
    def test_validation_email_format(self):
        """Test email format validation"""
        mock_booking = Mock()
        mock_booking.guest_name = "John Doe"
        mock_booking.guest_email = "invalid-email"
        mock_booking.start_date = Mock()
        mock_booking.end_date = Mock()
        mock_booking.num_guests = 2
        
        # Should raise ValueError for invalid email
        with self.assertRaises(ValueError) as context:
            self.email_service._validate_booking_request(mock_booking)
        
        self.assertIn("Invalid email format", str(context.exception))
    
    def test_validation_required_fields(self):
        """Test required field validation"""
        mock_booking = Mock()
        # Missing guest_name
        mock_booking.guest_email = "test@example.com"
        mock_booking.start_date = Mock()
        mock_booking.end_date = Mock()
        mock_booking.num_guests = 2
        
        # Should raise ValueError for missing required field
        with self.assertRaises(ValueError) as context:
            self.email_service._validate_booking_request(mock_booking)
        
        self.assertIn("Guest name is required", str(context.exception))
    
    def test_validation_length_limits(self):
        """Test field length validation"""
        mock_booking = Mock()
        mock_booking.guest_name = "A" * 101  # Too long
        mock_booking.guest_email = "test@example.com"
        mock_booking.start_date = Mock()
        mock_booking.end_date = Mock()
        mock_booking.num_guests = 2
        mock_booking.special_requests = "A" * 1001  # Too long
        
        # Should raise ValueError for field too long
        with self.assertRaises(ValueError) as context:
            self.email_service._validate_booking_request(mock_booking)
        
        error_message = str(context.exception)
        self.assertIn("Guest name must be 100 characters or less", error_message)
        self.assertIn("Special requests must be 1000 characters or less", error_message)
    
    def test_validation_guest_count(self):
        """Test guest count validation"""
        mock_booking = Mock()
        mock_booking.guest_name = "John Doe"
        mock_booking.guest_email = "test@example.com"
        mock_booking.start_date = Mock()
        mock_booking.end_date = Mock()
        mock_booking.num_guests = 25  # Too many guests
        
        # Should raise ValueError for too many guests
        with self.assertRaises(ValueError) as context:
            self.email_service._validate_booking_request(mock_booking)
        
        self.assertIn("Number of guests exceeds maximum capacity", str(context.exception))


if __name__ == '__main__':
    unittest.main()
