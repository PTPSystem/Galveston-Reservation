"""
Galveston Island Resort Rentals Calendar Scraper
Scrapes availability data from the official booking website
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
from typing import List, Dict, Optional
import logging

class GalvestonRentalScraper:
    """Scraper for Galveston Island Resort Rentals calendar"""
    
    def __init__(self):
        self.base_url = "https://www.galvestonislandresortrentals.com"
        self.property_url = "/galveston-vacation-rentals/bayfront-retreat"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_calendar_data(self, months_ahead: int = 6) -> Dict[str, any]:
        """
        Fetch calendar availability data from the rental website
        
        Args:
            months_ahead: Number of months to fetch data for
            
        Returns:
            Dictionary containing availability data
        """
        try:
            # Build URL with calendar parameters
            today = datetime.now()
            end_date = today + timedelta(days=months_ahead * 30)
            
            # Format dates for the API
            begin_date = today.strftime("%m/%d/%Y")
            end_date_str = end_date.strftime("%m/%d/%Y")
            
            # URL parameters matching the booking system
            params = {
                'rcav': f'{{"rcav":{{"begin":"{begin_date}","end":"{end_date_str}","adult":"10","child":"0","eid":"44"}}}}'
            }
            
            full_url = self.base_url + self.property_url
            
            logging.info(f"Fetching calendar data from: {full_url}")
            response = self.session.get(full_url, params=params, timeout=30)
            response.raise_for_status()
            
            return self._parse_calendar_html(response.text)
            
        except requests.RequestException as e:
            logging.error(f"Failed to fetch calendar data: {e}")
            return {'error': str(e), 'available_dates': [], 'blocked_dates': []}
        except Exception as e:
            logging.error(f"Error parsing calendar data: {e}")
            return {'error': str(e), 'available_dates': [], 'blocked_dates': []}
    
    def _parse_calendar_html(self, html_content: str) -> Dict[str, any]:
        """
        Parse the HTML calendar content to extract availability
        
        Args:
            html_content: Raw HTML from the website
            
        Returns:
            Dictionary with available and blocked dates
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the calendar container
        calendar_div = soup.find('div', class_='rcav-calendar')
        if not calendar_div:
            logging.warning("Calendar container not found in HTML")
            return {'error': 'Calendar not found', 'available_dates': [], 'blocked_dates': []}
        
        available_dates = []
        blocked_dates = []
        current_year = datetime.now().year
        
        # Find all calendar month tables
        month_tables = calendar_div.find_all('table', class_='rc-calendar')
        
        for table in month_tables:
            # Get month and year from caption
            caption = table.find('caption', class_='rc-calendar-month')
            if not caption:
                continue
                
            month_text = caption.get_text().strip()
            month_name, year_str = month_text.split()
            year = int(year_str)
            month_num = self._month_name_to_number(month_name)
            
            if month_num is None:
                continue
            
            # Find all day cells
            day_cells = table.find_all('td', class_='day')
            
            for cell in day_cells:
                day_span = cell.find('span', class_='mday')
                if not day_span:
                    continue
                    
                try:
                    day = int(day_span.get_text().strip())
                    date_obj = datetime(year, month_num, day)
                    date_str = date_obj.strftime('%Y-%m-%d')
                    
                    # Determine availability based on CSS classes
                    classes = cell.get('class', [])
                    
                    if 'av-O' in classes:
                        # Available dates
                        check_in = 'av-IN' in classes
                        check_out = 'av-OUT' in classes
                        available_dates.append({
                            'date': date_str,
                            'check_in_allowed': check_in,
                            'check_out_allowed': check_out
                        })
                    elif 'av-X' in classes:
                        # Blocked/unavailable dates
                        blocked_dates.append({
                            'date': date_str,
                            'reason': 'blocked'
                        })
                        
                except (ValueError, TypeError):
                    continue
        
        logging.info(f"Parsed {len(available_dates)} available dates and {len(blocked_dates)} blocked dates")
        
        return {
            'available_dates': available_dates,
            'blocked_dates': blocked_dates,
            'last_updated': datetime.now().isoformat(),
            'source': 'galvestonislandresortrentals.com'
        }
    
    def _month_name_to_number(self, month_name: str) -> Optional[int]:
        """Convert month name to number"""
        months = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4,
            'May': 5, 'June': 6, 'July': 7, 'August': 8,
            'September': 9, 'October': 10, 'November': 11, 'December': 12
        }
        return months.get(month_name)
    
    def get_blocked_date_ranges(self) -> List[Dict[str, str]]:
        """
        Get blocked date ranges for easy calendar sync
        
        Returns:
            List of date ranges that are blocked
        """
        calendar_data = self.get_calendar_data()
        blocked_dates = calendar_data.get('blocked_dates', [])
        
        if not blocked_dates:
            return []
        
        # Sort blocked dates
        sorted_dates = sorted([datetime.strptime(item['date'], '%Y-%m-%d') for item in blocked_dates])
        
        # Group consecutive dates into ranges
        ranges = []
        if sorted_dates:
            start_date = sorted_dates[0]
            end_date = sorted_dates[0]
            
            for current_date in sorted_dates[1:]:
                if (current_date - end_date).days == 1:
                    # Consecutive date, extend range
                    end_date = current_date
                else:
                    # Gap found, save current range and start new one
                    ranges.append({
                        'start': start_date.strftime('%Y-%m-%d'),
                        'end': end_date.strftime('%Y-%m-%d'),
                        'title': 'Blocked - Not Available'
                    })
                    start_date = current_date
                    end_date = current_date
            
            # Add the last range
            ranges.append({
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d'),
                'title': 'Blocked - Not Available'
            })
        
        return ranges
    
    def compare_with_google_calendar(self, google_events: List[Dict]) -> Dict[str, any]:
        """
        Compare scraped availability with Google Calendar events
        
        Args:
            google_events: List of events from Google Calendar
            
        Returns:
            Comparison results with discrepancies
        """
        rental_data = self.get_calendar_data()
        blocked_dates = {item['date'] for item in rental_data.get('blocked_dates', [])}
        
        # Convert Google Calendar events to date set
        google_blocked = set()
        for event in google_events:
            if 'start' in event and 'date' in event['start']:
                google_blocked.add(event['start']['date'])
            elif 'start' in event and 'dateTime' in event['start']:
                # Convert datetime to date
                dt = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
                google_blocked.add(dt.strftime('%Y-%m-%d'))
        
        # Find discrepancies
        rental_only = blocked_dates - google_blocked  # Blocked on rental site but not in Google
        google_only = google_blocked - blocked_dates  # Blocked in Google but not on rental site
        
        return {
            'total_rental_blocked': len(blocked_dates),
            'total_google_blocked': len(google_blocked),
            'discrepancies': {
                'rental_site_only': list(rental_only),
                'google_calendar_only': list(google_only)
            },
            'sync_needed': len(rental_only) > 0 or len(google_only) > 0,
            'last_compared': datetime.now().isoformat()
        }
