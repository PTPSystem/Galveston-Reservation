#!/bin/bash
#
# Setup Calendar Sync Cron Job
# This script installs the calendar sync cron job on the server
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Setting up calendar sync cron job..."

# Make scripts executable
chmod +x "$SCRIPT_DIR/calendar_sync_cron.sh"
chmod +x "$SCRIPT_DIR/calendar_sync_cron.py"

# Copy the cron job script to the server if we're running locally
if [ "$(hostname)" != "$(ssh howardshen@83.229.35.162 hostname 2>/dev/null || echo 'local')" ]; then
    echo "Copying scripts to server..."
    scp "$SCRIPT_DIR/calendar_sync_cron.sh" howardshen@83.229.35.162:~/galveston-reservation/scripts/
    scp "$SCRIPT_DIR/calendar_sync_cron.py" howardshen@83.229.35.162:~/galveston-reservation/scripts/
    
    echo "Setting up cron job on server..."
    ssh howardshen@83.229.35.162 << 'EOF'
        cd ~/galveston-reservation/scripts
        chmod +x calendar_sync_cron.sh calendar_sync_cron.py
        
        # Create cron job entry (runs every 2 hours)
        CRON_JOB="0 */2 * * * $HOME/galveston-reservation/scripts/calendar_sync_cron.sh"
        
        # Check if cron job already exists
        if crontab -l 2>/dev/null | grep -q "calendar_sync_cron.sh"; then
            echo "Cron job already exists, updating..."
            (crontab -l 2>/dev/null | grep -v "calendar_sync_cron.sh"; echo "$CRON_JOB") | crontab -
        else
            echo "Adding new cron job..."
            (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
        fi
        
        echo "Current crontab:"
        crontab -l
EOF
else
    echo "Running on server, setting up cron job..."
    
    # Create cron job entry (runs every 2 hours)
    CRON_JOB="0 */2 * * * $PROJECT_DIR/scripts/calendar_sync_cron.sh"
    
    # Check if cron job already exists
    if crontab -l 2>/dev/null | grep -q "calendar_sync_cron.sh"; then
        echo "Cron job already exists, updating..."
        (crontab -l 2>/dev/null | grep -v "calendar_sync_cron.sh"; echo "$CRON_JOB") | crontab -
    else
        echo "Adding new cron job..."
        (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    fi
    
    echo "Current crontab:"
    crontab -l
fi

echo ""
echo "✅ Calendar sync cron job setup completed!"
echo ""
echo "The job will run every 2 hours and sync blocked dates from:"
echo "https://www.galvestonislandresortrentals.com/galveston-vacation-rentals/bayfront-retreat"
echo ""
echo "To your Google Calendar: livingbayfront@gmail.com"
echo ""
echo "Logs will be stored in: $PROJECT_DIR/logs/"
echo ""
echo "To test the sync manually, run:"
echo "  $PROJECT_DIR/scripts/calendar_sync_cron.sh"
