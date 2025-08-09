# Galveston Reservation System - Deployment Guide

This guide covers deploying the Galveston Reservation System to a Windows server with SSL certificate for str.ptpsystem.com.

## Prerequisites

- Windows Server with IIS or Apache/Nginx
- Python 3.8+ installed
- Domain str.ptpsystem.com pointing to your server
- SSL certificate for str.ptpsystem.com

## Installation

### 1. Clone and Setup Application

```powershell
# Clone the repository
git clone https://github.com/PTPSystem/Galveston-Reservation.git
cd Galveston-Reservation

# Run setup script
python setup.py
```

### 2. Configure Environment

Edit `.env` file with your production settings:

```env
# Production Configuration
SECRET_KEY=your-production-secret-key-here
FLASK_ENV=production
DEBUG=False

# Domain Configuration
DOMAIN=str.ptpsystem.com
BASE_URL=https://str.ptpsystem.com

# Google Calendar Configuration
GOOGLE_PROJECT_ID=your-google-project-id
GOOGLE_CALENDAR_ID=bayfrontliving@gmail.com
GOOGLE_CREDENTIALS_PATH=./secrets/service-account.json

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-smtp-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@ptpsystem.com

# Admin Configuration
ADMIN_EMAIL=admin@ptpsystem.com
NOTIFICATION_EMAILS=admin@ptpsystem.com,manager@ptpsystem.com,cleaning@ptpsystem.com
```

### 3. Google Calendar API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials:
   - Application type: Web application
   - Authorized redirect URIs: `https://str.ptpsystem.com/auth/callback`
5. Download `client_secrets.json` to `secrets/` folder
6. For server-side access, also create a Service Account:
   - Download service account JSON to `secrets/service-account.json`
   - Share your calendar with the service account email

### 4. Email Configuration

For Gmail SMTP:
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password for SMTP
3. Use the app password in `MAIL_PASSWORD`

## Deployment Options

### Option 1: IIS with FastCGI

1. Install Python and ensure it's in PATH
2. Install `wfastcgi`:
   ```powershell
   pip install wfastcgi
   wfastcgi-enable
   ```

3. Create `web.config` in project root:
   ```xml
   <?xml version="1.0" encoding="utf-8"?>
   <configuration>
     <system.webServer>
       <handlers>
         <add name="Python FastCGI" path="*" verb="*" 
              modules="FastCgiModule" 
              scriptProcessor="C:\Path\To\Python\python.exe|C:\Path\To\Python\Lib\site-packages\wfastcgi.py" 
              resourceType="Unspecified" />
       </handlers>
     </system.webServer>
     <appSettings>
       <add key="WSGI_HANDLER" value="run.app" />
       <add key="PYTHONPATH" value="C:\Path\To\Your\App" />
     </appSettings>
   </configuration>
   ```

### Option 2: Reverse Proxy with Gunicorn

1. Install Gunicorn:
   ```powershell
   .venv\Scripts\activate
   pip install gunicorn
   ```

2. Create `gunicorn_config.py`:
   ```python
   bind = "127.0.0.1:5000"
   workers = 2
   timeout = 30
   keepalive = 2
   max_requests = 1000
   max_requests_jitter = 100
   ```

3. Run with Gunicorn:
   ```powershell
   gunicorn -c gunicorn_config.py run:app
   ```

4. Configure IIS/Nginx as reverse proxy to localhost:5000

### Option 3: Windows Service

1. Install `pywin32`:
   ```powershell
   pip install pywin32
   ```

2. Create Windows Service script `service.py`:
   ```python
   import win32serviceutil
   import win32service
   import win32event
   import servicemanager
   import socket
   import sys
   import os
   
   # Add your app directory to path
   sys.path.insert(0, os.path.dirname(__file__))
   
   from app import create_app
   
   class GalvestonReservationService(win32serviceutil.ServiceFramework):
       _svc_name_ = "GalvestonReservationService"
       _svc_display_name_ = "Galveston Reservation System"
       _svc_description_ = "Web service for managing Galveston rental bookings"
       
       def __init__(self, args):
           win32serviceutil.ServiceFramework.__init__(self, args)
           self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
           socket.setdefaulttimeout(60)
       
       def SvcStop(self):
           self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
           win32event.SetEvent(self.hWaitStop)
       
       def SvcDoRun(self):
           servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                               servicemanager.PYS_SERVICE_STARTED,
                               (self._svc_name_,''))
           self.main()
       
       def main(self):
           app = create_app()
           app.run(host='0.0.0.0', port=5000)
   
   if __name__ == '__main__':
       win32serviceutil.HandleCommandLine(GalvestonReservationService)
   ```

