from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import sqlite3
import os

bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__,template_folder='templates')
    app.config.from_object('app.config.Config')

    bcrypt.init_app(app)
    secret_key = os.urandom(24)  # Generates a random 24-byte string
    app.config['SECRET_KEY'] = secret_key

    # Configure Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # User loader function for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        user_info = cursor.execute("SELECT * FROM clients WHERE client_id = user_id").fetchone()
        if user_info:
            return user_info
        user_info = cursor.execute("SELECT * FROM drivers WHERE driver_id = user_id").fetchone()
        if user_info:
            return user_info
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
