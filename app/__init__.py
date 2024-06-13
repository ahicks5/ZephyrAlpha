from flask import Flask
from flask_login import LoginManager
from .database import db  # Ensure this import matches the location of your db instance
from config import Config
from .extensions import cache, socketio
from .events import socket_events

# Import Blueprints
from .routes.admin_routes import admin_bp
from .routes.game_routes import game_bp

# Import the User model
from .models.models import User

# Initialize extensions
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions with the app instance
    db.init_app(app)
    socketio.init_app(app)
    cache.init_app(app)
    login_manager.init_app(app)

    # Configure LoginManager
    login_manager.login_view = 'game.login'

    # Register blueprints
    app.register_blueprint(game_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        # If you're using models here for something like `db.create_all()`, keep this import
        from .models import models
        # Ensure all your database tables are created
        db.create_all()

    return app

# User loader callback function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
