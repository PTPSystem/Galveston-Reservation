@echo off
echo 🚀 Starting Galveston Reservation System (Production)
echo.

REM Check if we're in the right directory
if not exist "app" (
    echo ❌ Error: Not in the correct directory. Please run from the project root.
    echo Expected: C:\Users\Administrator\Documents\Galveston-Reservation
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo ✅ Virtual environment activated
) else (
    echo ⚠️  Virtual environment not found. Please run: python setup.py
    pause
    exit /b 1
)

echo.

REM Initialize database if needed
echo 🗄️  Checking database...
if not exist "galveston_reservations.db" (
    echo 📋 Database not found. Creating...
    python init_db.py
    echo ✅ Database created
) else (
    echo ✅ Database exists
)

echo.

REM Show server info
echo 🌐 Starting production server for Cloudflare...
echo ┌─────────────────────────────────────────────────┐
echo │         Galveston Reservation System            │
echo ├─────────────────────────────────────────────────┤
echo │  Local Server:      http://localhost:8080       │
echo │  Public URL:        https://str.ptpsystem.com   │
echo │  Admin Interface:   /admin                      │
echo │  API Endpoint:      /api                        │
echo ├─────────────────────────────────────────────────┤
echo │  🔒 SSL/Security: Handled by Cloudflare         │
echo │  📧 Email Setup:  Configure in .env file       │
echo │  📅 Calendar API: Configure Google credentials  │
echo └─────────────────────────────────────────────────┘
echo.

REM Start the production server
echo ⏳ Starting Waitress WSGI server on port 8080...
echo Press Ctrl+C to stop the server
echo.

python simple_server.py

echo.
echo 🛑 Server stopped
echo.
pause
