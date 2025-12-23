from flask import Flask
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__,template_folder='templates')
    app.config.from_object('app.config.Config')

    bcrypt.init_app(app)

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
