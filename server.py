from waitress import serve
from app import create_app
import os
from datetime import datetime

def main():
    """Main server startup function"""
    app = create_app()
    
    # Configuration
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8080))
    threads = int(os.getenv('THREADS', 4))
    
    # Display startup information
    print("=" * 60)
    print("🏖️  GALVESTON RESERVATION SYSTEM")
    print("=" * 60)
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Local URL: http://localhost:{port}")
    print(f"🌐 Network URL: http://str.ptpsystem.com:{port}")
    print(f"📧 Admin Email: {os.getenv('ADMIN_EMAIL', 'admin@ptpsystem.com')}")
    print(f"📅 Calendar: {os.getenv('GOOGLE_CALENDAR_ID', 'bayfrontliving@gmail.com')}")
    print(f"🔧 Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"🧵 Threads: {threads}")
    print("=" * 60)
    print("📋 Available Endpoints:")
    print("   📱 Main Site: http://localhost:8080/")
    print("   📅 Calendar: http://localhost:8080/calendar")
    print("   📝 Booking: http://localhost:8080/booking/request")
    print("   🔧 Admin: http://localhost:8080/admin/dashboard")
    print("   ❤️  Health: http://localhost:8080/health")
    print("=" * 60)
    print("⏹️  Press Ctrl+C to stop the server")
    print("")
    
    try:
        # Start the Waitress WSGI server
        serve(
            app, 
            host=host, 
            port=port, 
            threads=threads,
            connection_limit=100,
            cleanup_interval=30,
            channel_timeout=120
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        raise

if __name__ == '__main__':
    main()
