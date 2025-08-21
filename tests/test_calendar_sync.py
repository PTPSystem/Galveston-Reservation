"""
Test Calendar Synchronization
Compare rental website calendar with Google Calendar
"""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from app.services.calendar_sync import CalendarSyncService
from app.services.rental_scraper import GalvestonRentalScraper
import json

def test_rental_scraper():
    """Test the rental website scraper"""
    print("🏖️  Testing Galveston Rental Website Scraper")
    print("=" * 60)
    
    scraper = GalvestonRentalScraper()
    
    print("📊 Fetching calendar data from rental website...")
    calendar_data = scraper.get_calendar_data()
    
    if 'error' in calendar_data:
        print(f"❌ Error: {calendar_data['error']}")
        return False
    
    available_dates = calendar_data.get('available_dates', [])
    blocked_dates = calendar_data.get('blocked_dates', [])
    
    print(f"✅ Successfully scraped calendar data!")
    print(f"📅 Available dates: {len(available_dates)}")
    print(f"🚫 Blocked dates: {len(blocked_dates)}")
    
    # Show first few available dates
    if available_dates:
        print(f"\n📋 First 5 available dates:")
        for date_info in available_dates[:5]:
            check_in = "✓" if date_info.get('check_in_allowed') else "✗"
            check_out = "✓" if date_info.get('check_out_allowed') else "✗"
            print(f"  • {date_info['date']} (Check-in: {check_in}, Check-out: {check_out})")
    
    # Show first few blocked dates
    if blocked_dates:
        print(f"\n🚫 First 5 blocked dates:")
        for date_info in blocked_dates[:5]:
            print(f"  • {date_info['date']} ({date_info.get('reason', 'blocked')})")
    
    # Test blocked date ranges
    print(f"\n📊 Getting blocked date ranges...")
    blocked_ranges = scraper.get_blocked_date_ranges()
    print(f"✅ Found {len(blocked_ranges)} blocked periods:")
    
    for range_info in blocked_ranges[:3]:  # Show first 3 ranges
        print(f"  • {range_info['start']} to {range_info['end']}: {range_info['title']}")
    
    return True

def test_calendar_comparison():
    """Test calendar comparison between sources"""
    print("\n🔄 Testing Calendar Comparison")
    print("=" * 60)
    
    sync_service = CalendarSyncService()
    
    print("📊 Comparing Google Calendar with rental website...")
    comparison = sync_service.get_availability_comparison()
    
    if not comparison.get('success'):
        print(f"❌ Comparison failed: {comparison.get('error')}")
        return False
    
    print("✅ Comparison completed!")
    print(f"\n📈 Results:")
    
    rental_data = comparison.get('rental_website', {})
    google_data = comparison.get('google_calendar', {})
    comp_data = comparison.get('comparison', {})
    
    print(f"🏖️  Rental Website:")
    print(f"   • Available dates: {rental_data.get('available_dates', 0)}")
    print(f"   • Blocked dates: {rental_data.get('blocked_dates', 0)}")
    
    print(f"📅 Google Calendar:")
    print(f"   • Total events: {google_data.get('total_events', 0)}")
    print(f"   • Calendar ID: {google_data.get('calendar_id')}")
    
    print(f"🔍 Comparison:")
    print(f"   • Sync needed: {comp_data.get('sync_needed', False)}")
    
    discrepancies = comp_data.get('discrepancies', {})
    rental_only = discrepancies.get('rental_site_only', [])
    google_only = discrepancies.get('google_calendar_only', [])
    
    if rental_only:
        print(f"   • Dates blocked on rental site only: {len(rental_only)}")
        print(f"     Examples: {rental_only[:3]}")
    
    if google_only:
        print(f"   • Dates blocked in Google only: {len(google_only)}")
        print(f"     Examples: {google_only[:3]}")
    
    recommendations = comparison.get('recommendations', [])
    if recommendations:
        print(f"\n💡 Recommendations:")
        for rec in recommendations:
            print(f"   • {rec}")
    
    return True

def test_sync_preview():
    """Test sync preview (dry run)"""
    print("\n🧪 Testing Sync Preview (Dry Run)")
    print("=" * 60)
    
    sync_service = CalendarSyncService()
    
    print("🔄 Running sync preview...")
    sync_result = sync_service.sync_blocked_dates_to_google(dry_run=True)
    
    if not sync_result.get('success'):
        print(f"❌ Sync preview failed: {sync_result.get('error')}")
        return False
    
    print("✅ Sync preview completed!")
    print(f"📊 Results:")
    print(f"   • Events to create: {len(sync_result.get('events_to_create', []))}")
    print(f"   • Blocked ranges found: {sync_result.get('blocked_ranges_found', 0)}")
    print(f"   • Message: {sync_result.get('message')}")
    
    events_to_create = sync_result.get('events_to_create', [])
    if events_to_create:
        print(f"\n📅 Events that would be created:")
        for event in events_to_create[:3]:  # Show first 3
            print(f"   • {event['summary']}")
            print(f"     From: {event['start_date'].strftime('%Y-%m-%d')}")
            print(f"     To: {event['end_date'].strftime('%Y-%m-%d')}")
    
    return True

def test_next_available_dates():
    """Test getting next available dates"""
    print("\n📅 Testing Next Available Dates")
    print("=" * 60)
    
    sync_service = CalendarSyncService()
    
    print("📊 Getting next 10 available dates...")
    available_dates = sync_service.get_next_available_dates(10)
    
    if not available_dates:
        print("⚠️  No available dates found")
        return False
    
    print(f"✅ Found {len(available_dates)} available dates:")
    
    for date_info in available_dates:
        check_in = "✓" if date_info.get('check_in_allowed') else "✗"
        check_out = "✓" if date_info.get('check_out_allowed') else "✗"
        print(f"   • {date_info['date']} (Check-in: {check_in}, Check-out: {check_out})")
    
    return True

def main():
    """Run all tests"""
    print("🧪 Galveston Reservation Calendar Sync Tests")
    print("=" * 80)
    
    tests = [
        ("Rental Scraper", test_rental_scraper),
        ("Calendar Comparison", test_calendar_comparison),
        ("Sync Preview", test_sync_preview),
        ("Next Available Dates", test_next_available_dates)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 80)
    print("📊 Test Results Summary:")
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   • {test_name}: {status}")
    
    all_passed = all(success for _, success in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Calendar sync system is ready.")
        print("\n📋 Next steps:")
        print("   1. Review the sync preview results")
        print("   2. Run actual sync if needed: sync_service.sync_blocked_dates_to_google(dry_run=False)")
        print("   3. Set up automated sync schedule")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
