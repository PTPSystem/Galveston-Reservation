"""
Smart Calendar Sync - Sync rental bookings to Google Calendar with proper check-in/check-out times
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.rental_scraper_v2 import GalvestonRentalScraper
from app.services.google_calendar import GoogleCalendarService
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SmartCalendarSync:
    def __init__(self):
        self.scraper = GalvestonRentalScraper()
        self.calendar_service = GoogleCalendarService()
        self.checkin_time = "15:00:00"  # 3:00 PM
        self.checkout_time = "11:00:00"  # 11:00 AM
        
    def analyze_booking_patterns(self) -> List[Dict]:
        """
        Analyze rental website data to identify actual booking periods
        """
        logger.info("Analyzing booking patterns from rental website...")
        
        # Get availability data
        availability_data = self.scraper.scrape_availability()
        
        if 'error' in availability_data:
            logger.error(f"Scraper error: {availability_data['error']}")
            return []
        
        # Create lookup for all dates
        date_status = {}
        
        # Add available dates
        for date_info in availability_data.get('available_dates', []):
            date_status[date_info['date']] = {
                'status': 'available',
                'check_in_allowed': date_info.get('check_in_allowed', False),
                'check_out_allowed': date_info.get('check_out_allowed', False),
                'classes': date_info.get('classes', [])
            }
        
        # Add blocked dates
        for date_info in availability_data.get('blocked_dates', []):
            date_status[date_info['date']] = {
                'status': 'blocked',
                'check_in_allowed': False,
                'check_out_allowed': False,
                'classes': date_info.get('classes', [])
            }
        
        # Identify booking periods
        bookings = self._identify_booking_periods(date_status)
        
        logger.info(f"Identified {len(bookings)} booking periods")
        
        return bookings
    
    def _identify_booking_periods(self, date_status: Dict) -> List[Dict]:
        """
        Identify continuous booking periods from the date status data
        """
        bookings = []
        
        # Get all dates and sort them
        all_dates = sorted(date_status.keys())
        
        i = 0
        while i < len(all_dates):
            current_date = all_dates[i]
            current_info = date_status[current_date]
            
            # Look for start of a booking period
            # This could be:
            # 1. A blocked date
            # 2. An available date with check-out only (indicating current booking)
            
            if (current_info['status'] == 'blocked' or 
                (current_info['status'] == 'available' and 
                 current_info['check_out_allowed'] and not current_info['check_in_allowed'])):
                
                # Found potential booking start
                booking_start = current_date
                booking_end = current_date
                
                # Look ahead to find the end of this booking
                j = i + 1
                while j < len(all_dates):
                    next_date = all_dates[j]
                    next_info = date_status[next_date]
                    
                    # Check if this is part of the same booking
                    if (next_info['status'] == 'blocked' or
                        (next_info['status'] == 'available' and 
                         next_info['check_out_allowed'] and not next_info['check_in_allowed'])):
                        
                        # Still part of the booking
                        booking_end = next_date
                        j += 1
                    else:
                        # End of booking found
                        break
                
                # If we found a booking period, determine the actual check-in and check-out dates
                checkin_date, checkout_date = self._determine_booking_times(
                    booking_start, booking_end, date_status)
                
                if checkin_date and checkout_date:
                    bookings.append({
                        'checkin_date': checkin_date,
                        'checkout_date': checkout_date,
                        'start_date_detected': booking_start,
                        'end_date_detected': booking_end
                    })
                
                # Move to the next unprocessed date
                i = j
            else:
                i += 1
        
        return bookings
    
    def _determine_booking_times(self, start_date: str, end_date: str, date_status: Dict) -> Tuple[str, str]:
        """
        Determine actual check-in and check-out times for a booking period
        """
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Check the day before start_date to see if it's available with check-out
            day_before = (start_dt - timedelta(days=1)).strftime('%Y-%m-%d')
            
            if (day_before in date_status and 
                date_status[day_before]['status'] == 'available' and
                date_status[day_before]['check_out_allowed']):
                # Previous guest checks out, new guest checks in same day
                checkin_datetime = f"{start_date}T{self.checkin_time}"
            else:
                # Regular check-in
                checkin_datetime = f"{start_date}T{self.checkin_time}"
            
            # Check the day after end_date to see if it's available with check-in
            day_after = (end_dt + timedelta(days=1)).strftime('%Y-%m-%d')
            
            if (day_after in date_status and 
                date_status[day_after]['status'] == 'available' and
                date_status[day_after]['check_in_allowed']):
                # Guest checks out, new guest can check in same day
                checkout_datetime = f"{day_after}T{self.checkout_time}"
            else:
                # Regular check-out (day after last occupied night)
                checkout_date = (end_dt + timedelta(days=1)).strftime('%Y-%m-%d')
                checkout_datetime = f"{checkout_date}T{self.checkout_time}"
            
            return checkin_datetime, checkout_datetime
            
        except Exception as e:
            logger.error(f"Error determining booking times: {e}")
            return None, None
    
    def sync_bookings_to_calendar(self, dry_run: bool = True) -> Dict:
        """
        Sync identified bookings to Google Calendar
        """
        logger.info(f"Starting calendar sync (dry_run={dry_run})...")
        
        # Get bookings from rental site
        bookings = self.analyze_booking_patterns()
        
        if not bookings:
            logger.info("No bookings found to sync")
            return {'synced': 0, 'errors': 0}
        
        # Get existing events from Google Calendar
        existing_events = self.calendar_service.get_events(max_results=200)
        
        synced_count = 0
        error_count = 0
        
        for booking in bookings:
            try:
                # Check if this booking already exists in Google Calendar
                if self._booking_exists_in_calendar(booking, existing_events):
                    logger.info(f"Booking {booking['checkin_date']} to {booking['checkout_date']} already exists in calendar")
                    continue
                
                # Parse datetime strings
                from datetime import datetime
                checkin_dt = datetime.fromisoformat(booking['checkin_date'])
                checkout_dt = datetime.fromisoformat(booking['checkout_date'])
                
                # Create event details
                summary = 'Property Booked - Bayfront Retreat'
                description = f"Property occupied from {booking['checkin_date']} to {booking['checkout_date']}\\n\\nCheck-in: 3:00 PM\\nCheck-out: 11:00 AM\\n\\nDetected from rental website calendar"
                location = 'Bayfront Retreat, Jamaica Beach, Galveston, TX'
                
                if dry_run:
                    logger.info(f"DRY RUN: Would create event:")
                    logger.info(f"  Title: {summary}")
                    logger.info(f"  Start: {booking['checkin_date']}")
                    logger.info(f"  End: {booking['checkout_date']}")
                    logger.info(f"  Location: {location}")
                    synced_count += 1
                else:
                    # Actually create the event
                    created_event = self.calendar_service.create_event(
                        summary=summary,
                        start_datetime=checkin_dt,
                        end_datetime=checkout_dt,
                        description=description,
                        location=location
                    )
                    if created_event:
                        logger.info(f"✅ Created booking event: {booking['checkin_date']} to {booking['checkout_date']}")
                        synced_count += 1
                    else:
                        logger.error(f"❌ Failed to create event for booking: {booking['checkin_date']}")
                        error_count += 1
                
            except Exception as e:
                logger.error(f"Error syncing booking {booking}: {e}")
                error_count += 1
        
        logger.info(f"Sync complete. Synced: {synced_count}, Errors: {error_count}")
        
        return {
            'synced': synced_count,
            'errors': error_count,
            'bookings_found': len(bookings),
            'dry_run': dry_run
        }
    
    def _booking_exists_in_calendar(self, booking: Dict, existing_events: List[Dict]) -> bool:
        """
        Check if a booking already exists in the calendar
        """
        booking_start = booking['checkin_date']
        booking_end = booking['checkout_date']
        
        for event in existing_events:
            if 'start' in event and 'end' in event:
                event_start = event['start'].get('dateTime', event['start'].get('date'))
                event_end = event['end'].get('dateTime', event['end'].get('date'))
                
                # Simple overlap check
                if event_start and event_end:
                    if (event_start.startswith(booking_start[:10]) and 
                        event_end.startswith(booking_end[:10])):
                        return True
        
        return False

def main():
    """Main function to run the calendar sync"""
    logger.info("🏠 Smart Calendar Sync for Bayfront Retreat")
    logger.info("=" * 50)
    
    sync_service = SmartCalendarSync()
    
    # First, analyze what bookings we can detect
    logger.info("🔍 Analyzing booking patterns...")
    bookings = sync_service.analyze_booking_patterns()
    
    if bookings:
        logger.info(f"\\n📅 Found {len(bookings)} booking periods:")
        for i, booking in enumerate(bookings, 1):
            logger.info(f"  Booking {i}:")
            logger.info(f"    Check-in:  {booking['checkin_date']} (3:00 PM)")
            logger.info(f"    Check-out: {booking['checkout_date']} (11:00 AM)")
            logger.info(f"    Detected from: {booking['start_date_detected']} to {booking['end_date_detected']}")
            logger.info("")
        
        # Ask user if they want to proceed with sync
        print("\\n🤔 Do you want to sync these bookings to Google Calendar?")
        print("Options:")
        print("  1. Dry run (show what would be created)")
        print("  2. Actually create the events")
        print("  3. Cancel")
        
        choice = input("Enter choice (1/2/3): ").strip()
        
        if choice == "1":
            logger.info("\\n🧪 Running dry run...")
            result = sync_service.sync_bookings_to_calendar(dry_run=True)
        elif choice == "2":
            logger.info("\\n📝 Creating calendar events...")
            result = sync_service.sync_bookings_to_calendar(dry_run=False)
        else:
            logger.info("❌ Cancelled")
            return
        
        logger.info(f"\\n✅ Sync completed: {result}")
    else:
        logger.info("❌ No bookings found to sync")

if __name__ == "__main__":
    main()
