import pandas as pd
import os

# Function to determine the correct base path
def determine_base_path():
    paths = [
        "/var/www/html/season_stats/",
        "C:/Users/arhic/PycharmProjects/ZephyrAlpha/season_stats/"
    ]

    for path in paths:
        if os.path.exists(path):
            return path

    raise FileNotFoundError("No valid base path found. Please check the paths.")

# Set the base path dynamically
base_path = determine_base_path()

def predict_game_goals(stats_home_team, stats_away_team, stats_league_long_name):
    # Load predictions for the league
    predictions_df = load_predictions(stats_league_long_name)

    if predictions_df is not None:
        prediction_row = predictions_df[
            (predictions_df['home_team'] == stats_home_team) & (predictions_df['away_team'] == stats_away_team)]
        if not prediction_row.empty:
            prediction = prediction_row.to_dict('records')[0]
            # Round predictions to 2 decimal places
            prediction['home_goals_pred'] = round(prediction['home_goals_pred'], 2)
            prediction['away_goals_pred'] = round(prediction['away_goals_pred'], 2)
            return prediction
    return None

def load_predictions(stats_league_long_name):
    predictions_filepath = os.path.join(base_path, stats_league_long_name, f'current_predictions_{stats_league_long_name}.csv')
    if os.path.exists(predictions_filepath):
        return pd.read_csv(predictions_filepath)
    else:
        return None