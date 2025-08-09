"""
Setup script for Galveston Reservation System
Run this script to set up the application environment
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = [
        'secrets',
        'logs',
        'app/static/css',
        'app/static/js',
        'app/static/images',
        'app/templates/admin'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {directory}")

def create_env_file():
    """Create .env file if it doesn't exist"""
    if not os.path.exists('.env'):
        print("\n📝 Creating .env file...")
        with open('.env', 'w') as f:
            f.write("""# Galveston Reservation System Environment Configuration
# Copy from .env.example and customize with your values

# Flask Configuration
SECRET_KEY=change-this-secret-key-in-production
FLASK_ENV=development
DEBUG=True

# Domain Configuration
DOMAIN=str.ptpsystem.com
BASE_URL=https://str.ptpsystem.com

# Google Calendar Configuration
GOOGLE_PROJECT_ID=your-google-project-id
GOOGLE_CALENDAR_ID=bayfrontliving@gmail.com
GOOGLE_CREDENTIALS_PATH=./secrets/service-account.json
GOOGLE_CLIENT_SECRETS_PATH=./secrets/client_secrets.json

# Email Configuration (SMTP)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-smtp-username@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@ptpsystem.com

# Notification Email Addresses
ADMIN_EMAIL=admin@ptpsystem.com
NOTIFICATION_EMAILS=admin@ptpsystem.com,manager@ptpsystem.com

# Database Configuration
DATABASE_URL=sqlite:///galveston_reservations.db

# Security Configuration
APPROVAL_TOKEN_SECRET=change-this-token-secret
TOKEN_EXPIRATION_HOURS=48
""")
        print("✅ Created .env file - Please customize with your values")
    else:
        print("✅ .env file already exists")

def main():
    """Main setup function"""
    print("🏖️  Galveston Reservation System Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Create environment file
    create_env_file()
    
    # Check if virtual environment exists
    venv_path = Path('.venv')
    if not venv_path.exists():
        print("\n🐍 Creating virtual environment...")
        if not run_command(f"{sys.executable} -m venv .venv", "Creating virtual environment"):
            print("❌ Failed to create virtual environment")
            sys.exit(1)
    else:
        print("✅ Virtual environment already exists")
    
    # Determine activation script based on OS
    if os.name == 'nt':  # Windows
        activate_script = r".venv\Scripts\activate"
        pip_command = r".venv\Scripts\pip"
        python_command = r".venv\Scripts\python"
    else:  # Unix/Linux/macOS
        activate_script = ".venv/bin/activate"
        pip_command = ".venv/bin/pip"
        python_command = ".venv/bin/python"
    
    # Install requirements
    print("\n📦 Installing Python packages...")
    if not run_command(f"{pip_command} install --upgrade pip", "Upgrading pip"):
        print("⚠️  Pip upgrade failed, continuing anyway")
    
    if not run_command(f"{pip_command} install -r requirements.txt", "Installing requirements"):
        print("❌ Failed to install requirements")
        sys.exit(1)
    
    # Initialize database
    print("\n🗄️  Initializing database...")
    init_db_command = f"{python_command} -c \"from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('Database initialized')\""
    if not run_command(init_db_command, "Initializing database"):
        print("❌ Failed to initialize database")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Customize your .env file with actual values")
    print("2. Set up Google Calendar API credentials:")
    print("   - Go to Google Cloud Console")
    print("   - Enable Calendar API")
    print("   - Create OAuth 2.0 credentials")
    print("   - Download client_secrets.json to secrets/ folder")
    print("3. Configure email settings in .env")
    print("4. Run the application:")
    if os.name == 'nt':
        print("   > .venv\\Scripts\\activate")
    else:
        print("   $ source .venv/bin/activate")
    print("   $ python run.py")
    print("\n🌐 Application will be available at: http://localhost:5000")
    print("📧 Admin emails will be sent for booking requests")

if __name__ == "__main__":
    main()
