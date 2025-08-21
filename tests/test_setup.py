"""
Test script to validate the Galveston Reservation System setup
"""
import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    try:
        print("🧪 Testing imports...")
        
        import flask
        print(f"✅ Flask {flask.__version__}")
        
        import waitress
        print(f"✅ Waitress installed")
        
        from dotenv import load_dotenv
        print("✅ python-dotenv")
        
        # Test app import
        from app import create_app, db
        print("✅ App modules")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_app_creation():
    """Test app creation and basic functionality"""
    try:
        print("\n🧪 Testing app creation...")
        
        from app import create_app
        app = create_app()
        
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            if response.status_code == 200:
                print("✅ Health endpoint working")
            else:
                print(f"⚠️  Health endpoint returned {response.status_code}")
                
            # Test main page
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Main page accessible")
            else:
                print(f"⚠️  Main page returned {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ App creation error: {e}")
        return False

def test_database():
    """Test database creation"""
    try:
        print("\n🧪 Testing database...")
        
        from app import create_app, db
        app = create_app()
        
        with app.app_context():
            db.create_all()
            print("✅ Database tables created")
            
            # Test basic database operations
            from app.models import BookingRequest
            print(f"✅ BookingRequest model accessible")
            
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    try:
        print("\n🧪 Testing environment...")
        
        env_file = ".env"
        if os.path.exists(env_file):
            print("✅ .env file exists")
        else:
            print("⚠️  .env file not found - you'll need to create it")
        
        secrets_dir = "secrets"
        if os.path.exists(secrets_dir):
            print("✅ secrets directory exists")
        else:
            print("⚠️  secrets directory not found - creating it")
            os.makedirs(secrets_dir, exist_ok=True)
        
        return True
    except Exception as e:
        print(f"❌ Environment error: {e}")
        return False

def main():
    """Run all tests"""
    print("🏖️  GALVESTON RESERVATION SYSTEM - SETUP TEST")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_environment,
        test_database,
        test_app_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! Your system is ready.")
        print("\n📋 Next steps:")
        print("1. Configure .env with your Google Calendar and email settings")
        print("2. Add Google API credentials to secrets/ folder") 
        print("3. Run: python server.py")
        print("4. Visit: http://localhost:8080")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
