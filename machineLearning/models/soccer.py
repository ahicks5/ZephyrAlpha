import pandas as pd
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler
import joblib
import os
from machineLearning.soccerLeagueLinks import league_dict


class SoccerGoalPredictor:
    def __init__(self, friendly_league_name, year=None):
        self.league_info = league_dict[friendly_league_name]
        self.league_long_name = self.league_info['league_long_name'].replace(' ', '_').lower()
        self.year = year
        self.cleaned_data_filepath = self.generate_filepath('cleaned_data')
        self.recent_team_stats_filepath = self.generate_filepath('recent_stats')
        self.model_home_filepath = self.generate_filepath('model_home')
        self.model_away_filepath = self.generate_filepath('model_away')
        self.scaler_filepath = self.generate_filepath('scaler')

        self.data = pd.read_csv(self.cleaned_data_filepath)
        self.recent_team_stats = pd.read_csv(self.recent_team_stats_filepath)
        self.features = None
        self.model_home = None
        self.model_away = None
        self.scaler = StandardScaler()
        self.train_models()

    def generate_filepath(self, file_type):
        base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..', 'season_stats', self.league_long_name))

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
            raise ValueError(
                "Invalid file type. Use 'cleaned_data', 'recent_stats', 'model_home', 'model_away', or 'scaler'.")

    def train_models(self):
        # Prepare features and target variables
        self.features = self.data.drop(
            columns=['game_id', 'date', 'league', 'home_goals', 'away_goals', 'home_team', 'away_team'])
        target_home = self.data['home_goals']
        target_away = self.data['away_goals']

        # Split data into training and test sets
        X_train, X_test, y_train_home, y_test_home = train_test_split(self.features, target_home, test_size=0.2,
                                                                      random_state=42)
        X_train, X_test, y_train_away, y_test_away = train_test_split(self.features, target_away, test_size=0.2,
                                                                      random_state=42)

        # Standardize the data
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Hyperparameter tuning for RandomForest using RandomizedSearchCV
        rf_params = {
            'n_estimators': [50, 100, 200, 300],
            'max_depth': [10, 20, 30, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'bootstrap': [True, False]
        }
        n_iter_search = 50  # Number of parameter settings sampled

        print("Starting hyperparameter tuning for home goal model...")
        rf_home = RandomizedSearchCV(RandomForestRegressor(random_state=42), rf_params, cv=5, n_iter=n_iter_search,
                                     n_jobs=-1, verbose=2, random_state=42)
        rf_home.fit(X_train, y_train_home)
        print("Best parameters for home goal model:", rf_home.best_params_)

        print("Starting hyperparameter tuning for away goal model...")
        rf_away = RandomizedSearchCV(RandomForestRegressor(random_state=42), rf_params, cv=5, n_iter=n_iter_search,
                                     n_jobs=-1, verbose=2, random_state=42)
        rf_away.fit(X_train, y_train_away)
        print("Best parameters for away goal model:", rf_away.best_params_)

        # Store the best models
        self.model_home = rf_home.best_estimator_
        self.model_away = rf_away.best_estimator_

        # Save models and scaler
        self.save_model(self.model_home, self.model_home_filepath)
        self.save_model(self.model_away, self.model_away_filepath)
        self.save_model(self.scaler, self.scaler_filepath)

        # Evaluate models
        self.evaluate_models(X_test_scaled, y_test_home, y_test_away)

    def evaluate_models(self, X_test, y_test_home, y_test_away):
        pred_home = self.model_home.predict(X_test)
        pred_away = self.model_away.predict(X_test)
        mae_home = mean_absolute_error(y_test_home, pred_home)
        mse_home = mean_squared_error(y_test_home, pred_home)
        mae_away = mean_absolute_error(y_test_away, pred_away)
        mse_away = mean_squared_error(y_test_away, pred_away)
        print(f"RandomForest - Home Goals - MAE: {mae_home}, MSE: {mse_home}")
        print(f"RandomForest - Away Goals - MAE: {mae_away}, MSE: {mse_away}")

    def get_latest_team_stats(self, team, home=True):
        if home:
            team_stats = self.recent_team_stats[self.recent_team_stats['team'] == team].filter(
                regex='^home_|^home_allowed_')
        else:
            team_stats = self.recent_team_stats[self.recent_team_stats['team'] == team].filter(
                regex='^away_|^away_allowed_')
        if team_stats.empty:
            raise ValueError(f"No stats found for team: {team}")
        return team_stats

    def predict_goals(self, home_team, away_team):
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
            'RandomForest': (home_goals_pred, away_goals_pred)
        }

    def save_model(self, model, filepath):
        joblib.dump(model, filepath)

    def load_model(self, filepath):
        return joblib.load(filepath)


if __name__ == '__main__':
    # Usage
    friendly_league_name = 'Brazil Serie A'
    year = None

    # For historical data
    predictor_historical = SoccerGoalPredictor(friendly_league_name, year)

    # For current season data
    predictor_current = SoccerGoalPredictor(friendly_league_name)

    #teams = [
    #    ('Orlando City', 'Los Angeles FC'),
    #]

    #for home_team, away_team in teams:
    #    predictions = predictor_current.predict_goals(home_team, away_team)
    #    for model_name, (home_goals, away_goals) in predictions.items():
    #        print(
    #            f"{model_name} - Predicted goals - Home Team ({home_team}): {home_goals}, Away Team ({away_team}): {away_goals}")
