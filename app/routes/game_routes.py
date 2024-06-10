from flask import Blueprint, render_template, jsonify
from app.utilities.data_fetching import get_live_game_data
from app.utilities.cache_utils import pull_all_games_cached
from app.utilities.bet_data_processing import get_organize_bet_data
from app.utilities.game_data import split_games_by_upcoming
from app.utilities.json_for_comparison import TeamComparison
from app.models.models import Message

game_bp = Blueprint('game', __name__)

@game_bp.route('/')
def index():
    games_list = pull_all_games_cached().to_dict(orient='records')
    all_games, upcoming_games, later_games = split_games_by_upcoming(games_list)
    unique_sports = {game['sport'] for game in games_list}
    return render_template('index.html', games=upcoming_games, later_games=later_games, sports=unique_sports)

@game_bp.route('/signup')
def signup():
    return "Signup Page - To be implemented"

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
    print(home_team, away_team, league)

    comparison_data = None
    try:
        print(home_team, away_team, league)
        comparison = TeamComparison(home_team, away_team, league)
        comparison_data = comparison.generate_json()
    except Exception as e:
        print(f"Error generating comparison data: {e}")

    print(comparison_data)

    messages = Message.query.filter_by(game_id=game_id).order_by(Message.timestamp.asc()).all()

    return render_template('game_page.html',
                           game=game_details,
                           live_data=live_data,
                           messages=messages,
                           betting_data=betting_data,
                           comparison_data=comparison_data)

