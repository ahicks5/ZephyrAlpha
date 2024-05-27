from flask import Blueprint, render_template
from app.utilities.data_fetching import get_live_game_data
from app.utilities.cache_utils import pull_all_games_cached  # Adjusted to use the cache internally
from app.utilities.bet_data_processing import get_organize_bet_data
from app.models.models import Message  # Ensure correct import path based on your app structure

game_bp = Blueprint('game', __name__)

@game_bp.route('/')
def index():
    # Directly call the function without passing cache
    games_list = pull_all_games_cached().to_dict(orient='records')
    return render_template('index.html', games=games_list)

@game_bp.route('/game/<int:game_id>')
def game_page(game_id):
    # Corrected call without passing cache
    games_df = pull_all_games_cached()
    game_id_str = str(game_id)
    live_data = get_live_game_data(game_id)
    game_details = next((game for game in games_df.to_dict(orient='records') if str(game['id']) == game_id_str), None)

    if not game_details:
        return "Game not found", 404

    link = game_details.get('link')
    betting_data = get_organize_bet_data(link) if link else {}

    messages = Message.query.filter_by(game_id=game_id).order_by(Message.timestamp.asc()).all()

    return render_template('game_page.html', game=game_details, live_data=live_data, messages=messages, betting_data=betting_data)
