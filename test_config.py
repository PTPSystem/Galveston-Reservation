#!/usr/bin/env python3
"""
Test script to verify the centralized configuration works correctly
"""
import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_config():
    """Test the centralized configuration"""
    print("Testing centralized configuration...")
    
    try:
        # Import the config module directly to avoid Flask dependencies
        sys.path.insert(0, str(Path(__file__).parent / 'app'))
        import config as config_module
        
        # Create an instance of the Config class
        config = config_module.Config()
        print("✓ Successfully imported and instantiated Config class")
        
        # Test Google Calendar configuration
        print(f"Google Calendar ID: {config.GOOGLE_CALENDAR_ID}")
        print(f"Google Credentials Path: {config.GOOGLE_CREDENTIALS_PATH}")
        
        # Test Property Management configuration
        print(f"Property Management URL: {config.PROPERTY_MANAGEMENT_URL}")
        print(f"Property Name: {config.PROPERTY_NAME}")
        print(f"Max Guests: {config.MAX_GUESTS}")
        
        # Test Email configuration
        print(f"Booking Approval Email: {config.BOOKING_APPROVAL_EMAIL}")
        print(f"Booking Notification Emails: {config.BOOKING_NOTIFICATION_EMAILS}")
        print(f"Admin Email: {config.ADMIN_EMAIL}")
        
        # Test Application URLs
        print(f"App URL: {config.APP_URL}")
        print(f"Base URL (alias): {config.BASE_URL}")
        print(f"Domain Name: {config.DOMAIN_NAME}")
        
        # Test helper methods
        print(f"Full Property URL: {config.get_full_property_url()}")
        print(f"Email List: {config.get_notification_email_list()}")
        
        # Test validation
        validation_result = config.validate_required_settings()
        if validation_result['valid']:
            print("✓ All required settings are present")
        else:
            print(f"✗ Missing required settings: {validation_result['missing']}")
        
        print("\n✓ Configuration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("CENTRALIZED CONFIGURATION TEST")
    print("=" * 60)
    
    config_test = test_config()
    
    print("\n" + "=" * 60)
    if config_test:
        print("✓ CONFIGURATION TEST PASSED - Config class is working!")
        print("\nNote: To test full service integration, run this in the Docker environment")
        print("where all dependencies are available.")
        sys.exit(0)
    else:
        print("✗ CONFIGURATION TEST FAILED - Check errors above")
        sys.exit(1)
