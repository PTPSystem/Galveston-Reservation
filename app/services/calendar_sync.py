"""
Calendar Synchronization Service
Synchronizes availability between Google Calendar and rental booking website
"""
from app.services.google_calendar import GoogleCalendarService
from app.services.rental_scraper import GalvestonRentalScraper
from datetime import datetime, timedelta
import logging
from typing import Dict, List

class CalendarSyncService:
    """Service to synchronize calendar data between sources"""
    
    def __init__(self):
        self.google_service = GoogleCalendarService()
        self.rental_scraper = GalvestonRentalScraper()
        
    def sync_blocked_dates_to_google(self, dry_run: bool = True) -> Dict[str, any]:
        """
        Sync blocked dates from rental website to Google Calendar
        
        Args:
            dry_run: If True, only report what would be synced without making changes
            
        Returns:
            Sync results
        """
        try:
            logging.info("Starting calendar sync process...")
            
            # Get blocked date ranges from rental website
            blocked_ranges = self.rental_scraper.get_blocked_date_ranges()
            
            if not blocked_ranges:
                return {
                    'success': True,
                    'message': 'No blocked dates found on rental website',
                    'events_created': 0,
                    'dry_run': dry_run
                }
            
            events_created = 0
            events_to_create = []
            
            for range_data in blocked_ranges:
                start_date = datetime.strptime(range_data['start'], '%Y-%m-%d')
                end_date = datetime.strptime(range_data['end'], '%Y-%m-%d')
                
                # Check if this period is already blocked in Google Calendar
                existing_events = self.google_service.get_events(start_date, end_date + timedelta(days=1))
                
                # Simple check - if there are any events in this period, consider it already blocked
                if not existing_events:
                    event_data = {
                        'summary': range_data['title'],
                        'start_date': start_date,
                        'end_date': end_date + timedelta(days=1),  # End date is exclusive
                        'description': f'Automatically synced from rental booking website\nBlocked period: {range_data["start"]} to {range_data["end"]}',
                        'all_day': True
                    }
                    
                    events_to_create.append(event_data)
                    
                    if not dry_run:
                        # Create the blocking event
                        created_event = self.google_service.create_event(
                            summary=event_data['summary'],
                            start_datetime=event_data['start_date'],
                            end_datetime=event_data['end_date'],
                            description=event_data['description']
                        )
                        
                        if created_event:
                            events_created += 1
                            logging.info(f"Created blocking event for {range_data['start']} to {range_data['end']}")
                        else:
                            logging.error(f"Failed to create event for {range_data['start']} to {range_data['end']}")
            
            return {
                'success': True,
                'message': f'Sync completed. {"Would create" if dry_run else "Created"} {len(events_to_create)} blocking events',
                'events_created': events_created,
                'events_to_create': events_to_create if dry_run else [],
                'blocked_ranges_found': len(blocked_ranges),
                'dry_run': dry_run
            }
            
        except Exception as e:
            logging.error(f"Calendar sync failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'events_created': 0,
                'dry_run': dry_run
            }
    
    def get_availability_comparison(self) -> Dict[str, any]:
        """
        Compare availability between Google Calendar and rental website
        
        Returns:
            Detailed comparison of both sources
        """
        try:
            # Get data from both sources
            rental_data = self.rental_scraper.get_calendar_data()
            
            # Get Google Calendar events for the next 6 months
            start_date = datetime.now()
            end_date = start_date + timedelta(days=180)
            google_events = self.google_service.get_events(start_date, end_date)
            
            # Compare the data
            comparison = self.rental_scraper.compare_with_google_calendar(google_events)
            
            return {
                'success': True,
                'rental_website': {
                    'available_dates': len(rental_data.get('available_dates', [])),
                    'blocked_dates': len(rental_data.get('blocked_dates', [])),
                    'last_updated': rental_data.get('last_updated')
                },
                'google_calendar': {
                    'total_events': len(google_events),
                    'calendar_id': self.google_service.calendar_id
                },
                'comparison': comparison,
                'recommendations': self._generate_sync_recommendations(comparison)
            }
            
        except Exception as e:
            logging.error(f"Availability comparison failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_sync_recommendations(self, comparison: Dict) -> List[str]:
        """Generate recommendations based on comparison results"""
        recommendations = []
        
        if comparison.get('sync_needed', False):
            discrepancies = comparison.get('discrepancies', {})
            
            rental_only = discrepancies.get('rental_site_only', [])
            google_only = discrepancies.get('google_calendar_only', [])
            
            if rental_only:
                recommendations.append(
                    f"Add {len(rental_only)} blocked dates from rental website to Google Calendar"
                )
            
            if google_only:
                recommendations.append(
                    f"Review {len(google_only)} dates that are blocked in Google but available on rental website"
                )
        else:
            recommendations.append("Both calendars are in sync - no action needed")
        
        return recommendations
    
    def get_next_available_dates(self, num_dates: int = 10) -> List[Dict[str, str]]:
        """
        Get the next available dates from rental website
        
        Args:
            num_dates: Number of available dates to return
            
        Returns:
            List of next available dates with check-in/out info
        """
        try:
            rental_data = self.rental_scraper.get_calendar_data()
            available_dates = rental_data.get('available_dates', [])
            
            # Filter to future dates and sort
            today = datetime.now().date()
            future_dates = [
                date_info for date_info in available_dates 
                if datetime.strptime(date_info['date'], '%Y-%m-%d').date() >= today
            ]
            
            # Sort by date
            future_dates.sort(key=lambda x: x['date'])
            
            return future_dates[:num_dates]
            
        except Exception as e:
            logging.error(f"Failed to get available dates: {e}")
            return []
