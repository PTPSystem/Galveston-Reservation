#!/usr/bin/env python3
"""
Enhanced Calendar Sync with Change Detection
Synchronizes blocked dates AND detects changes to booking events
"""
import sys
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.calendar_sync import CalendarSyncService
from app.services.calendar_change_detection import CalendarChangeDetectionService
from app import create_app

# Set up logging
try:
    log_dir = Path(__file__).parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f'calendar_sync_enhanced_{datetime.now().strftime("%Y%m%d")}.log'
    
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

def run_calendar_sync(dry_run: bool = True):
    """Run the standard calendar sync process"""
    try:
        logger.info("Starting standard calendar sync...")
        
        sync_service = CalendarSyncService()
        result = sync_service.sync_blocked_dates_to_google(dry_run=dry_run)
        
        logger.info(f"Calendar sync completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in calendar sync: {e}")
        return {'success': False, 'error': str(e)}

def run_change_detection():
    """Run calendar change detection and notifications"""
    try:
        logger.info("Starting calendar change detection...")
        
        change_service = CalendarChangeDetectionService()
        
        # Detect changes in the last 7 days
        changes = change_service.detect_booking_changes(days_back=7)
        
        if not changes:
            logger.info("No calendar changes detected")
            return {'success': True, 'changes': 0, 'notifications': 0}
        
        logger.info(f"Detected {len(changes)} calendar changes")
        
        # Send notifications for changes
        notification_results = change_service.send_change_notifications(changes)
        
        logger.info(f"Notification results: {notification_results}")
        
        # Log each change for reference
        for change in changes:
            logger.info(f"Change detected - Booking ID: {change.booking_id}, "
                       f"Type: {change.change_type}, "
                       f"Guest: {change.guest_email}")
        
        return {
            'success': True,
            'changes': len(changes),
            'notifications': notification_results
        }
        
    except Exception as e:
        logger.error(f"Error in change detection: {e}")
        return {'success': False, 'error': str(e)}

def main():
    """Main enhanced sync function"""
    logger.info("=" * 60)
    logger.info("Starting Enhanced Calendar Sync with Change Detection")
    logger.info("=" * 60)
    
    # Create Flask application context
    app = create_app()
    
    with app.app_context():
        try:
            # Step 1: Run standard calendar sync
            sync_result = run_calendar_sync(dry_run=False)  # Set to True for testing
            
            # Step 2: Run change detection
            change_result = run_change_detection()
            
            # Summary
            logger.info("=" * 60)
            logger.info("Enhanced Calendar Sync Summary:")
            logger.info(f"Standard Sync: {'Success' if sync_result.get('success') else 'Failed'}")
            logger.info(f"Change Detection: {'Success' if change_result.get('success') else 'Failed'}")
            logger.info(f"Changes Detected: {change_result.get('changes', 0)}")
            logger.info(f"Notifications Sent: {change_result.get('notifications', {})}")
            logger.info("=" * 60)
            
            return {
                'sync_result': sync_result,
                'change_result': change_result
            }
            
        except Exception as e:
            logger.error(f"Fatal error in enhanced calendar sync: {e}")
            return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    result = main()
    
    # Exit with appropriate code
    if not result.get('sync_result', {}).get('success', False) or \
       not result.get('change_result', {}).get('success', False):
        sys.exit(1)
    else:
        sys.exit(0)
