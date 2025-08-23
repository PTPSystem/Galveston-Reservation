"""
Improved Galveston Island Resort Rentals Calendar Scraper
Successfully extracts availability data from the booking website
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
import time
import re
from typing import Dict, List, Optional

class GalvestonRentalScraper:
    def __init__(self):
        # Import config here to avoid circular imports
        from app.config import config
        
        self.base_url = "https://www.galvestonislandresortrentals.com"
        self.property_url = config.PROPERTY_MANAGEMENT_URL
        self.logger = logging.getLogger(__name__)
        
        # Headers that work with the website
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
    def scrape_availability(self, months_ahead: int = 6) -> Dict[str, any]:
        """
        Scrape availability for Bayfront Retreat
        
        Args:
            months_ahead: Number of months to look ahead
            
        Returns:
            Dictionary with availability data
        """
        try:
            self.logger.info(f"Scraping availability from: {self.property_url}")
            
            session = requests.Session()
            session.headers.update(self.headers)
            
            # Be respectful with delays
            time.sleep(2)
            
            response = session.get(self.property_url, timeout=30)
            response.raise_for_status()
            
            self.logger.info(f"Successfully fetched page ({len(response.content)} bytes)")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse the calendar data
            return self._parse_calendar_data(soup)
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch calendar data: {e}")
            return {'error': str(e), 'available_dates': [], 'blocked_dates': []}
        except Exception as e:
            self.logger.error(f"Error parsing calendar data: {e}")
            return {'error': str(e), 'available_dates': [], 'blocked_dates': []}
    
    def _parse_calendar_data(self, soup: BeautifulSoup) -> Dict[str, any]:
        """
        Parse the HTML to extract calendar availability data
        
        Args:
            soup: BeautifulSoup object with the page HTML
            
        Returns:
            Dictionary with parsed availability data
        """
        available_dates = []
        blocked_dates = []
        
        # Find all calendar tables
        calendar_tables = soup.find_all('table', class_=lambda x: x and 'calendar' in str(x).lower())
        
        self.logger.info(f"Found {len(calendar_tables)} calendar tables")
        
        # Current year for context
        current_year = datetime.now().year
        
        for table in calendar_tables:
            # Try to find month/year context
            month_year = self._extract_month_year(table)
            
            if not month_year:
                continue
                
            month, year = month_year
            
            self.logger.info(f"Processing calendar for {month}/{year}")
            
            # Find all day cells with availability classes
            day_cells = table.find_all(['td', 'div'], class_=lambda x: x and any(
                cls in str(x) for cls in ['av-O', 'av-X', 'day']))
            
            for cell in day_cells:
                day_info = self._parse_day_cell(cell, month, year)
                if day_info:
                    if day_info['status'] == 'available':
                        available_dates.append(day_info)
                    elif day_info['status'] == 'blocked':
                        blocked_dates.append(day_info)
        
        # Also look for day cells outside of tables (in case of different structure)
        if not available_dates and not blocked_dates:
            self.logger.info("No data from tables, trying alternative parsing...")
            all_day_cells = soup.find_all(class_=lambda x: x and any(
                cls in str(x) for cls in ['av-O', 'av-X', 'day']))
            
            self.logger.info(f"Found {len(all_day_cells)} day cells with av- classes")
            
            # Try to extract dates from these cells
            for cell in all_day_cells[:50]:  # Limit to first 50 for analysis
                try:
                    classes = cell.get('class', [])
                    text = cell.get_text(strip=True)
                    
                    # Skip legend/key elements
                    if 'rcav-key' in classes or not text or len(text) > 2:
                        continue
                    
                    # Try to determine if this is a valid day
                    if text.isdigit() and 1 <= int(text) <= 31:
                        day = int(text)
                        
                        # Determine status from classes
                        if any('av-O' in cls for cls in classes):
                            status = 'available'
                        elif any('av-X' in cls for cls in classes):
                            status = 'blocked'
                        else:
                            continue
                        
                        # We need to infer the month/year - this is tricky
                        # For now, use current month as a starting point
                        estimated_date = self._estimate_date_for_day(day, soup, cell)
                        
                        if estimated_date:
                            day_info = {
                                'date': estimated_date.strftime('%Y-%m-%d'),
                                'day': day,
                                'status': status,
                                'check_in_allowed': any('av-IN' in cls for cls in classes),
                                'check_out_allowed': any('av-OUT' in cls for cls in classes)
                            }
                            
                            if status == 'available':
                                available_dates.append(day_info)
                            elif status == 'blocked':
                                blocked_dates.append(day_info)
                                
                except (ValueError, TypeError):
                    continue
        
        self.logger.info(f"Parsed {len(available_dates)} available dates and {len(blocked_dates)} blocked dates")
        
        return {
            'available_dates': available_dates,
            'blocked_dates': blocked_dates,
            'total_available': len(available_dates),
            'total_blocked': len(blocked_dates),
            'last_updated': datetime.now().isoformat(),
            'source': 'galvestonislandresortrentals.com'
        }
    
    def _extract_month_year(self, table) -> Optional[tuple]:
        """Extract month and year from table context"""
        try:
            # Look for caption with month/year
            caption = table.find('caption')
            if caption:
                caption_text = caption.get_text().strip()
                # Pattern like "August 2025"
                match = re.search(r'(\w+)\s+(\d{4})', caption_text)
                if match:
                    month_name, year = match.groups()
                    month_num = self._month_name_to_number(month_name)
                    if month_num:
                        return month_num, int(year)
            
            # Look in nearby headers
            headers = table.find_previous_siblings(['h1', 'h2', 'h3', 'h4', 'div'])
            for header in headers[:3]:  # Check previous 3 siblings
                if header:
                    header_text = header.get_text().strip()
                    match = re.search(r'(\w+)\s+(\d{4})', header_text)
                    if match:
                        month_name, year = match.groups()
                        month_num = self._month_name_to_number(month_name)
                        if month_num:
                            return month_num, int(year)
            
            return None
        except Exception:
            return None
    
    def _parse_day_cell(self, cell, month: int, year: int) -> Optional[Dict]:
        """Parse individual day cell for availability info"""
        try:
            text = cell.get_text(strip=True)
            classes = cell.get('class', [])
            
            # Skip if not a valid day number
            if not text.isdigit() or not (1 <= int(text) <= 31):
                return None
            
            day = int(text)
            
            # Create date object
            try:
                date_obj = datetime(year, month, day)
            except ValueError:
                return None  # Invalid date
            
            # Determine status from classes
            if any('av-O' in cls for cls in classes):
                status = 'available'
            elif any('av-X' in cls for cls in classes):
                status = 'blocked'
            else:
                return None  # No clear status
            
            return {
                'date': date_obj.strftime('%Y-%m-%d'),
                'day': day,
                'month': month,
                'year': year,
                'status': status,
                'check_in_allowed': any('av-IN' in cls for cls in classes),
                'check_out_allowed': any('av-OUT' in cls for cls in classes),
                'classes': classes
            }
            
        except (ValueError, TypeError):
            return None
    
    def _estimate_date_for_day(self, day: int, soup: BeautifulSoup, cell) -> Optional[datetime]:
        """Try to estimate the month/year for a day cell"""
        try:
            # This is a fallback method - look for month context around the cell
            current_date = datetime.now()
            
            # Start with current month and try a few months ahead
            for month_offset in range(12):  # Check next 12 months
                try_date = current_date.replace(day=1) + timedelta(days=32 * month_offset)
                try_date = try_date.replace(day=day)
                
                # Check if this date makes sense (not too far in the past)
                if try_date >= current_date.replace(hour=0, minute=0, second=0, microsecond=0):
                    return try_date
            
            return None
        except Exception:
            return None
    
    def _month_name_to_number(self, month_name: str) -> Optional[int]:
        """Convert month name to number"""
        months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        return months.get(month_name.lower())
    
    def get_blocked_date_ranges(self) -> List[Dict[str, str]]:
        """
        Get blocked date ranges for calendar sync
        
        Returns:
            List of date ranges that are blocked
        """
        calendar_data = self.scrape_availability()
        blocked_dates = calendar_data.get('blocked_dates', [])
        
        if not blocked_dates:
            return []
        
        # Sort blocked dates
        sorted_dates = sorted([
            datetime.strptime(item['date'], '%Y-%m-%d') 
            for item in blocked_dates
        ])
        
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
                        'title': 'Blocked - Not Available',
                        'summary': 'Property not available for booking'
                    })
                    start_date = current_date
                    end_date = current_date
            
            # Add the last range
            ranges.append({
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d'),
                'title': 'Blocked - Not Available',
                'summary': 'Property not available for booking'
            })
        
        return ranges
