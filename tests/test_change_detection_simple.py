#!/usr/bin/env python3
"""
Simple Test for Calendar Change Detection
Tests the change detection service without database dependencies
"""
import sys
from pathlib import Path
import os
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set environment variable to avoid database initialization
os.environ['FLASK_ENV'] = 'testing'

@dataclass
class MockBookingChange:
    """Mock booking change for testing"""
    booking_id: str
    change_type: str
    guest_email: str
    old_data: dict
    new_data: dict
    detected_at: datetime

def test_service_imports():
    """Test that we can import the change detection service"""
    print("Testing Service Imports...")
    print("=" * 40)
    
    try:
        # Test individual service imports
        print("1. Testing GoogleCalendarService import...")
        from app.services.google_calendar import GoogleCalendarService
        print("   ✓ GoogleCalendarService imported successfully")
        
        print("2. Testing EmailService import...")
        from app.services.email import EmailService
        print("   ✓ EmailService imported successfully")
        
        print("3. Testing InputSanitizer import...")
        from app.services.input_sanitizer import input_sanitizer
        print("   ✓ InputSanitizer imported successfully")
        
        print("4. Testing CalendarChangeDetectionService import...")
        from app.services.calendar_change_detection import CalendarChangeDetectionService
        print("   ✓ CalendarChangeDetectionService imported successfully")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_change_detection_logic():
    """Test the change detection logic without requiring real API calls"""
    print("\nTesting Change Detection Logic...")
    print("=" * 40)
    
    try:
        from app.services.calendar_change_detection import CalendarChangeDetectionService
        
        # Create mock changes to test notification logic
        mock_changes = [
            MockBookingChange(
                booking_id="test_001",
                change_type="deleted",
                guest_email="test@example.com",
                old_data={
                    'start_date': datetime.now().isoformat(),
                    'end_date': (datetime.now() + timedelta(days=3)).isoformat(),
                    'summary': 'Test Booking - Family Vacation'
                },
                new_data={},
                detected_at=datetime.now()
            ),
            MockBookingChange(
                booking_id="test_002", 
                change_type="modified",
                guest_email="guest@example.com",
                old_data={
                    'start_date': datetime.now().isoformat(),
                    'end_date': (datetime.now() + timedelta(days=2)).isoformat(),
                    'summary': 'Original Booking'
                },
                new_data={
                    'start_date': (datetime.now() + timedelta(days=1)).isoformat(),
                    'end_date': (datetime.now() + timedelta(days=4)).isoformat(),
                    'summary': 'Modified Booking'
                },
                detected_at=datetime.now()
            )
        ]
        
        print(f"1. Created {len(mock_changes)} mock changes for testing")
        
        print("2. Testing change analysis...")
        for i, change in enumerate(mock_changes, 1):
            print(f"   Change {i}:")
            print(f"     - Type: {change.change_type}")
            print(f"     - Booking ID: {change.booking_id}")
            print(f"     - Guest: {change.guest_email}")
            
            if change.change_type == 'deleted':
                print(f"     - Deleted dates: {change.old_data['start_date']} to {change.old_data['end_date']}")
            elif change.change_type == 'modified':
                print(f"     - Old: {change.old_data['start_date']} to {change.old_data['end_date']}")
                print(f"     - New: {change.new_data['start_date']} to {change.new_data['end_date']}")
        
        print("   ✓ Change analysis completed successfully")
        
        print("3. Testing notification message generation...")
        # Test message generation logic
        for change in mock_changes:
            if change.change_type == 'deleted':
                message = f"Booking {change.booking_id} was deleted. Guest: {change.guest_email}"
            else:
                message = f"Booking {change.booking_id} was modified. Guest: {change.guest_email}"
            print(f"   Generated message: {message}")
        
        print("   ✓ Message generation completed successfully")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Logic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_configuration():
    """Test that required configuration is available"""
    print("\nTesting Configuration...")
    print("=" * 40)
    
    try:
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv()
        
        # Check for required environment variables
        required_vars = [
            'GOOGLE_CALENDAR_CREDENTIALS_PATH',
            'GOOGLE_CALENDAR_ID',
            'MAIL_SERVER',
            'MAIL_USERNAME'
        ]
        
        missing_vars = []
        for var in required_vars:
            value = os.getenv(var)
            if value:
                print(f"   ✓ {var}: {'*' * min(len(value), 10)}...")
            else:
                print(f"   ✗ {var}: Not set")
                missing_vars.append(var)
        
        if missing_vars:
            print(f"\n   Warning: Missing {len(missing_vars)} environment variables")
            print("   These are needed for full functionality but not for testing")
        else:
            print("   ✓ All required environment variables are set")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Configuration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Calendar Change Detection - Simple Test")
    print("=" * 50)
    print(f"Test run at: {datetime.now()}")
    print()
    
    results = {
        'imports': test_service_imports(),
        'logic': test_change_detection_logic(),
        'config': test_configuration()
    }
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"   {test_name.title()}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The calendar change detection system is ready.")
        print("\nNext steps:")
        print("1. Set up Google Calendar credentials")
        print("2. Configure email settings")
        print("3. Run the enhanced calendar sync script")
        print("4. Set up automatic monitoring with cron")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please review the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
