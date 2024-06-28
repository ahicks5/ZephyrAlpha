from flask_socketio import SocketIO
from flask_caching import Cache

socketio = SocketIO(cors_allowed_origins="*")  # Allow CORS for all origins
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
