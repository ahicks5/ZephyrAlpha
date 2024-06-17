from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, Flask
from flask_login import current_user, login_required, login_user, logout_user
from app.utilities.data_fetching import get_live_game_data
from app.utilities.cache_utils import pull_all_games_cached
from app.utilities.bet_data_processing import get_organize_bet_data
from app.utilities.game_data import split_games_by_upcoming
from app.utilities.json_for_comparison import TeamComparison
from app.models.models import Message, db, User
from app.utilities.soccerPrediction import predict_game_goals
import re
from pull_vsin.updateMLS import get_vsin_data
import json
from app.utilities.sport_league_mappings import team_mappings, sort_team_mappings

game_bp = Blueprint('game', __name__)

@game_bp.route('/')
def index():
    games_list = pull_all_games_cached().to_dict(orient='records')
    all_games, upcoming_games, later_games = split_games_by_upcoming(games_list)
    unique_sports = {game['sport'] for game in games_list}
    unique_sports = sorted(unique_sports)

    # Get the favorite teams for the current user
    favorite_teams = {}
    if current_user.is_authenticated:
        favorite_teams = json.loads(current_user.favorite_teams) if current_user.favorite_teams else {}

    # Find games that include favorite teams
    favorite_games = []
    for game in games_list:
        for league, teams in favorite_teams.items():
            if game['homeTeam'] in teams or game['awayTeam'] in teams:
                favorite_games.append(game)
                break

    username = session.get('username')
    return render_template('index.html', games=upcoming_games, later_games=later_games, sports=unique_sports, username=username, favorite_games=favorite_games, favorite_teams=favorite_teams)



@game_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.account_status == 'admin':
        return redirect(url_for('admin.admin_dashboard'))

    favorite_teams = json.loads(current_user.favorite_teams) if current_user.favorite_teams else {}
    subscription_status = current_user.account_status
    signup_time = current_user.signup_time
    sorted_team_mappings = sort_team_mappings(team_mappings)

    return render_template(
        'dashboard.html',
        username=current_user.username,
        favorite_teams=favorite_teams,
        subscription_status=subscription_status,
        signup_time=signup_time,
        team_mappings=sorted_team_mappings
    )

@game_bp.route('/update-favorites', methods=['POST'])
@login_required
def update_favorites():
    selected_teams = request.form.getlist('teams[]')
    league_key = request.form.get('league')

    favorite_teams = json.loads(current_user.favorite_teams) if current_user.favorite_teams else {}

    if league_key:
        if selected_teams:
            favorite_teams[league_key] = selected_teams
        else:
            if league_key in favorite_teams:
                del favorite_teams[league_key]
    else:
        # Remove any teams associated with the empty league key
        if "" in favorite_teams:
            del favorite_teams[""]

    current_user.favorite_teams = json.dumps(favorite_teams)
    db.session.commit()

    return jsonify({'message': 'Changes have been saved.'})

@game_bp.route('/clear-favorites', methods=['POST'])
@login_required
def clear_favorites():
    current_user.favorite_teams = json.dumps({})
    db.session.commit()
    return jsonify({'message': 'Favorites have been cleared.'})


@game_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')

        # Server-side validation
        if not re.match(r'^[a-zA-Z0-9]{5,15}$', username):
            error = "Username must be 5-15 characters long and contain only letters and numbers."
            return render_template('register.html', error=error)

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

        # Log the user in
        login_user(user)  # This line is essential to log the user in using Flask-Login

        return redirect(url_for('game.dashboard'))

    return render_template('login.html')


@game_bp.route('/logout')
def logout():
    logout_user()  # This ensures the user is logged out using Flask-Login
    session.clear()  # Clear all session data
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

    # Load predictions from CSV
    prediction_data = None
    try:
        prediction_data = predict_game_goals(home_team, away_team, league)
    except Exception as e:
        print(f"Error loading prediction data: {e}")

    vsin_data = None
    try:
        vsin_data = get_vsin_data(home_team, away_team, '/var/www/html/pull_vsin/mls_betting_splits.csv')
        vsin_data = json.dumps({str(k): v for k, v in vsin_data.items()})  # Ensure all keys are strings
    except Exception as e:
        print(f"Error loading VSIN data: {e}")

    messages = Message.query.filter_by(game_id=game_id).order_by(Message.timestamp.asc()).all()

    username = session.get('username')

    return render_template('game_page.html',
                           game=game_details,
                           live_data=live_data,
                           messages=messages,
                           betting_data=betting_data,
                           comparison_data=comparison_data,
                           prediction_data=prediction_data,
                           vsin_data=vsin_data,
                           username=username)

@game_bp.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@game_bp.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

