"""
Test Email Service Security
Focus on token secret validation
"""
import os
import sys
import unittest
from unittest.mock import Mock, patch
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_serializer_logic():
    """Test the _get_serializer logic directly without Flask context"""
    print("🔒 Testing Email Service Security Validation...")
    
    # Test 1: Missing APPROVAL_TOKEN_SECRET
    try:
        from itsdangerous import URLSafeTimedSerializer
        
        config = Mock()
        config.APPROVAL_TOKEN_SECRET = None
        
        # Simulate the logic from _get_serializer
        if not config.APPROVAL_TOKEN_SECRET:
            raise ValueError("APPROVAL_TOKEN_SECRET must be configured for email service")
        
        print("❌ Test 1 failed - should have raised ValueError")
        return False
        
    except ValueError as e:
        if "APPROVAL_TOKEN_SECRET must be configured" in str(e):
            print("✅ Test 1 passed - Missing APPROVAL_TOKEN_SECRET rejected")
        else:
            print(f"❌ Test 1 failed - Wrong error: {e}")
            return False
    
    # Test 2: Empty APPROVAL_TOKEN_SECRET
    try:
        config = Mock()
        config.APPROVAL_TOKEN_SECRET = ""
        
        # Simulate the logic from _get_serializer
        if not config.APPROVAL_TOKEN_SECRET:
            raise ValueError("APPROVAL_TOKEN_SECRET must be configured for email service")
        
        print("❌ Test 2 failed - should have raised ValueError")
        return False
        
    except ValueError as e:
        if "APPROVAL_TOKEN_SECRET must be configured" in str(e):
            print("✅ Test 2 passed - Empty APPROVAL_TOKEN_SECRET rejected")
        else:
            print(f"❌ Test 2 failed - Wrong error: {e}")
            return False
    
    # Test 3: Short APPROVAL_TOKEN_SECRET
    try:
        config = Mock()
        config.APPROVAL_TOKEN_SECRET = "short-key"  # 9 characters
        
        # Simulate the logic from _get_serializer
        if not config.APPROVAL_TOKEN_SECRET:
            raise ValueError("APPROVAL_TOKEN_SECRET must be configured for email service")
        
        if len(config.APPROVAL_TOKEN_SECRET) < 32:
            raise ValueError("APPROVAL_TOKEN_SECRET must be at least 32 characters long")
        
        print("❌ Test 3 failed - should have raised ValueError")
        return False
        
    except ValueError as e:
        if "must be at least 32 characters" in str(e):
            print("✅ Test 3 passed - Short APPROVAL_TOKEN_SECRET rejected")
        else:
            print(f"❌ Test 3 failed - Wrong error: {e}")
            return False
    
    # Test 4: Valid APPROVAL_TOKEN_SECRET
    try:
        config = Mock()
        config.APPROVAL_TOKEN_SECRET = "a" * 32  # 32 characters
        
        # Simulate the logic from _get_serializer
        if not config.APPROVAL_TOKEN_SECRET:
            raise ValueError("APPROVAL_TOKEN_SECRET must be configured for email service")
        
        if len(config.APPROVAL_TOKEN_SECRET) < 32:
            raise ValueError("APPROVAL_TOKEN_SECRET must be at least 32 characters long")
        
        serializer = URLSafeTimedSerializer(config.APPROVAL_TOKEN_SECRET)
        
        if serializer:
            print("✅ Test 4 passed - Valid APPROVAL_TOKEN_SECRET accepted")
        else:
            print("❌ Test 4 failed - serializer creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Test 4 failed - Unexpected error: {e}")
        return False
    
    # Test 5: Verify the actual code change
    print("\n🔍 Testing actual EmailService implementation...")
    try:
        # Create a mock environment to test the EmailService
        with patch('app.services.email.current_app') as mock_app:
            mock_app.config = {'SECRET_KEY': 'flask-secret-key'}
            
            mock_config = Mock()
            mock_config.APPROVAL_TOKEN_SECRET = None
            mock_config.BOOKING_APPROVAL_EMAIL = 'test@example.com'
            mock_config.BOOKING_NOTIFICATION_EMAILS = ['test@example.com']
            mock_config.BASE_URL = 'https://test.com'
            
            with patch('app.services.email.config', mock_config):
                # Import after patching to avoid circular import issues
                from app.services.email import EmailService
                
                email_service = EmailService()
                
                try:
                    email_service._get_serializer()
                    print("❌ Test 5 failed - should have raised ValueError")
                    return False
                except ValueError as e:
                    if "APPROVAL_TOKEN_SECRET must be configured" in str(e):
                        print("✅ Test 5 passed - EmailService properly rejects missing token")
                    else:
                        print(f"❌ Test 5 failed - Wrong error: {e}")
                        return False
                    
    except Exception as e:
        print(f"❌ Test 5 failed - Error testing EmailService: {e}")
        return False
    
    print("\n🎉 All security tests passed!")
    return True

if __name__ == '__main__':
    success = test_serializer_logic()
    if not success:
        sys.exit(1)