from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_socketio import SocketIO, emit, join_room
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from ARCHIVE.pullLiveGames import pull_all_games
from flask_caching import Cache
from time import sleep
from ARCHIVE.fetchLiveData import get_live_game_data, get_organize_bet_data
from werkzeug.security import generate_password_hash, check_password_hash


# Configure cache
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ahicks5:admin@localhost/chat_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.jinja_env.add_extension('jinja2.ext.do')

# Initialize cache with your app
cache.init_app(app)

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    print(f"User {request.sid} connected.")
    # Additional logging or initialization logic here

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    game_id = db.Column(db.Integer, nullable=False)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

def pull_all_games_cached():
    # Use cache to store the result of pull_all_games()
    games_df = cache.get('games_df')
    if games_df is None:
        games_df = pull_all_games()
        cache.set('games_df', games_df, timeout=60 * 15)  # Cache for 15 minutes
    return games_df

def commit_db_periodically():
    with app.app_context():
        while True:
            sleep(3)  # Wait for 3 seconds before each commit
            try:
                db.session.commit()
            except Exception as e:
                print(f"Error committing to DB: {e}")
                db.session.rollback()

@app.route('/')
def index():
    games_list = pull_all_games_cached().to_dict(orient='records')
    return render_template('index.html', games=games_list)

@app.route('/game/<int:game_id>')
def game_page(game_id):
    games_df = pull_all_games_cached()
    game_id_str = str(game_id)
    live_data = get_live_game_data(game_id)
    game_details = next((game for game in games_df.to_dict(orient='records') if str(game['id']) == game_id_str), None)

    if not game_details:
        return "Game not found", 404

    # Assuming you have a way to get the 'link' related to this game
    link = game_details.get('link')
    betting_data = get_organize_bet_data(link) if link else {}

    messages = Message.query.filter_by(game_id=game_id).order_by(Message.timestamp.asc()).all()

    return render_template('game_page.html', game=game_details, live_data=live_data, messages=messages, betting_data=betting_data)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if username or email already exists
        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()

        if user_exists:
            flash('Username or email already exists.')
            return redirect(url_for('register'))

        # Hash the password and create a new user
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Please login.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            flash('Login successful.')
            return redirect(url_for('index'))  # Or wherever you want to redirect users after login
        else:
            flash('Invalid username or password.')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))

@socketio.on('join_room')
def on_join(data):
    room = data['roomId']
    # Use request.sid for the session ID if you don't have a userId
    session_id = request.sid
    join_room(room)
    print(f"User {session_id} is trying to join room {room}.")
    emit('join_confirmation', {'room': room}, room=session_id)  # Notify the user's client
    print(f"User {session_id} has successfully joined room {room}.")


@socketio.on('send_message')
def handle_send_message(data):
    print("~~~~Send Message Data Received:~~~~", data)
    message = Message(text=data['message'], game_id=data['roomId'])
    db.session.add(message)
    db.session.commit()
    print("~~~~Send Message Data Uploaded:~~~~", data)

    # Emit the message to all clients in the room, including the sender
    emit('receive_message', {'message': data['message']}, room=data['roomId'], include_self=True)

@socketio.on('disconnect')
def handle_disconnect():
    print(f"User {request.sid} disconnected.")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created within an application context
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)