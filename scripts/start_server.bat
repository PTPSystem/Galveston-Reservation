@echo off
echo ====================================
echo  Galveston Reservation System
echo ====================================

cd /d "C:\Users\Administrator\Documents\Galveston-Reservation"

echo Activating Python environment...
call .venv\Scripts\activate

echo.
echo Starting server...
echo Local URL: http://localhost:8080
echo Network URL: http://str.ptpsystem.com:8080
echo.
echo Press Ctrl+C to stop the server
echo.

python server.py

echo.
echo Server stopped.
pause
