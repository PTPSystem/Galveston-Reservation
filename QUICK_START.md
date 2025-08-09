# Galveston Reservation System - Quick Start Guide

## ✅ What We've Built

You now have a complete web-based reservation system for your Galveston rental property:

### 🏗️ **Core Features:**
1. **Web Interface** at str.ptpsystem.com
2. **Booking Calendar** - Synced with BayfrontLiving@gmail.com
3. **Request System** - Users submit booking requests
4. **Email Workflow** - Approve/reject via email links
5. **Google Calendar Integration** - Auto-creates calendar events
6. **Admin Dashboard** - Manage all bookings

### 🛠️ **Technical Stack:**
- **Python Flask** web framework
- **SQLite database** for booking storage
- **Google Calendar API** for calendar sync
- **SMTP email** for notifications
- **Waitress server** for Windows deployment

## 🚀 Simple Deployment (No IIS/Apache Required)

### **Option 1: Quick Test** (Recommended First Step)

1. **Open PowerShell as Administrator** in your project folder
2. **Run the setup:**
   ```powershell
   cd "C:\Users\Administrator\Documents\Galveston-Reservation"
   .\simple_deploy.ps1
   ```
3. **Start the server:**
   ```powershell
   .\start_server.bat
   ```

### **Option 2: Background Service** (Production)

1. **Install as Windows Service:**
   ```powershell
   # Run as Administrator
   .\manage_service.ps1 install
   .\manage_service.ps1 start
   ```

2. **Your site will be available at:**
   - Local: `http://localhost:8080`
   - Network: `http://str.ptpsystem.com:8080`

## 📧 Configuration Required

### 1. **Google Calendar Setup**
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create project & enable Calendar API
- Download `client_secrets.json` to `secrets/` folder
- Share BayfrontLiving@gmail.com calendar with service account

### 2. **Email Configuration**
Edit `.env` file:
```env
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
ADMIN_EMAIL=admin@ptpsystem.com
```

### 3. **Domain Setup**
- Point `str.ptpsystem.com` DNS to your server IP
- Use Cloudflare for free SSL (recommended)

## 📋 How It Works

### **For Guests:**
1. Visit `str.ptpsystem.com:8080`
2. View available dates on calendar
3. Fill out booking request form
4. Receive email confirmation when approved

### **For You (Admin):**
1. Receive email when new booking request comes in
2. Click "APPROVE" or "REJECT" in email
3. System automatically:
   - Creates Google Calendar event
   - Sends confirmation to guest
   - Notifies your team members

### **Automatic Features:**
- Calendar stays synced with Google
- Email notifications to multiple people
- Booking conflict detection
- Mobile-friendly interface

## 🔒 SSL/HTTPS Setup

### **Cloudflare (Recommended - Free & Easy):**
1. Add `ptpsystem.com` to Cloudflare
2. Create DNS record: `str` → `A` → `Your-Server-IP`
3. Enable SSL in Cloudflare dashboard
4. Your site becomes: `https://str.ptpsystem.com`

## 🖥️ Server Management

### **Start/Stop Server:**
```powershell
# Manual start
.\start_server.bat

# Windows Service
.\manage_service.ps1 start
.\manage_service.ps1 stop
.\manage_service.ps1 restart
```

### **View Logs:**
- Check `logs/` folder for application logs
- Windows Event Viewer for service logs

### **Health Check:**
Visit: `http://localhost:8080/health`

## 🔥 Windows Firewall

Allow incoming connections:
```powershell
New-NetFirewallRule -DisplayName "Galveston Reservation" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow
```

## 📱 Testing the System

1. **Visit your site:** `http://localhost:8080`
2. **Submit test booking request**
3. **Check email for approval link**
4. **Click approve/reject**
5. **Verify Google Calendar event created**

## 🚨 Troubleshooting

### **Server won't start:**
- Check if Python virtual environment is activated
- Verify all packages installed: `pip list`
- Check `.env` file exists

### **No emails received:**
- Verify SMTP settings in `.env`
- Check spam folder
- Test with different email provider

### **Calendar not working:**
- Verify Google API credentials in `secrets/`
- Check calendar sharing permissions
- Monitor Google API quota

### **Can't access from network:**
- Check Windows Firewall settings
- Verify DNS configuration
- Test with IP address first

## 🎯 Next Steps

1. **Configure your `.env` file** with real credentials
2. **Set up Google Calendar API** credentials
3. **Test the booking workflow** end-to-end
4. **Configure SSL** with Cloudflare
5. **Set up monitoring** and backups

## 💡 Production Tips

- **Monitor the `/health` endpoint** for uptime
- **Backup SQLite database** regularly
- **Rotate logs** in `logs/` folder
- **Update packages** monthly
- **Test email delivery** weekly

## 📞 Support

If you need help:
1. Check logs in `logs/` directory
2. Run `python test_setup.py` to diagnose issues
3. Review this documentation
4. Check Google Calendar API quotas
5. Verify email SMTP settings

---

**🏖️ Your Galveston Reservation System is ready!**

The system provides everything you requested:
✅ Web calendar synced with BayfrontLiving@gmail.com  
✅ User booking request form  
✅ Email approval workflow  
✅ Automatic calendar event creation  
✅ Multi-recipient notifications  
✅ Simple Windows deployment  

Just configure the credentials and you're live!
