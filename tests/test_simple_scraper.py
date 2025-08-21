"""
Simple test script to check rental website accessibility
"""
import requests
from bs4 import BeautifulSoup
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_website_access():
    """Test different approaches to access the rental website"""
    
    # Better headers to avoid blocking
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    urls_to_test = [
        "https://www.galvestonislandresortrentals.com/galveston-vacation-rentals/bayfront-retreat",
        "https://www.galvestonislandresortrentals.com",
        "https://galvestonislandresortrentals.com"
    ]
    
    session = requests.Session()
    session.headers.update(headers)
    
    for url in urls_to_test:
        logger.info(f"Testing URL: {url}")
        try:
            # Add delay to be respectful
            time.sleep(2)
            
            response = session.get(url, timeout=30)
            logger.info(f"Status: {response.status_code}")
            logger.info(f"Response size: {len(response.content)} bytes")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Check for title
                title = soup.title.string if soup.title else "No title"
                logger.info(f"Page title: {title}")
                
                # Look for calendar-related elements
                calendar_elements = soup.find_all(['div', 'table'], 
                    class_=lambda x: x and any(term in str(x).lower() for term in ['calendar', 'rcav', 'availability']))
                
                logger.info(f"Found {len(calendar_elements)} calendar-related elements")
                
                # Look for date cells
                date_cells = soup.find_all(['td', 'span'], 
                    class_=lambda x: x and any(term in str(x) for term in ['av-', 'day', 'mday']))
                
                logger.info(f"Found {len(date_cells)} potential date cells")
                
                # Sample some content
                if date_cells:
                    logger.info("Sample date cells:")
                    for i, cell in enumerate(date_cells[:5]):
                        classes = cell.get('class', [])
                        text = cell.get_text(strip=True)
                        logger.info(f"  Cell {i+1}: classes={classes}, text='{text}'")
                
                # Check for any JavaScript that might load calendar data
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string and ('calendar' in script.string.lower() or 'rcav' in script.string.lower()):
                        logger.info("Found calendar-related JavaScript")
                        break
                
                logger.info(f"✓ Successfully accessed {url}")
                
                # Save a sample of the HTML for analysis
                if 'bayfront-retreat' in url:
                    with open('sample_page.html', 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    logger.info("Saved sample HTML to sample_page.html")
                
                return True
                
            else:
                logger.error(f"HTTP {response.status_code}: {response.reason}")
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout accessing {url}")
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error for {url}")
        except Exception as e:
            logger.error(f"Error accessing {url}: {e}")
        
        logger.info("---")
    
    return False

def test_calendar_parsing():
    """Test parsing the saved HTML file for calendar data"""
    try:
        with open('sample_page.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        logger.info("Analyzing saved HTML for calendar structure...")
        
        # Look for different calendar structures
        calendar_containers = soup.find_all(['div', 'section'], 
            class_=lambda x: x and any(term in str(x).lower() for term in ['calendar', 'availability', 'booking']))
        
        logger.info(f"Found {len(calendar_containers)} calendar containers")
        
        # Look for tables that might contain calendar data
        tables = soup.find_all('table')
        logger.info(f"Found {len(tables)} tables total")
        
        calendar_tables = [t for t in tables if t.find_all('td') and len(t.find_all('td')) > 7]
        logger.info(f"Found {len(calendar_tables)} tables that look like calendars")
        
        # Look for month navigation or month headers
        month_headers = soup.find_all(text=lambda text: text and any(
            month in text for month in ['January', 'February', 'March', 'April', 'May', 'June',
                                      'July', 'August', 'September', 'October', 'November', 'December']))
        
        logger.info(f"Found {len(month_headers)} month references")
        
        # Look for specific availability classes mentioned in your original request
        av_elements = soup.find_all(class_=lambda x: x and ('av-' in str(x)))
        logger.info(f"Found {len(av_elements)} elements with 'av-' classes")
        
        if av_elements:
            logger.info("Sample availability elements:")
            for i, elem in enumerate(av_elements[:5]):
                classes = elem.get('class', [])
                text = elem.get_text(strip=True)
                logger.info(f"  Element {i+1}: classes={classes}, text='{text}'")
        
        return len(av_elements) > 0
        
    except FileNotFoundError:
        logger.error("sample_page.html not found - run test_website_access first")
        return False
    except Exception as e:
        logger.error(f"Error parsing saved HTML: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting rental website accessibility test...")
    
    if test_website_access():
        logger.info("\n" + "="*50)
        logger.info("Now testing calendar parsing...")
        test_calendar_parsing()
    else:
        logger.error("Could not access website")
    
    logger.info("Test completed.")
