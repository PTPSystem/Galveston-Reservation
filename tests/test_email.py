"""
Test Email Configuration
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from dotenv import load_dotenv
from flask import Flask
from flask_mail import Mail, Message

# Load environment variables
load_dotenv()

def test_email():
    """Test email configuration"""
    
    # Create a minimal Flask app for testing
    app = Flask(__name__)
    
    # Email configuration
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
    
    print("Email Configuration:")
    print(f"MAIL_SERVER: {app.config['MAIL_SERVER']}")
    print(f"MAIL_PORT: {app.config['MAIL_PORT']}")
    print(f"MAIL_USE_TLS: {app.config['MAIL_USE_TLS']}")
    print(f"MAIL_USERNAME: {app.config['MAIL_USERNAME']}")
    print(f"MAIL_DEFAULT_SENDER: {app.config['MAIL_DEFAULT_SENDER']}")
    print(f"Password set: {'Yes' if app.config['MAIL_PASSWORD'] else 'No'}")
    print()
    
    # Initialize mail
    mail = Mail(app)
    
    with app.app_context():
        try:
            # Create test message
            msg = Message(
                subject="🧪 Test Email - Galveston Booking System",
                recipients=[os.getenv('MAIL_USERNAME')],  # Send to self
                html="""
                <h2>📧 Email Configuration Test</h2>
                
                <p>This is a test email to verify that the Galveston Booking System email configuration is working correctly.</p>
                
                <div style="background-color: #d4edda; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 5px solid #28a745;">
                    <h3>✅ Test Results</h3>
                    <ul>
                        <li><strong>SMTP Server:</strong> Gmail (smtp.gmail.com)</li>
                        <li><strong>From Address:</strong> livingbayfront@gmail.com</li>
                        <li><strong>Encryption:</strong> TLS (Port 587)</li>
                        <li><strong>Status:</strong> Email sending is working!</li>
                    </ul>
                </div>
                
                <p>The booking system is now ready to send:</p>
                <ul>
                    <li>📋 Booking approval requests</li>
                    <li>✅ Guest confirmations</li>
                    <li>❌ Rejection notifications</li>
                    <li>📅 Team notifications</li>
                </ul>
                
                <p><small>Test sent from: Galveston Reservation System</small></p>
                """
            )
            
            print("Sending test email...")
            mail.send(msg)
            print("✅ Test email sent successfully!")
            print("Check your inbox at livingbayfront@gmail.com")
            return True
            
        except Exception as e:
            print(f"❌ Email test failed: {e}")
            print("\nTroubleshooting tips:")
            print("1. Make sure 'Less secure app access' is enabled on Gmail")
            print("2. Or use Gmail App Password instead of regular password")
            print("3. Check if 2-factor authentication is enabled")
            return False

if __name__ == "__main__":
    test_email()