3. Install and start service:
   ```powershell
   python service.py install
   python service.py start
   ```

## SSL Certificate Setup

### Option 1: Let's Encrypt (Recommended)

1. Install Certbot for Windows
2. Obtain certificate:
   ```powershell
   certbot certonly --webroot -w C:\Path\To\Your\App -d str.ptpsystem.com
   ```

### Option 2: Commercial SSL Certificate

1. Purchase SSL certificate for str.ptpsystem.com
2. Install certificate in Windows Certificate Store
3. Bind certificate to IIS site

## Web Server Configuration

### IIS Configuration

1. Create new website in IIS Manager:
   - Site name: Galveston Reservation
   - Physical path: C:\Path\To\Your\App
   - Binding: HTTPS, port 443, hostname: str.ptpsystem.com

2. Configure SSL:
   - Select SSL certificate for str.ptpsystem.com
   - Require SSL: Yes

3. URL Rewrite (optional):
   ```xml
   <rule name="Redirect to HTTPS" stopProcessing="true">
     <match url="(.*)" />
     <conditions>
       <add input="{HTTPS}" pattern="off" ignoreCase="true" />
     </conditions>
     <action type="Redirect" url="https://{HTTP_HOST}/{R:1}" 
             redirectType="Permanent" />
   </rule>
   ```

## Database Setup

For production, consider upgrading to PostgreSQL or SQL Server:

```python
# In .env file
DATABASE_URL=postgresql://username:password@localhost/galveston_reservations
# or
DATABASE_URL=mssql+pyodbc://username:password@server/database?driver=ODBC+Driver+17+for+SQL+Server
```

## Monitoring and Logging

1. Set up log rotation in `logs/` directory
2. Configure Windows Event Log integration
3. Set up monitoring for:
   - Application health (`/health` endpoint)
   - Email delivery status
   - Google Calendar API quota
   - Database performance

## Security Considerations

1. **Firewall**: Only allow ports 80, 443
2. **Environment Variables**: Store secrets in Windows Credential Manager
3. **File Permissions**: Restrict access to `secrets/` directory
4. **SSL**: Use strong ciphers and TLS 1.2+
5. **Updates**: Regularly update Python packages and OS

## Backup Strategy

1. **Database**: Regular automated backups
2. **Secrets**: Secure backup of `secrets/` directory
3. **Application**: Version control with Git
4. **Configuration**: Backup `.env` and config files

## Testing Deployment

1. **Health Check**: Visit `https://str.ptpsystem.com/health`
2. **Calendar Integration**: Test Google Calendar connection
3. **Email**: Submit test booking request
4. **SSL**: Verify certificate validity and security headers

## Troubleshooting

### Common Issues

1. **Google Calendar API Errors**:
   - Check service account permissions
   - Verify calendar sharing settings
   - Monitor API quota usage

2. **Email Delivery Issues**:
   - Verify SMTP credentials
   - Check spam folder
   - Test with different email providers

3. **SSL Certificate Issues**:
   - Verify DNS propagation
   - Check certificate chain
   - Validate domain ownership

### Logs Location

- Application logs: `logs/`
- IIS logs: `C:\inetpub\logs\LogFiles\`
- Windows Event Logs: Event Viewer > Application

### Performance Optimization

1. **Caching**: Implement Redis for session storage
2. **CDN**: Use CloudFlare for static assets
3. **Database**: Add indexes for frequent queries
4. **Monitoring**: Set up APM tools

## Maintenance Tasks

### Daily
- Monitor booking requests
- Check email delivery
- Review error logs

### Weekly
- Update calendar sync
- Backup database
- Review security logs

### Monthly
- Update SSL certificate (if needed)
- Review system performance
- Update Python packages
- Test disaster recovery procedures

## Support

For deployment issues:
1. Check logs in `logs/` directory
2. Verify all environment variables are set
3. Test Google Calendar API access
4. Validate email configuration
5. Create GitHub issue with error details

## Scaling Considerations

For high traffic:
1. **Load Balancer**: Multiple app instances
2. **Database**: Master-slave replication
3. **Caching**: Redis cluster
4. **CDN**: Static asset distribution
5. **Monitoring**: Application performance monitoring
