"""
Test the improved rental scraper
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.rental_scraper_v2 import GalvestonRentalScraper
from app.services.google_calendar import GoogleCalendarService
import logging
import json

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_rental_scraper():
    """Test the improved rental website scraper"""
    logger.info("Testing improved rental scraper...")
    
    scraper = GalvestonRentalScraper()
    
    try:
        # Test basic availability scraping
        availability_data = scraper.scrape_availability()
        
        logger.info("=== RENTAL SCRAPER RESULTS ===")
        logger.info(f"Total available dates: {availability_data.get('total_available', 0)}")
        logger.info(f"Total blocked dates: {availability_data.get('total_blocked', 0)}")
        
        if 'error' in availability_data:
            logger.error(f"Scraper error: {availability_data['error']}")
            return False
        
        # Show sample data
        available_dates = availability_data.get('available_dates', [])
        blocked_dates = availability_data.get('blocked_dates', [])
        
        if available_dates:
            logger.info("Sample available dates:")
            for date_info in available_dates[:5]:
                logger.info(f"  {date_info['date']} - Check-in: {date_info.get('check_in_allowed', False)}, Check-out: {date_info.get('check_out_allowed', False)}")
        
        if blocked_dates:
            logger.info("Sample blocked dates:")
            for date_info in blocked_dates[:5]:
                logger.info(f"  {date_info['date']} - Status: {date_info['status']}")
        
        # Test blocked date ranges
        logger.info("\n=== BLOCKED DATE RANGES ===")
        date_ranges = scraper.get_blocked_date_ranges()
        logger.info(f"Found {len(date_ranges)} blocked date ranges:")
        
        for i, range_info in enumerate(date_ranges[:10]):  # Show first 10 ranges
            logger.info(f"  Range {i+1}: {range_info['start']} to {range_info['end']}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing rental scraper: {e}")
        return False

def test_google_calendar():
    """Test Google Calendar integration"""
    logger.info("\nTesting Google Calendar integration...")
    
    try:
        calendar_service = GoogleCalendarService()
        
        # Test getting events
        events = calendar_service.get_events(max_results=10)
        logger.info(f"Found {len(events)} events in Google Calendar")
        
        if events:
            logger.info("Sample events:")
            for event in events[:3]:
                summary = event.get('summary', 'No summary')
                start = event.get('start', {}).get('date') or event.get('start', {}).get('dateTime', 'No date')
                logger.info(f"  {summary} - {start}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing Google Calendar: {e}")
        return False

def test_calendar_comparison():
    """Test comparing rental website data with Google Calendar"""
    logger.info("\n=== CALENDAR COMPARISON ===")
    
    try:
        # Get rental data
        scraper = GalvestonRentalScraper()
        rental_data = scraper.scrape_availability()
        
        # Get Google Calendar data
        calendar_service = GoogleCalendarService()
        google_events = calendar_service.get_events(max_results=100)
        
        # Get blocked dates from rental site
        rental_blocked = set()
        for blocked_date in rental_data.get('blocked_dates', []):
            rental_blocked.add(blocked_date['date'])
        
        # Get blocked dates from Google Calendar (events = blocked)
        google_blocked = set()
        for event in google_events:
            if 'start' in event:
                if 'date' in event['start']:
                    google_blocked.add(event['start']['date'])
                elif 'dateTime' in event['start']:
                    # Convert datetime to date
                    from datetime import datetime
                    dt = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
                    google_blocked.add(dt.strftime('%Y-%m-%d'))
        
        # Compare
        logger.info(f"Rental site blocked dates: {len(rental_blocked)}")
        logger.info(f"Google Calendar blocked dates: {len(google_blocked)}")
        
        # Find discrepancies
        only_in_rental = rental_blocked - google_blocked
        only_in_google = google_blocked - rental_blocked
        
        logger.info(f"Dates blocked only on rental site: {len(only_in_rental)}")
        logger.info(f"Dates blocked only in Google Calendar: {len(only_in_google)}")
        
        if only_in_rental:
            logger.info("Sample dates blocked only on rental site:")
            for date in sorted(list(only_in_rental))[:5]:
                logger.info(f"  {date}")
        
        if only_in_google:
            logger.info("Sample dates blocked only in Google Calendar:")
            for date in sorted(list(only_in_google))[:5]:
                logger.info(f"  {date}")
        
        # Suggest sync actions
        if only_in_rental:
            logger.info(f"\nSUGGESTION: Add {len(only_in_rental)} rental site blocked dates to Google Calendar")
        
        if only_in_google:
            logger.info(f"SUGGESTION: Review {len(only_in_google)} Google Calendar events that aren't blocked on rental site")
        
        return {
            'rental_blocked_count': len(rental_blocked),
            'google_blocked_count': len(google_blocked),
            'sync_needed': len(only_in_rental) > 0,
            'discrepancies': {
                'rental_only': list(only_in_rental),
                'google_only': list(only_in_google)
            }
        }
        
    except Exception as e:
        logger.error(f"Error in calendar comparison: {e}")
        return None

if __name__ == "__main__":
    logger.info("Starting comprehensive calendar sync test...")
    
    # Test rental scraper
    rental_success = test_rental_scraper()
    
    # Test Google Calendar
    google_success = test_google_calendar()
    
    # If both work, test comparison
    if rental_success and google_success:
        comparison_result = test_calendar_comparison()
        
        if comparison_result:
            # Save comparison results
            with open('calendar_comparison_results.json', 'w') as f:
                json.dump(comparison_result, f, indent=2)
            logger.info("Saved comparison results to calendar_comparison_results.json")
    
    logger.info("Test completed!")
