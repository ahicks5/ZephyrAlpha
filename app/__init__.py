from flask import Flask
from .database import db  # Ensure this import matches the location of your db instance
from config import Config
from .extensions import cache, socketio
from .events import socket_events

# Import Blueprints
##from .routes.auth_routes import auth_bp
from .routes.game_routes import game_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions with the app instance
    db.init_app(app)
    socketio.init_app(app)
    cache.init_app(app)

    # Register blueprints
    ##app.register_blueprint(auth_bp, url_prefix='/auth')
    # Make sure to register game_bp only once
    app.register_blueprint(game_bp)

    with app.app_context():
        # If you're using models here for something like `db.create_all()`, keep this import
        from .models import models
        # Ensure all your database tables are created
        db.create_all()

    return app
