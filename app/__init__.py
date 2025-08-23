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

# Import centralized configuration
from app.config import config

# Initialize extensions
db = SQLAlchemy()
mail = Mail()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration from centralized config
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Email configuration from centralized config
    app.config['MAIL_SERVER'] = config.MAIL_SERVER
    app.config['MAIL_PORT'] = config.MAIL_PORT
    app.config['MAIL_USE_TLS'] = config.MAIL_USE_TLS
    app.config['MAIL_USERNAME'] = config.MAIL_USERNAME
    app.config['MAIL_PASSWORD'] = config.MAIL_PASSWORD
    app.config['MAIL_DEFAULT_SENDER'] = config.MAIL_DEFAULT_SENDER
    
    # Debug mode
    app.config['DEBUG'] = config.FLASK_DEBUG
    
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
