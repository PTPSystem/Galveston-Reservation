#!/usr/bin/env python3
"""
Test Calendar Change Detection
Simple test to verify the change detection system works
"""
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.calendar_change_detection import CalendarChangeDetectionService
from app import create_app

def test_change_detection():
    """Test the calendar change detection functionality"""
    print("Testing Calendar Change Detection...")
    print("=" * 50)
    
    # Create Flask application context
    app = create_app()
    
    with app.app_context():
        try:
            # Initialize the service
            change_service = CalendarChangeDetectionService()
            
            # Test change detection
            print("1. Detecting changes in calendar...")
            changes = change_service.detect_booking_changes(days_back=30)
            
            print(f"   Found {len(changes)} changes")
            
            if changes:
                print("\n2. Change details:")
                for i, change in enumerate(changes, 1):
                    print(f"   Change {i}:")
                    print(f"     - Booking ID: {change.booking_id}")
                    print(f"     - Type: {change.change_type}")
                    print(f"     - Guest: {change.guest_email}")
                    
                    if change.change_type == 'deleted':
                        print(f"     - Original dates: {change.old_data['start_date']} to {change.old_data['end_date']}")
                    elif change.change_type == 'modified':
                        print(f"     - Old dates: {change.old_data['start_date']} to {change.old_data['end_date']}")
                        print(f"     - New dates: {change.new_data['start_date']} to {change.new_data['end_date']}")
                
                # Test notification sending (dry run)
                print("\n3. Testing notification sending...")
                print("   (Note: This will send actual emails if configured)")
                
                user_input = input("   Send actual notification emails? (y/N): ").strip().lower()
                
                if user_input == 'y':
                    notification_results = change_service.send_change_notifications(changes)
                    print(f"   Notification results: {notification_results}")
                else:
                    print("   Skipped sending notifications")
            else:
                print("\n2. No changes detected - this is expected if no calendar events were modified")
                
            print("\n" + "=" * 50)
            print("Test completed successfully!")
            
        except Exception as e:
            print(f"Error during test: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_change_detection()
