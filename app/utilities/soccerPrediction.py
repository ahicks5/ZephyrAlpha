import pandas as pd
import os
from app.utilities.sport_league_mappings import team_mappings, base_path
from machineLearning.soccerLeagueLinks import league_dict
import joblib

class SoccerGoalPredictor:
    def __init__(self, friendly_league_name, year=None):
        self.league_info = team_mappings[friendly_league_name]
        self.league_long_name = self.league_info['league_name'].replace(' ', '_').lower()
        self.year = year
        self.cleaned_data_filepath = self.generate_filepath('cleaned_data')
        self.recent_team_stats_filepath = self.generate_filepath('recent_stats')
        self.model_home_filepath = self.generate_filepath('model_home')
        self.model_away_filepath = self.generate_filepath('model_away')
        self.scaler_filepath = self.generate_filepath('scaler')

        self.features = None
        self.model_home = self.load_model(self.model_home_filepath)
        self.model_away = self.load_model(self.model_away_filepath)
        self.scaler = self.load_model(self.scaler_filepath)
        self.recent_team_stats = pd.read_csv(self.recent_team_stats_filepath)
        if self.cleaned_data_filepath:
            self.data = pd.read_csv(self.cleaned_data_filepath)
            self.features = self.data.drop(
                columns=['game_id', 'date', 'league', 'home_goals', 'away_goals', 'home_team', 'away_team'])

    def generate_filepath(self, file_type):
        base_dir = os.path.abspath(os.path.join(base_path, self.league_long_name))

        if file_type == 'cleaned_data':
            if self.year:
                return os.path.join(base_dir, f'cleaned_data_{self.league_long_name}_{self.year}.csv')
            else:
                return os.path.join(base_dir, f'cleaned_data_{self.league_long_name}.csv')
        elif file_type == 'recent_stats':
            return os.path.join(base_dir, f'recent_stats_{self.league_long_name}.csv')
        elif file_type == 'model_home':
            return os.path.join(base_dir, f'{self.league_long_name}_home_model.pkl')
        elif file_type == 'model_away':
            return os.path.join(base_dir, f'{self.league_long_name}_away_model.pkl')
        elif file_type == 'scaler':
            return os.path.join(base_dir, f'{self.league_long_name}_scaler.pkl')
        else:
            raise ValueError("Invalid file type. Use 'cleaned_data', 'recent_stats', 'model_home', 'model_away', or 'scaler'.")

    def get_team_name(self, team_name):
        for league_key, league_value in team_mappings.items():
            if team_name in league_value['teams']:
                return league_value['teams'][team_name]
        raise ValueError(f"Team '{team_name}' not found in team mappings.")

    def get_latest_team_stats(self, team, home=True):
        team = self.get_team_name(team)
        if home:
            team_stats = self.recent_team_stats[self.recent_team_stats['team'] == team].filter(regex='^home_|^home_allowed_')
        else:
            team_stats = self.recent_team_stats[self.recent_team_stats['team'] == team].filter(regex='^away_|^away_allowed_')
        if team_stats.empty:
            raise ValueError(f"No stats found for team: {team}")
        return team_stats

    def predict_goals(self, home_team, away_team):
        home_team = self.get_team_name(home_team)
        away_team = self.get_team_name(away_team)

        # Get the latest stats for the given teams
        home_stats = self.get_latest_team_stats(home_team, home=True).iloc[0]
        away_stats = self.get_latest_team_stats(away_team, home=False).iloc[0]

        # Combine stats into a single row without duplication
        match_stats = pd.concat([home_stats, away_stats]).to_frame().T

        # Reorder columns to match training data
        match_stats = match_stats.reindex(columns=self.features.columns, fill_value=0)

        # Standardize the match stats
        match_stats_scaled = self.scaler.transform(match_stats)

        home_goals_pred = self.model_home.predict(match_stats_scaled)[0]
        away_goals_pred = self.model_away.predict(match_stats_scaled)[0]

        return {
            'home_goals_pred': home_goals_pred,
            'away_goals_pred': away_goals_pred
        }

    def save_model(self, model, filepath):
        joblib.dump(model, filepath)

    def load_model(self, filepath):
        return joblib.load(filepath)

def generate_predictions_for_all_teams(league_name):
    predictor = SoccerGoalPredictor(league_name)
    all_teams = team_mappings[league_name]['teams'].keys()
    predictions = []

    for home_team in all_teams:
        for away_team in all_teams:
            if home_team != away_team:
                prediction = predictor.predict_goals(home_team, away_team)
                predictions.append({
                    'home_team': home_team,
                    'away_team': away_team,
                    'home_goals_pred': prediction['home_goals_pred'],
                    'away_goals_pred': prediction['away_goals_pred']
                })

    league_long_name = team_mappings[league_name]['league_name'].replace(' ', '_').lower()
    predictions_df = pd.DataFrame(predictions)
    predictions_filepath = os.path.join(base_path, league_long_name, f'current_predictions_{league_long_name}.csv')
    predictions_df.to_csv(predictions_filepath, index=False)


def predict_game_goals(home_team, away_team, league):
    # Load predictions for the league
    predictions_df = load_predictions(league)

    # Find the correct league key
    league_key = None
    for key, value in team_mappings.items():
        if value['league_name'] == league:
            league_key = key
            break

    if not league_key:
        raise ValueError(f"League '{league}' not supported")

    # Map the teams using the league key
    home_team = team_mappings[league_key]['teams'].get(home_team, home_team)
    away_team = team_mappings[league_key]['teams'].get(away_team, away_team)

    if predictions_df is not None:
        prediction_row = predictions_df[
            (predictions_df['home_team'] == home_team) & (predictions_df['away_team'] == away_team)]
        if not prediction_row.empty:
            prediction = prediction_row.to_dict('records')[0]
            # Round predictions to 2 decimal places
            prediction['home_goals_pred'] = round(prediction['home_goals_pred'], 2)
            prediction['away_goals_pred'] = round(prediction['away_goals_pred'], 2)
            return prediction
    return None


def load_predictions(league_name):
    league_long_name = league_dict[league_name]['league_long_name'].replace(' ', '_').lower()
    predictions_filepath = os.path.join(base_path, league_long_name, f'current_predictions_{league_long_name}.csv')
    if os.path.exists(predictions_filepath):
        return pd.read_csv(predictions_filepath)
    else:
        return None

if __name__ == '__main__':
    print(predict_game_goals('Seattle Sounders', 'Minnesota United', 'MLS'))
