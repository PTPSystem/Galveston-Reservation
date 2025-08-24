#!/bin/bash
"""
Deploy Calendar Change Detection
Sets up automatic change detection monitoring
"""

set -e

echo "Deploying Calendar Change Detection System..."
echo "=============================================="

# Configuration
PROJECT_DIR="/Users/howardshen/Library/CloudStorage/OneDrive-Personal/Galveston-Reservation/Galveston-Reservation"
SCRIPT_NAME="calendar_sync_enhanced.py"
CRON_INTERVAL="*/30"  # Every 30 minutes

# Function to check if we're in the right directory
check_directory() {
    if [ ! -f "run.py" ]; then
        echo "Error: Not in the correct project directory"
        echo "Please run this script from: $PROJECT_DIR"
        exit 1
    fi
}

# Function to make scripts executable
make_executable() {
    echo "1. Making scripts executable..."
    chmod +x scripts/calendar_sync_enhanced.py
    chmod +x tests/test_change_detection.py
    echo "   ✓ Scripts are now executable"
}

# Function to test the change detection
test_system() {
    echo ""
    echo "2. Testing change detection system..."
    
    # Test in staging environment first
    export FLASK_ENV=staging
    
    echo "   Running test script..."
    python3 tests/test_change_detection_simple.py
    
    if [ $? -eq 0 ]; then
        echo "   ✓ Change detection test passed"
    else
        echo "   ✗ Change detection test failed"
        exit 1
    fi
}

# Function to set up cron job
setup_cron() {
    echo ""
    echo "3. Setting up cron job for automatic monitoring..."
    
    # Create the cron command
    CRON_COMMAND="$CRON_INTERVAL * * * * cd $PROJECT_DIR && /usr/bin/python3 scripts/calendar_sync_enhanced.py >> logs/calendar_change_detection.log 2>&1"
    
    echo "   Cron command: $CRON_COMMAND"
    
    # Check if cron job already exists
    if crontab -l 2>/dev/null | grep -q "calendar_sync_enhanced.py"; then
        echo "   Calendar change detection cron job already exists"
        echo "   Current cron jobs:"
        crontab -l | grep calendar
    else
        # Add the cron job
        echo "   Adding cron job..."
        (crontab -l 2>/dev/null; echo "$CRON_COMMAND") | crontab -
        echo "   ✓ Cron job added successfully"
    fi
}

# Function to create log directory
setup_logging() {
    echo ""
    echo "4. Setting up logging..."
    
    mkdir -p logs
    touch logs/calendar_change_detection.log
    
    echo "   ✓ Log directory created: logs/calendar_change_detection.log"
}

# Function to show monitoring status
show_status() {
    echo ""
    echo "5. System Status:"
    echo "   =================="
    
    echo "   Active cron jobs:"
    crontab -l | grep calendar || echo "   No calendar-related cron jobs found"
    
    echo ""
    echo "   Log file location: $PROJECT_DIR/logs/calendar_change_detection.log"
    echo "   Test script: $PROJECT_DIR/tests/test_change_detection_simple.py"
    echo "   Main script: $PROJECT_DIR/scripts/calendar_sync_enhanced.py"
    
    echo ""
    echo "   Manual commands:"
    echo "     Test: python3 tests/test_change_detection_simple.py"
    echo "     Run sync: python3 scripts/calendar_sync_enhanced.py"
    echo "     View logs: tail -f logs/calendar_change_detection.log"
}

# Main deployment function
main() {
    cd "$PROJECT_DIR"
    check_directory
    
    echo "Starting deployment from: $(pwd)"
    echo ""
    
    make_executable
    setup_logging
    
    # Ask user if they want to run the test
    read -p "Run test before setting up cron? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        test_system
    fi
    
    # Ask user about cron setup
    read -p "Set up automatic monitoring with cron? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        setup_cron
    fi
    
    show_status
    
    echo ""
    echo "=============================================="
    echo "Calendar Change Detection Deployment Complete!"
    echo ""
    echo "The system will now:"
    echo "• Monitor Google Calendar for booking changes"
    echo "• Send automatic notifications to stakeholders"
    echo "• Log all activities to logs/calendar_change_detection.log"
    echo ""
    echo "No manual intervention required - it runs automatically!"
}

# Run the deployment
main
