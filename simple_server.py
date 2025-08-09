"""
Simple Flask app without SQLAlchemy for testing
"""
from flask import Flask, jsonify, render_template_string
import os

def create_simple_app():
    """Create a simple Flask app for testing"""
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Galveston Reservation System</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .hero { background: #007bff; color: white; padding: 40px; text-align: center; border-radius: 10px; }
        .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; }
        .warning { background: #fff3cd; color: #856404; }
        .button { display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="hero">
        <h1>🏖️ Galveston Reservation System</h1>
        <p>Your beachfront rental booking system</p>
    </div>
    
    <div class="section">
        <h2>System Status</h2>
        <div class="status success">✅ Web server is running</div>
        <div class="status warning">⚠️ Database setup required</div>
        <div class="status warning">⚠️ Google Calendar integration pending</div>
        <div class="status warning">⚠️ Email configuration pending</div>
    </div>
    
    <div class="section">
        <h2>Next Steps</h2>
        <ol>
            <li>Configure your <code>.env</code> file with:
                <ul>
                    <li>Google Calendar API credentials</li>
                    <li>SMTP email settings</li>
                    <li>Admin email addresses</li>
                </ul>
            </li>
            <li>Add Google API credentials to <code>secrets/</code> folder</li>
            <li>Test the booking system</li>
        </ol>
    </div>
    
    <div class="section">
        <h2>Quick Links</h2>
        <a href="/health" class="button">Health Check</a>
        <a href="/booking" class="button">Booking Form (Coming Soon)</a>
        <a href="/calendar" class="button">Calendar View (Coming Soon)</a>
    </div>
    
    <div class="section">
        <h2>Configuration</h2>
        <p><strong>Domain:</strong> str.ptpsystem.com</p>
        <p><strong>Port:</strong> {{ port }}</p>
        <p><strong>Environment:</strong> {{ env }}</p>
    </div>
</body>
</html>
        ''', port=os.getenv('PORT', '8080'), env=os.getenv('FLASK_ENV', 'development'))
    
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'service': 'Galveston Reservation System',
            'version': '1.0.0',
            'port': os.getenv('PORT', '8080'),
            'environment': os.getenv('FLASK_ENV', 'development')
        })
    
    @app.route('/booking')
    def booking():
        return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Booking - Galveston Rental</title>
    <style>body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }</style>
</head>
<body>
    <h1>🏖️ Booking Request</h1>
    <p>The full booking system will be available once the database and Google Calendar integration are configured.</p>
    <p><strong>Coming soon:</strong></p>
    <ul>
        <li>Interactive calendar</li>
        <li>Booking request form</li>
        <li>Email notifications</li>
        <li>Admin approval workflow</li>
    </ul>
    <a href="/">← Back to Home</a>
</body>
</html>
        ''')
    
    @app.route('/calendar')
    def calendar():
        return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Calendar - Galveston Rental</title>
    <style>body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }</style>
</head>
<body>
    <h1>📅 Availability Calendar</h1>
    <p>The calendar will show real-time availability once Google Calendar integration is configured.</p>
    <p><strong>Features:</strong></p>
    <ul>
        <li>Real-time availability from BayfrontLiving@gmail.com</li>
        <li>Interactive date selection</li>
        <li>Booking conflict detection</li>
        <li>Mobile-responsive design</li>
    </ul>
    <a href="/">← Back to Home</a>
</body>
</html>
        ''')
    
    return app

if __name__ == '__main__':
    app = create_simple_app()
    port = int(os.getenv('PORT', 8080))
    
    print("🏖️  GALVESTON RESERVATION SYSTEM (Simple Mode)")
    print("=" * 50)
    print(f"🌐 Local URL: http://localhost:{port}")
    print(f"🌐 Network URL: http://str.ptpsystem.com:{port}")
    print("📝 Note: This is a simplified version for testing")
    print("   Full features available after configuration")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=port, debug=True)
