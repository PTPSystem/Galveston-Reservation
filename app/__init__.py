"""
Galveston Reservation System - Main Application Factory
"""
import os
from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
mail = Mail()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///galveston_reservations.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Email configuration
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
    
    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.booking import booking_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(booking_bp, url_prefix='/booking')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
