"""
Simple Google Calendar Access Test
"""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from google.oauth2 import service_account
from googleapiclient.discovery import build

def test_calendar_access():
    print("🔧 Testing Google Calendar Access")
    print("=" * 50)
    
    # Configuration
    credentials_path = "./secrets/service-account.json"
    calendar_id = os.getenv('GOOGLE_CALENDAR_ID', 'livingbayfront@gmail.com')
    scopes = ['https://www.googleapis.com/auth/calendar.readonly']
    
    print(f"📧 Calendar ID: {calendar_id}")
    print(f"🔑 Service Account: galveston-calendar-service@galveston-booking-468515.iam.gserviceaccount.com")
    print(f"📁 Credentials: {credentials_path}")
    
    try:
        # Load credentials
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=scopes)
        
        # Build service
        service = build('calendar', 'v3', credentials=credentials)
        
        # Test 1: List calendars the service account has access to
        print("\n📋 Testing calendar list access...")
        calendar_list = service.calendarList().list().execute()
        
        print(f"✅ Found {len(calendar_list.get('items', []))} accessible calendars:")
        for cal in calendar_list.get('items', []):
            print(f"  • {cal.get('summary', 'Unknown')} ({cal.get('id')})")
        
        # Test 2: Try to access the specific calendar
        print(f"\n📅 Testing access to {calendar_id}...")
        try:
            calendar_info = service.calendars().get(calendarId=calendar_id).execute()
            print(f"✅ Successfully accessed calendar: {calendar_info.get('summary')}")
            
            # Test 3: Get recent events
            print("\n📊 Testing event access...")
            events_result = service.events().list(
                calendarId=calendar_id,
                maxResults=5,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            print(f"✅ Found {len(events)} events")
            
            return True
            
        except Exception as e:
            print(f"❌ Cannot access calendar {calendar_id}")
            print(f"Error: {e}")
            print("\n🔍 This usually means:")
            print(f"  1. Calendar '{calendar_id}' doesn't exist")
            print(f"  2. Service account email not shared with this calendar")
            print(f"  3. Calendar ID is wrong")
            
            return False
            
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

if __name__ == "__main__":
    test_calendar_access()
