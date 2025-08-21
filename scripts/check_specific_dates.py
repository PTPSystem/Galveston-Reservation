"""
Check specific dates around the August 29 - September 2 booking
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.rental_scraper_v2 import GalvestonRentalScraper
import logging
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_specific_dates():
    """Check the specific dates around the August 29 - September 2 booking"""
    logger.info("Checking specific dates for August 29 - September 2 booking...")
    
    scraper = GalvestonRentalScraper()
    
    try:
        # Get all availability data
        availability_data = scraper.scrape_availability()
        
        if 'error' in availability_data:
            logger.error(f"Scraper error: {availability_data['error']}")
            return
        
        # Combine all dates for easy lookup
        all_dates = {}
        
        # Add available dates
        for date_info in availability_data.get('available_dates', []):
            all_dates[date_info['date']] = {
                'status': 'available',
                'check_in_allowed': date_info.get('check_in_allowed', False),
                'check_out_allowed': date_info.get('check_out_allowed', False)
            }
        
        # Add blocked dates
        for date_info in availability_data.get('blocked_dates', []):
            all_dates[date_info['date']] = {
                'status': 'blocked'
            }
        
        # Check dates from August 27 to September 5 (wider range)
        logger.info("=== DATE STATUS AROUND BOOKING ===")
        start_date = datetime(2025, 8, 27)
        
        for i in range(10):  # Check 10 days
            check_date = start_date + timedelta(days=i)
            date_str = check_date.strftime('%Y-%m-%d')
            date_display = check_date.strftime('%A, %B %d, %Y')
            
            if date_str in all_dates:
                date_info = all_dates[date_str]
                status = date_info['status']
                
                if status == 'available':
                    check_in = "✓" if date_info.get('check_in_allowed') else "✗"
                    check_out = "✓" if date_info.get('check_out_allowed') else "✗"
                    logger.info(f"{date_display}: 🟢 AVAILABLE (Check-in: {check_in}, Check-out: {check_out})")
                else:
                    logger.info(f"{date_display}: 🔴 BLOCKED")
            else:
                logger.info(f"{date_display}: ❓ NOT FOUND")
        
        logger.info("\n=== EXPECTED vs ACTUAL ===")
        logger.info("Expected blocked dates: Aug 29, Aug 30, Aug 31, Sep 1, Sep 2")
        
        expected_blocked = [
            '2025-08-29',
            '2025-08-30', 
            '2025-08-31',
            '2025-09-01',
            '2025-09-02'
        ]
        
        logger.info("Actual status from scraper:")
        for date_str in expected_blocked:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            date_display = date_obj.strftime('%b %d')
            
            if date_str in all_dates:
                status = all_dates[date_str]['status']
                if status == 'blocked':
                    logger.info(f"  {date_display}: ✅ Correctly BLOCKED")
                else:
                    logger.info(f"  {date_display}: ❌ Shows as AVAILABLE (should be blocked)")
            else:
                logger.info(f"  {date_display}: ❌ NOT FOUND in scraper data")
        
        # Show what we found around this period
        actual_blocked_in_range = []
        for date_str in all_dates:
            if all_dates[date_str]['status'] == 'blocked':
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                if datetime(2025, 8, 27) <= date_obj <= datetime(2025, 9, 5):
                    actual_blocked_in_range.append(date_str)
        
        logger.info(f"\nActual blocked dates found in Aug 27 - Sep 5 range:")
        for date_str in sorted(actual_blocked_in_range):
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            logger.info(f"  {date_obj.strftime('%b %d')}: BLOCKED")
            
    except Exception as e:
        logger.error(f"Error checking specific dates: {e}")

if __name__ == "__main__":
    check_specific_dates()
