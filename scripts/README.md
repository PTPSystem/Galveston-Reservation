# Scripts Directory

This directory contains utility scripts for setup, deployment, and maintenance of the Galveston Reservation System.

## Setup Scripts

- `init_db.py` - Initialize the SQLite database with required tables
- `setup.py` - System setup and configuration script
- `setup_firewall.ps1` - Windows Firewall configuration for port 80
- `setup_firewall_fixed.ps1` - Enhanced firewall setup script

## Deployment Scripts

- `start_production.bat` - Start production server on Windows
- `start_server.bat` - Start development server on Windows  
- `simple_deploy.ps1` - PowerShell deployment automation

## Maintenance Scripts

- `smart_calendar_sync.py` - Calendar synchronization utility
- `check_specific_dates.py` - Date-specific availability checker

## Usage Examples

```bash
# Initialize database
python scripts/init_db.py

# Run calendar sync
python scripts/smart_calendar_sync.py

# Start production (Windows)
scripts/start_production.bat

# Configure firewall (run as Administrator)
PowerShell -ExecutionPolicy Bypass -File scripts/setup_firewall.ps1
```

## Prerequisites

- Python 3.11+
- Required packages from requirements.txt
- Proper environment configuration (.env file)
- Administrator privileges for firewall scripts
