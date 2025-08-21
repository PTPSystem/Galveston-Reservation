"""
Test Google Calendar API Connection
Run this script to verify your calendar integration is working
"""
import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.google_calendar import GoogleCalendarService
from datetime import datetime, timedelta
import json

def test_calendar_connection():
    """Test the Google Calendar API connection"""
    print("🧪 Testing Google Calendar API Connection")
    print("=" * 50)
    
    try:
        # Initialize the calendar service
        print("🔧 Initializing Google Calendar service...")
        calendar_service = GoogleCalendarService()
        
        # Test basic connection
        print("📅 Testing calendar access...")
        
        # Try to get events for the next 7 days
        start_date = datetime.now()
        end_date = start_date + timedelta(days=7)
        
        print(f"📊 Checking events from {start_date.date()} to {end_date.date()}")
        
        # Check availability (this will test the connection)
        availability = calendar_service.check_availability(start_date, end_date)
        
        print("✅ Calendar connection successful!")
        print("\n📋 Availability Results:")
        print(json.dumps(availability, indent=2, default=str))
        
        # Try to sync events
        print("\n🔄 Testing event sync...")
        events = calendar_service.sync_events()
        print(f"✅ Synced {len(events)} events from calendar")
        
        return True
        
    except Exception as e:
        print(f"❌ Calendar connection failed:")
        print(f"Error: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Check common issues
        print("\n🔍 Troubleshooting:")
        
        # Check if service account file exists
        secrets_path = Path("secrets/service-account.json")
        if secrets_path.exists():
            print("✅ Service account file found")
        else:
            print("❌ Service account file missing at secrets/service-account.json")
            
        # Check environment variables
        project_id = os.getenv('GOOGLE_PROJECT_ID')
        calendar_id = os.getenv('GOOGLE_CALENDAR_ID')
        
        print(f"📝 Project ID: {project_id}")
        print(f"📧 Calendar ID: {calendar_id}")
        
        if not project_id:
            print("❌ GOOGLE_PROJECT_ID not set in environment")
        if not calendar_id:
            print("❌ GOOGLE_CALENDAR_ID not set in environment")
            
        return False

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    success = test_calendar_connection()
    
    if success:
        print("\n🎉 Google Calendar integration is ready!")
        print("Your reservation system can now:")
        print("  • Check availability in real-time")
        print("  • Create booking events")
        print("  • Sync with Google Calendar")
    else:
        print("\n⚠️  Calendar integration needs attention")
        print("Please check the troubleshooting information above")
