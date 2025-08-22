#!/bin/bash
#
# Calendar Sync Cron Job Wrapper
# This script runs the Python calendar sync in the Docker container
#

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Log file with timestamp
LOG_FILE="$PROJECT_DIR/logs/cron_calendar_sync_$(date +%Y%m%d_%H%M%S).log"

# Ensure logs directory exists
mkdir -p "$PROJECT_DIR/logs"

echo "$(date): Starting calendar sync cron job" >> "$LOG_FILE"

# Change to project directory
cd "$PROJECT_DIR" || {
    echo "$(date): Failed to change to project directory: $PROJECT_DIR" >> "$LOG_FILE"
    exit 1
}

# Run the sync script inside the Docker container
docker compose exec -T app python3 /app/scripts/calendar_sync_cron.py >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "$(date): Calendar sync completed successfully" >> "$LOG_FILE"
else
    echo "$(date): Calendar sync failed with exit code: $EXIT_CODE" >> "$LOG_FILE"
fi

# Keep only last 30 days of logs
find "$PROJECT_DIR/logs" -name "cron_calendar_sync_*.log" -mtime +30 -delete 2>/dev/null

exit $EXIT_CODE
