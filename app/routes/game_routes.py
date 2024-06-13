from flask import Flask, Blueprint, render_template, request, redirect, url_for, session
from app.utilities.data_fetching import get_live_game_data
from app.utilities.cache_utils import pull_all_games_cached
from app.utilities.bet_data_processing import get_organize_bet_data
from app.utilities.game_data import split_games_by_upcoming
from app.utilities.json_for_comparison import TeamComparison
from app.models.models import Message, db, User
from app.utilities.soccerPrediction import predict_game_goals

game_bp = Blueprint('game', __name__)

@game_bp.route('/')
def index():
    games_list = pull_all_games_cached().to_dict(orient='records')
    all_games, upcoming_games, later_games = split_games_by_upcoming(games_list)
    unique_sports = {game['sport'] for game in games_list}

    username = session.get('username')
    return render_template('index.html', games=upcoming_games, later_games=later_games, sports=unique_sports, username=username)

@game_bp.route('/dashboard')
def dashboard():
    username = session.get('username')
    if not username:
        return redirect(url_for('game.index'))
    return render_template('dashboard.html', username=username)

@game_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')

        if password != confirm_password:
            error = "Passwords do not match"
            return render_template('register.html', error=error)

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            error = "Username already exists"
            return render_template('register.html', error=error)

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            error = "Email already exists"
            return render_template('register.html', error=error)

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print(f"New user added: {username} with email {email}")
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return redirect(url_for('game.index'))

    return render_template('register.html')

@game_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            error = 'Invalid credentials'
            return render_template('login.html', error=error)

        # Set session variables
        session['user_id'] = user.id
        session['username'] = user.username

        return redirect(url_for('game.index'))

    return render_template('login.html')


@game_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('game.index'))


@game_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')

        if email:
            success_message = 'If this email is registered, you will receive a password reset link.'
            return render_template('forgot_password.html', success_message=success_message)

    return render_template('forgot_password.html')

@game_bp.route('/game/<int:game_id>')
def game_page(game_id):
    games_df = pull_all_games_cached()
    game_id_str = str(game_id)
    live_data = get_live_game_data(game_id)
    game_details = next((game for game in games_df.to_dict(orient='records') if str(game['id']) == game_id_str), None)

    if not game_details:
        return "Game not found", 404

    link = game_details.get('link')
    betting_data = get_organize_bet_data(link) if link else {}

    home_team = game_details['homeTeam']
    away_team = game_details['awayTeam']
    league = game_details['sport']

    comparison_data = None
    try:
        comparison = TeamComparison(home_team, away_team, league)
        comparison_data = comparison.generate_json()
    except Exception as e:
        print(f"Error generating comparison data: {e}")

    print(comparison_data)

    # Load predictions from CSV
    prediction_data = None
    try:
        prediction_data = predict_game_goals(home_team, away_team, league)
    except Exception as e:
        print(f"Error loading prediction data: {e}")

    messages = Message.query.filter_by(game_id=game_id).order_by(Message.timestamp.asc()).all()

    username = session.get('username')

    return render_template('game_page.html',
                           game=game_details,
                           live_data=live_data,
                           messages=messages,
                           betting_data=betting_data,
                           comparison_data=comparison_data,
                           prediction_data=prediction_data,
                           username=username)
