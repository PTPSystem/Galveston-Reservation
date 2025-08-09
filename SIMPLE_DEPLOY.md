# Galveston Reservation System - Simple Windows Deployment

This guide covers deploying the Galveston Reservation System on Windows Server using simple Python-based methods without IIS or Apache.

## Simple Deployment Options

### Option 1: Python Flask Development Server (Quick Start)

For testing and small-scale deployment:

```powershell
# Navigate to project directory
cd "C:\Users\Administrator\Documents\Galveston-Reservation"

# Activate virtual environment
.\.venv\Scripts\activate

# Set production environment
$env:FLASK_ENV="production"

# Run with specific host and port
python run.py
```

**Pros:** Simple, no additional setup
**Cons:** Not suitable for high traffic, single-threaded

### Option 2: Waitress WSGI Server (Recommended)

Waitress is a pure Python WSGI server that works great on Windows:

1. Install Waitress:
```powershell
.\.venv\Scripts\activate
pip install waitress
```

2. Create `server.py`:
```python
from waitress import serve
from app import create_app
import os

if __name__ == '__main__':
    app = create_app()
    
    # Get configuration from environment
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8080))
    
    print(f"🏖️  Starting Galveston Reservation System on {host}:{port}")
    print(f"🌐 Access at: http://{host}:{port}")
    
    serve(app, host=host, port=port, threads=4)
```

3. Run the server:
```powershell
.\.venv\Scripts\activate
python server.py
```

### Option 3: Windows Service with Waitress

For automatic startup and background operation:

1. Install additional packages:
```powershell
.\.venv\Scripts\activate
pip install waitress pywin32
```

2. Create `windows_service.py`:
```python
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import threading
import time

# Add project directory to Python path
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)

class GalvestonReservationService(win32serviceutil.ServiceFramework):
    _svc_name_ = "GalvestonReservation"
    _svc_display_name_ = "Galveston Reservation System"
    _svc_description_ = "Web service for Galveston rental bookings"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.server_thread = None
        socket.setdefaulttimeout(60)
    
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STOPPED,
            (self._svc_name_, '')
        )
    
    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.main()
    
    def main(self):
        try:
            # Change to project directory
            os.chdir(PROJECT_DIR)
            
            # Start the web server in a separate thread
            from waitress import serve
            from app import create_app
            
            app = create_app()
            host = os.getenv('HOST', '0.0.0.0')
            port = int(os.getenv('PORT', 8080))
            
            def run_server():
                serve(app, host=host, port=port, threads=4)
            
            self.server_thread = threading.Thread(target=run_server)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, f'Server started on {host}:{port}')
            )
            
            # Wait for stop signal
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            
        except Exception as e:
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_ERROR_TYPE,
                servicemanager.PYS_SERVICE_STOPPED,
                (self._svc_name_, str(e))
            )

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(GalvestonReservationService)
```

3. Install and manage the service:
```powershell
# Install service (run as Administrator)
python windows_service.py install

# Start service
python windows_service.py start

# Stop service
python windows_service.py stop

# Remove service
python windows_service.py remove
```

### Option 4: Task Scheduler (Simplest Auto-Start)

For automatic startup without Windows Service complexity:

1. Create `start_server.bat`:
```batch
@echo off
cd /d "C:\Users\Administrator\Documents\Galveston-Reservation"
call .venv\Scripts\activate
python server.py
```

2. Create `start_server.ps1` (PowerShell version):
```powershell
Set-Location "C:\Users\Administrator\Documents\Galveston-Reservation"
& .\.venv\Scripts\activate.ps1
python server.py
```

3. Use Windows Task Scheduler:
   - Open Task Scheduler
   - Create Basic Task
   - Name: "Galveston Reservation System"
   - Trigger: At system startup
   - Action: Start a program
   - Program: `powershell.exe`
   - Arguments: `-File "C:\Users\Administrator\Documents\Galveston-Reservation\start_server.ps1"`
   - Check "Run with highest privileges"

## SSL/HTTPS Setup (Simple)

### Option 1: Cloudflare (Recommended - Free SSL)

1. Add your domain to Cloudflare
2. Set DNS record: `str` -> `A` -> `Your-Server-IP`
3. Enable SSL/TLS encryption (Full or Flexible)
4. Your app runs on HTTP locally, Cloudflare provides HTTPS

### Option 2: Self-Signed Certificate (Development)

```python
# Add to server.py for HTTPS
from waitress import serve
import ssl

if __name__ == '__main__':
    app = create_app()
    
    # Create SSL context
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain('cert.pem', 'key.pem')  # Generate these
    
    serve(app, host='0.0.0.0', port=443, url_scheme='https')
```

