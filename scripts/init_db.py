"""
Database initialization script
"""
import os
import sys

# Set working directory
os.chdir(r'C:\Users\Administrator\Documents\Galveston-Reservation')

try:
    print("🔄 Initializing database...")
    
    # Import the app components
    from app import create_app, db
    
    # Create Flask app
    app = create_app()
    
    # Initialize database within app context
    with app.app_context():
        print("📊 Creating database tables...")
        db.create_all()
        
        # Verify tables were created
        from app.models import BookingRequest, CalendarEvent, SyncLog
        
        # Test database connection by counting records
        booking_count = BookingRequest.query.count()
        event_count = CalendarEvent.query.count()
        sync_count = SyncLog.query.count()
        
        print(f"✅ BookingRequest table created ({booking_count} records)")
        print(f"✅ CalendarEvent table created ({event_count} records)")  
        print(f"✅ SyncLog table created ({sync_count} records)")
        
        print("✅ Database initialization complete!")
        
        # Check if database file exists
        db_path = "galveston_reservations.db"
        if os.path.exists(db_path):
            size = os.path.getsize(db_path)
            print(f"✅ Database file created: {db_path} ({size} bytes)")
        else:
            print("⚠️  Database file not found - using in-memory database")
            
except Exception as e:
    print(f"❌ Database initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
    
print("\n🎉 Database is ready for the booking system!")
