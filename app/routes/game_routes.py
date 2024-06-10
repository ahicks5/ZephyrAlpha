from flask import Blueprint, render_template, jsonify
from app.utilities.data_fetching import get_live_game_data
from app.utilities.cache_utils import pull_all_games_cached
from app.utilities.bet_data_processing import get_organize_bet_data
from app.utilities.game_data import split_games_by_upcoming
from app.utilities.json_for_comparison import TeamComparison
from app.models.models import Message
from machineLearning.soccerLeagueLinks import league_dict
import os
import pandas as pd

game_bp = Blueprint('game', __name__)

def load_predictions(league_name):
    league_long_name = league_dict[league_name]['league_long_name'].replace(' ', '_').lower()
    predictions_filepath = os.path.join('..', '..', '..', 'season_stats', league_long_name, f'current_predictions_{league_long_name}.csv')
    if os.path.exists(predictions_filepath):
        return pd.read_csv(predictions_filepath)
    else:
        return None

@game_bp.route('/')
def index():
    games_list = pull_all_games_cached().to_dict(orient='records')
    all_games, upcoming_games, later_games = split_games_by_upcoming(games_list)
    unique_sports = {game['sport'] for game in games_list}
    return render_template('index.html', games=upcoming_games, later_games=later_games, sports=unique_sports)

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
        predictions_df = load_predictions(league)
        if predictions_df is not None:
            prediction_row = predictions_df[(predictions_df['home_team'] == home_team) & (predictions_df['away_team'] == away_team)]
            if not prediction_row.empty:
                prediction_data = prediction_row.to_dict('records')[0]
    except Exception as e:
        print(f"Error loading prediction data: {e}")

    messages = Message.query.filter_by(game_id=game_id).order_by(Message.timestamp.asc()).all()

    return render_template('game_page.html',
                           game=game_details,
                           live_data=live_data,
                           messages=messages,
                           betting_data=betting_data,
                           comparison_data=comparison_data,
                           prediction_data=prediction_data)
