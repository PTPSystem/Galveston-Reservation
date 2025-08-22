#!/bin/bash
#
# Manual Calendar Sync Test
# Run this script to manually test calendar synchronization
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🔄 Starting manual calendar sync test..."
echo "📅 Syncing from: https://www.galvestonislandresortrentals.com/galveston-vacation-rentals/bayfront-retreat"
echo "📍 To Google Calendar: livingbayfront@gmail.com"
echo ""

cd "$PROJECT_DIR" || exit 1

# Run the sync with real-time output
docker compose exec -T app python3 /app/scripts/calendar_sync_cron.py

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Calendar sync test completed successfully!"
else
    echo "❌ Calendar sync test failed with exit code: $EXIT_CODE"
fi

echo ""
echo "📝 Check logs in: $PROJECT_DIR/logs/"
echo ""
