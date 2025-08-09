# Galveston Reservation System - Simple Deployment Script
# Run this script to set up the system with Waitress server

Write-Host "🏖️  Setting up Galveston Reservation System" -ForegroundColor Cyan

# Navigate to project directory
$ProjectPath = "C:\Users\Administrator\Documents\Galveston-Reservation"
Set-Location $ProjectPath

# Check if virtual environment exists
if (!(Test-Path ".venv")) {
    Write-Host "❌ Virtual environment not found. Please run setup.py first!" -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "🐍 Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\activate.ps1

# Install Waitress if not already installed
Write-Host "📦 Installing Waitress server..." -ForegroundColor Yellow
& .\.venv\Scripts\pip install waitress

# Create environment file if it doesn't exist
if (!(Test-Path ".env")) {
    Write-Host "📝 Creating .env file..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "⚠️  Please edit .env with your configuration!" -ForegroundColor Red
}

# Create startup batch file
Write-Host "🖥️  Creating startup scripts..." -ForegroundColor Yellow
@"
@echo off
cd /d "$ProjectPath"
call .venv\Scripts\activate
echo Starting Galveston Reservation System...
python server.py
pause
"@ | Out-File -FilePath "start_server.bat" -Encoding ASCII

# Create PowerShell startup script
@"
Set-Location "$ProjectPath"
& .\.venv\Scripts\activate.ps1
python server.py
"@ | Out-File -FilePath "start_server.ps1" -Encoding UTF8

# Initialize database
Write-Host "🗄️  Initializing database..." -ForegroundColor Yellow
try {
    & .\.venv\Scripts\python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('✅ Database initialized successfully')"
} catch {
    Write-Host "⚠️  Database initialization failed. Check your configuration." -ForegroundColor Red
}

# Configure Windows Firewall
Write-Host "🔥 Configuring Windows Firewall..." -ForegroundColor Yellow
try {
    $FirewallRule = Get-NetFirewallRule -DisplayName "Galveston Reservation System" -ErrorAction SilentlyContinue
    if (!$FirewallRule) {
        New-NetFirewallRule -DisplayName "Galveston Reservation System" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow
        Write-Host "✅ Firewall rule added for port 8080" -ForegroundColor Green
    } else {
        Write-Host "✅ Firewall rule already exists" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Could not configure firewall. You may need to run as Administrator." -ForegroundColor Yellow
    Write-Host "   Manual step: Allow port 8080 in Windows Firewall" -ForegroundColor Yellow
}

# Create Windows Service installer (optional)
Write-Host "🔧 Creating Windows Service files..." -ForegroundColor Yellow
@"
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import threading

# Add project directory to Python path
PROJECT_DIR = r"$ProjectPath"
sys.path.insert(0, PROJECT_DIR)

class GalvestonReservationService(win32serviceutil.ServiceFramework):
    _svc_name_ = "GalvestonReservation"
    _svc_display_name_ = "Galveston Reservation System"
    _svc_description_ = "Web service for Galveston rental bookings at str.ptpsystem.com"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.server_thread = None
        socket.setdefaulttimeout(60)
    
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
    
    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, 'Service started successfully')
        )
        self.main()
    
    def main(self):
        try:
            os.chdir(PROJECT_DIR)
            
            from waitress import serve
            from app import create_app
            
            app = create_app()
            host = os.getenv('HOST', '0.0.0.0')
            port = int(os.getenv('PORT', 8080))
            
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, f'Server starting on {host}:{port}')
            )
            
            def run_server():
                serve(app, host=host, port=port, threads=4)
            
            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()
            
            # Wait for stop signal
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            
        except Exception as e:
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_ERROR_TYPE,
                servicemanager.PYS_SERVICE_STOPPED,
                (self._svc_name_, f'Service error: {str(e)}')
            )

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(GalvestonReservationService)
"@ | Out-File -FilePath "windows_service.py" -Encoding UTF8

# Create service management script
@"
# Galveston Reservation System - Service Management
# Run as Administrator

param(
    [Parameter(Mandatory=`$true)]
    [ValidateSet("install", "start", "stop", "restart", "remove", "status")]
    [string]`$Action
)

Set-Location "$ProjectPath"
& .\.venv\Scripts\activate.ps1

switch (`$Action) {
    "install" {
        Write-Host "Installing Windows Service..." -ForegroundColor Yellow
        & .\.venv\Scripts\python windows_service.py install
        Write-Host "✅ Service installed. Use 'start' to begin." -ForegroundColor Green
    }
    "start" {
        Write-Host "Starting service..." -ForegroundColor Yellow
        & .\.venv\Scripts\python windows_service.py start
        Write-Host "✅ Service started." -ForegroundColor Green
    }
    "stop" {
        Write-Host "Stopping service..." -ForegroundColor Yellow
        & .\.venv\Scripts\python windows_service.py stop
        Write-Host "✅ Service stopped." -ForegroundColor Green
    }
    "restart" {
        Write-Host "Restarting service..." -ForegroundColor Yellow
        & .\.venv\Scripts\python windows_service.py stop
        Start-Sleep -Seconds 2
        & .\.venv\Scripts\python windows_service.py start
        Write-Host "✅ Service restarted." -ForegroundColor Green
    }
    "remove" {
        Write-Host "Removing service..." -ForegroundColor Yellow
        & .\.venv\Scripts\python windows_service.py stop
        & .\.venv\Scripts\python windows_service.py remove
        Write-Host "✅ Service removed." -ForegroundColor Green
    }
    "status" {
        Get-Service -Name "GalvestonReservation" -ErrorAction SilentlyContinue | Format-Table -AutoSize
    }
}
"@ | Out-File -FilePath "manage_service.ps1" -Encoding UTF8

Write-Host ""
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env file with your settings:"
Write-Host "   - Google Calendar credentials" -ForegroundColor Gray
Write-Host "   - SMTP email configuration" -ForegroundColor Gray
Write-Host "   - Admin email addresses" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Add Google API credentials:"
Write-Host "   - Place client_secrets.json in secrets/ folder" -ForegroundColor Gray
Write-Host "   - Place service-account.json in secrets/ folder" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Start the server:" -ForegroundColor Cyan
Write-Host "   Manual: python server.py" -ForegroundColor Gray
Write-Host "   Batch: start_server.bat" -ForegroundColor Gray
Write-Host "   Service: .\manage_service.ps1 install" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Access your application:" -ForegroundColor Cyan
Write-Host "   Local: http://localhost:8080" -ForegroundColor Gray
Write-Host "   Network: http://str.ptpsystem.com:8080" -ForegroundColor Gray
Write-Host ""
Write-Host "🔒 For HTTPS/SSL:" -ForegroundColor Cyan
Write-Host "   - Use Cloudflare for easy SSL proxy" -ForegroundColor Gray
Write-Host "   - Point str.ptpsystem.com DNS to this server" -ForegroundColor Gray
Write-Host ""
Write-Host "🛠️  Need help? Check SIMPLE_DEPLOY.md for detailed instructions" -ForegroundColor Yellow
