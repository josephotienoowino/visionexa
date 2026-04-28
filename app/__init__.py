from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import os
import yaml

db = SQLAlchemy()
mail = Mail()

def _load_content(app):
    content_path = os.path.join(os.path.dirname(app.root_path), 'content.yaml')
    with open(content_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__)

    # Load configuration
    from config import config
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)

    # Import models before creating tables so metadata is registered
    from app import models

    # Ensure SQLite folder exists before creating the database file
    db_path = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if db_path.startswith('sqlite:///'):
        db_file = db_path.replace('sqlite:///', '')
        db_dir = os.path.dirname(db_file)
        if db_dir and not os.path.isdir(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    # Create database tables within app context
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"Database initialization error (non-fatal): {e}")

    # Load site content once and inject into every template context
    site_content = _load_content(app)

    @app.context_processor
    def inject_content():
        return site_content

    # Register blueprints
    from app.routes import main_bp, profile_bp, admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp)

    return app
