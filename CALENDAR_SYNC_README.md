# Calendar Sync Cron Job Setup

## Overview
Automated synchronization between your Galveston rental booking website and Google Calendar.

## What's Configured

### 🔄 **Automatic Sync**
- **Source**: https://www.galvestonislandresortrentals.com/galveston-vacation-rentals/bayfront-retreat
- **Target**: Google Calendar (livingbayfront@gmail.com)
- **Schedule**: Every 2 hours (00:00, 02:00, 04:00, etc.)
- **What it syncs**: Blocked/booked dates from rental website to Google Calendar

### 📁 **Files Created**
- `scripts/calendar_sync_cron.py` - Main sync logic
- `scripts/calendar_sync_cron.sh` - Shell wrapper for cron
- `scripts/test_calendar_sync.sh` - Manual testing script
- `scripts/setup_calendar_cron.sh` - Installation script

### 📝 **Logs**
- Location: `logs/cron_calendar_sync_YYYYMMDD_HHMMSS.log`
- Automatic cleanup: Logs older than 30 days are deleted
- Real-time output during manual testing

## Usage

### ✅ **Current Status**
```bash
# Check if cron job is running
ssh howardshen@83.229.35.162 'crontab -l'

# View recent logs
ssh howardshen@83.229.35.162 'ls -la ~/galveston-reservation/logs/ | tail -5'
```

### 🧪 **Manual Testing**
```bash
# Test sync manually (recommended before first use)
ssh howardshen@83.229.35.162 '~/galveston-reservation/scripts/test_calendar_sync.sh'

# Or run the direct sync script
ssh howardshen@83.229.35.162 '~/galveston-reservation/scripts/calendar_sync_cron.sh'
```

### 📊 **Monitor Performance**
```bash
# Check latest sync results
ssh howardshen@83.229.35.162 'tail -20 ~/galveston-reservation/logs/$(ls -t ~/galveston-reservation/logs/ | head -1)'

# View sync success/failure status
ssh howardshen@83.229.35.162 'grep -E "(completed successfully|failed)" ~/galveston-reservation/logs/cron_*.log | tail -5'
```

## How It Works

1. **Scraper** extracts availability data from the rental website
2. **Google Calendar API** checks current calendar events
3. **Sync Service** compares data and creates/updates calendar events
4. **Blocked dates** from rental site become calendar events
5. **Logs** track all operations for monitoring

## Last Test Results

✅ **Google Calendar Connection**: Successful  
✅ **Website Scraping**: Found 66 blocked dates, 299 available dates  
✅ **Sync Process**: Completed without errors  
✅ **Cron Job**: Installed and active  

## Troubleshooting

### Common Issues
1. **Permission errors**: Logs show as console output only (normal)
2. **Website timeouts**: Retry mechanism built-in with delays
3. **Calendar API limits**: Google has generous quotas for this usage

### Support Commands
```bash
# Restart containers if needed
ssh howardshen@83.229.35.162 'cd ~/galveston-reservation && docker compose restart'

# Check container health
ssh howardshen@83.229.35.162 'cd ~/galveston-reservation && docker compose ps'

# View live container logs
ssh howardshen@83.229.35.162 'cd ~/galveston-reservation && docker compose logs -f app'
```

## Configuration

The sync job is configured to:
- Run every 2 hours automatically
- Handle website rate limiting with delays
- Sync 6 months ahead of bookings
- Log all operations for monitoring
- Clean up old logs automatically

Your calendar will now stay synchronized with the rental website automatically! 🎉
