from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import sqlite3
import os
from app.utils.user_model import User
from datetime import timedelta

bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__,template_folder='templates')
    app.config.from_object('app.config.Config')

    bcrypt.init_app(app)
    secret_key = os.urandom(24)  # Generates a random 24-byte string
    app.config['SECRET_KEY'] = secret_key
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12)
    app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent XSS

    # Configure Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # User loader function for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        role, just_id = user_id.split(":")
        just_id = int(just_id)
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        if role == 'client' or role == 'admin':
            user_info = cursor.execute(f"SELECT client_id FROM clients WHERE client_id = '{just_id}'").fetchone()
            if user_info:
                conn.close()
                return User(user_info[0], role)
        elif role == 'driver':
            user_info = cursor.execute(f"SELECT driver_id FROM drivers WHERE driver_id = '{just_id}'").fetchone()
            if user_info:
                conn.close()
                return User(user_info[0], role)
        conn.close()
        return None


    # Import and register Blueprints
    from app.routes.client_routes import client_bp
    from app.routes.driver_routes import driver_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.auth_routes import auth_bp

    app.register_blueprint(client_bp, url_prefix='/')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(driver_bp, url_prefix='/driver')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app
