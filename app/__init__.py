from flask import Flask
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__,template_folder='templates')
    app.config.from_object('app.config.Config')

    bcrypt.init_app(app)

    # Import and register Blueprints
    from app.routes.main_routes import main_bp
    from app.routes.order_routes import order_bp
    from app.routes.auth_routes import auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(order_bp, url_prefix='/orders')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app