Generate self-signed certificate:
```powershell
# Using OpenSSL (install from https://slproweb.com/products/Win32OpenSSL.html)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

## Port Configuration

### Windows Firewall
```powershell
# Allow inbound traffic on port 8080
New-NetFirewallRule -DisplayName "Galveston Reservation" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow
```

### Domain Setup
Update your DNS to point `str.ptpsystem.com` to your server:
- If using Cloudflare: `str` -> `A` -> `Your-Server-IP`
- Direct DNS: Create A record for `str.ptpsystem.com`

## Complete Setup Script

Create `simple_deploy.ps1`:

```powershell
# Galveston Reservation System - Simple Deployment Script

Write-Host "🏖️  Setting up Galveston Reservation System" -ForegroundColor Cyan

# Navigate to project directory
Set-Location "C:\Users\Administrator\Documents\Galveston-Reservation"

# Activate virtual environment
& .\.venv\Scripts\activate

# Install Waitress
Write-Host "📦 Installing Waitress server..." -ForegroundColor Yellow
pip install waitress

# Copy environment template
if (!(Test-Path ".env")) {
    Write-Host "📝 Creating .env file..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "⚠️  Please edit .env with your configuration!" -ForegroundColor Red
}

# Create server script
Write-Host "🖥️  Creating server script..." -ForegroundColor Yellow
@"
from waitress import serve
from app import create_app
import os

if __name__ == '__main__':
    app = create_app()
    
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8080))
    
    print(f"🏖️  Starting Galveston Reservation System")
    print(f"🌐 Local access: http://localhost:{port}")
    print(f"🌐 Network access: http://str.ptpsystem.com:{port}")
    print(f"📧 Admin email: {os.getenv('ADMIN_EMAIL', 'admin@ptpsystem.com')}")
    print(f"📧 Calendar: {os.getenv('GOOGLE_CALENDAR_ID', 'bayfrontliving@gmail.com')}")
    print("")
    print("Press Ctrl+C to stop the server")
    
    serve(app, host=host, port=port, threads=4)
"@ | Out-File -FilePath "server.py" -Encoding UTF8

# Create startup batch file
@"
@echo off
cd /d "C:\Users\Administrator\Documents\Galveston-Reservation"
call .venv\Scripts\activate
python server.py
pause
"@ | Out-File -FilePath "start_server.bat" -Encoding ASCII

# Initialize database
Write-Host "🗄️  Initializing database..." -ForegroundColor Yellow
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('Database initialized')"

# Configure firewall
Write-Host "🔥 Configuring Windows Firewall..." -ForegroundColor Yellow
try {
    New-NetFirewallRule -DisplayName "Galveston Reservation System" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow -ErrorAction SilentlyContinue
    Write-Host "✅ Firewall rule added for port 8080" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Could not add firewall rule. Please add manually." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env with your Google Calendar and email settings"
Write-Host "2. Add Google API credentials to secrets/ folder"
Write-Host "3. Run: python server.py"
Write-Host "4. Visit: http://localhost:8080"
Write-Host ""
Write-Host "🌐 For public access, configure your DNS to point str.ptpsystem.com to this server"
Write-Host "🔒 For HTTPS, use Cloudflare or configure SSL certificates"
```

## Running the Simple Deployment

1. **Quick Start:**
   ```powershell
   # Run the setup script
   .\simple_deploy.ps1
   
   # Edit your .env file with real values
   notepad .env
   
   # Start the server
   python server.py
   ```

2. **Access your application:**
   - Locally: `http://localhost:8080`
   - Network: `http://your-server-ip:8080`
   - Domain (after DNS setup): `http://str.ptpsystem.com:8080`

3. **For HTTPS/SSL:**
   - Use Cloudflare (easiest - free SSL proxy)
   - Or configure certificates directly in Waitress

This approach is much simpler than IIS/Apache and works great for small to medium-scale applications!

## Advantages of This Approach

✅ **Simple:** No complex web server configuration
✅ **Pure Python:** Uses familiar Python ecosystem
✅ **Windows-friendly:** Waitress is designed for Windows
✅ **Auto-start:** Can use Windows Service or Task Scheduler
✅ **SSL-ready:** Easy integration with Cloudflare or certificates
✅ **Scalable:** Can handle multiple concurrent requests
✅ **Maintainable:** Standard Python debugging and monitoring

## Production Considerations

- Monitor with built-in `/health` endpoint
- Use Cloudflare for SSL and CDN
- Set up automated backups of database
- Configure log rotation
- Use environment variables for secrets
