"""
Input Sanitization Service for Galveston Reservation System

This service provides comprehensive input sanitization to prevent XSS attacks,
data corruption, and ensure data integrity across the application.
"""
import html
import re
from typing import Optional, Any, Dict
from flask import current_app

class InputSanitizer:
    """Service for sanitizing user input before database storage and processing."""
    
    def __init__(self):
        # Common malicious patterns to detect
        self.malicious_patterns = [
            r'<script[^>]*>.*?</script>',  # Script tags
            r'javascript:',               # JavaScript protocol
            r'on\w+\s*=',                # Event handlers (onclick, onload, etc.)
            r'expression\s*\(',          # CSS expressions
            r'<iframe[^>]*>.*?</iframe>', # Iframe tags
            r'<object[^>]*>.*?</object>', # Object tags
            r'<embed[^>]*>.*?</embed>',   # Embed tags
        ]
        
        # Compile regex patterns for performance
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE | re.DOTALL) 
                                for pattern in self.malicious_patterns]
    
    def sanitize_text(self, value: Any, max_length: Optional[int] = None, 
                     allow_html: bool = False) -> str:
        """
        Sanitize text input for safe storage and display.
        
        Args:
            value: The input value to sanitize
            max_length: Maximum allowed length (None for no limit)
            allow_html: Whether to allow basic HTML tags
            
        Returns:
            str: Sanitized and safe text
        """
        if not value:
            return ''
        
        # Convert to string
        text = str(value).strip()
        
        # Remove null bytes and control characters
        text = self._remove_control_characters(text)
        
        # Check for malicious patterns
        if self._contains_malicious_content(text):
            current_app.logger.warning(f"Malicious content detected in input: {text[:100]}...")
            # Strip all potentially dangerous content
            text = self._strip_dangerous_content(text)
        
        # HTML escape unless explicitly allowing HTML
        if not allow_html:
            text = html.escape(text)
        else:
            text = self._sanitize_html(text)
        
        # Truncate if max_length specified
        if max_length and len(text) > max_length:
            text = text[:max_length].rstrip()
        
        return text
    
    def sanitize_email(self, email: Any) -> str:
        """
        Sanitize and validate email address.
        
        Args:
            email: Email address to sanitize
            
        Returns:
            str: Sanitized email address
            
        Raises:
            ValueError: If email format is invalid
        """
        if not email:
            return ''
        
        email = str(email).strip().lower()
        
        # Remove dangerous characters
        email = self._remove_control_characters(email)
        
        # Basic email format validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")
        
        # Additional security checks
        if self._contains_malicious_content(email):
            raise ValueError("Invalid characters in email address")
        
        return email
    
    def sanitize_phone(self, phone: Any) -> str:
        """
        Sanitize phone number input.
        
        Args:
            phone: Phone number to sanitize
            
        Returns:
            str: Sanitized phone number
        """
        if not phone:
            return ''
        
        phone = str(phone).strip()
        
        # Remove control characters
        phone = self._remove_control_characters(phone)
        
        # Allow only digits, spaces, hyphens, parentheses, and plus sign
        phone = re.sub(r'[^\d\s\-\(\)\+]', '', phone)
        
        # Limit length
        if len(phone) > 20:
            phone = phone[:20]
        
        return phone
    
    def sanitize_booking_data(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize all booking form data.
        
        Args:
            form_data: Dictionary of form data
            
        Returns:
            Dict[str, Any]: Sanitized form data
        """
        sanitized = {}
        
        # Guest name - no HTML, max 100 chars
        sanitized['guest_name'] = self.sanitize_text(
            form_data.get('guest_name'), 
            max_length=100, 
            allow_html=False
        )
        
        # Guest email - validate and sanitize
        try:
            sanitized['guest_email'] = self.sanitize_email(form_data.get('guest_email'))
        except ValueError as e:
            raise ValueError(f"Invalid email: {e}")
        
        # Guest phone - sanitize phone format
        sanitized['guest_phone'] = self.sanitize_phone(form_data.get('guest_phone'))
        
        # Special requests - no HTML, max 1000 chars
        sanitized['special_requests'] = self.sanitize_text(
            form_data.get('special_requests'), 
            max_length=1000, 
            allow_html=False
        )
        
        # Number of guests - ensure integer and within bounds
        try:
            num_guests = int(form_data.get('num_guests', 1))
            if num_guests < 1 or num_guests > 20:
                raise ValueError("Number of guests must be between 1 and 20")
            sanitized['num_guests'] = num_guests
        except (ValueError, TypeError):
            raise ValueError("Invalid number of guests")
        
        # Copy non-text fields directly (dates will be handled separately)
        for key in ['start_date', 'end_date']:
            if key in form_data:
                sanitized[key] = form_data[key]
        
        return sanitized
    
    def _remove_control_characters(self, text: str) -> str:
        """Remove null bytes and control characters."""
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Remove other dangerous control characters but keep normal whitespace
        return re.sub(r'[\x01-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    def _contains_malicious_content(self, text: str) -> bool:
        """Check if text contains potentially malicious content."""
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                return True
        return False
    
    def _strip_dangerous_content(self, text: str) -> str:
        """Strip dangerous content from text."""
        # Remove script tags and their content
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove event handlers
        text = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', text, flags=re.IGNORECASE)
        text = re.sub(r'on\w+\s*=\s*[^>\s]+', '', text, flags=re.IGNORECASE)
        
        # Remove javascript: protocol
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        
        # Remove other dangerous tags
        dangerous_tags = ['iframe', 'object', 'embed', 'form', 'input', 'textarea', 'select']
        for tag in dangerous_tags:
            text = re.sub(f'<{tag}[^>]*>.*?</{tag}>', '', text, flags=re.IGNORECASE | re.DOTALL)
            text = re.sub(f'<{tag}[^>]*/?>', '', text, flags=re.IGNORECASE)
        
        return text
    
    def _sanitize_html(self, text: str) -> str:
        """Sanitize HTML while allowing safe tags."""
        # For now, just escape everything since we don't need HTML in user input
        # In the future, could use a library like bleach for more sophisticated HTML sanitization
        return html.escape(text)

# Global instance for easy import
input_sanitizer = InputSanitizer()
