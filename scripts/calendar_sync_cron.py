#!/usr/bin/env python3
"""
Calendar Sync Cron Job
Synchronizes blocked dates from Galveston Island Resort Rentals to Google Calendar
"""
import sys
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.calendar_sync import CalendarSyncService
from app.services.google_calendar import GoogleCalendarService
from app.services.rental_scraper_v2 import GalvestonRentalScraper

# Set up logging
try:
    log_dir = Path(__file__).parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f'calendar_sync_{datetime.now().strftime("%Y%m%d")}.log'
    
    # Try to write to the logs directory, fall back to stdout only if it fails
    handlers = [logging.StreamHandler(sys.stdout)]
    try:
        handlers.append(logging.FileHandler(log_file))
    except (PermissionError, OSError) as e:
        print(f"Warning: Could not create log file {log_file}: {e}")
        print("Continuing with console output only...")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
except Exception as e:
    # If all else fails, just use console logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    print(f"Warning: Could not set up file logging: {e}")

logger = logging.getLogger(__name__)

def main():
    """Main sync function"""
    try:
        logger.info("=" * 50)
        logger.info("Starting calendar sync job")
        logger.info("=" * 50)
        
        # Initialize services
        scraper = GalvestonRentalScraper()
        google_service = GoogleCalendarService()
        sync_service = CalendarSyncService()
        
        # Test connections first
        logger.info("Testing Google Calendar connection...")
        try:
            # Test with a small date range
            test_start = datetime.now()
            test_end = test_start + timedelta(days=1)
            events = google_service.get_events(test_start, test_end)
            logger.info(f"Google Calendar connection successful. Found {len(events)} events in test range.")
        except Exception as e:
            logger.error(f"Google Calendar connection failed: {e}")
            return 1
        
        # Scrape rental website
        logger.info("Scraping rental website for availability...")
        availability_data = scraper.scrape_availability(months_ahead=6)
        
        if 'error' in availability_data:
            logger.error(f"Failed to scrape rental website: {availability_data['error']}")
            return 1
        
        blocked_dates = availability_data.get('blocked_dates', [])
        logger.info(f"Found {len(blocked_dates)} blocked dates on rental website")
        
        # Sync to Google Calendar
        if blocked_dates:
            logger.info("Syncing blocked dates to Google Calendar...")
            
            # First run as dry-run to see what would be created
            sync_result = sync_service.sync_blocked_dates_to_google(dry_run=True)
            logger.info(f"Dry run result: {sync_result}")
            
            # Now perform the actual sync
            sync_result = sync_service.sync_blocked_dates_to_google(dry_run=False)
            
            if sync_result.get('success'):
                logger.info(f"Sync completed successfully. Events created: {sync_result.get('events_created', 0)}")
            else:
                logger.error(f"Sync failed: {sync_result.get('message', 'Unknown error')}")
                return 1
        else:
            logger.info("No blocked dates to sync")
        
        logger.info("=" * 50)
        logger.info("Calendar sync job completed successfully")
        logger.info("=" * 50)
        return 0
        
    except Exception as e:
        logger.error(f"Unexpected error in sync job: {e}")
        logger.exception("Full traceback:")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
