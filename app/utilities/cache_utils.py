from app.extensions import cache  # Adjust the import path based on your project structure
from .game_data import pull_all_games

def pull_all_games_cached():
    # Use cache to store the result of pull_all_games()
    games_df = cache.get('games_df')
    if games_df is None:
        games_df = pull_all_games()
        cache.set('games_df', games_df, timeout=60 * 15)  # Cache for 15 minutes
    return games_df
