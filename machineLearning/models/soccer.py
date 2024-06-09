import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


class SoccerGoalPredictor:
    def __init__(self, data_filepath, recent_team_stats_filepath):
        self.data = pd.read_csv(data_filepath)
        self.recent_team_stats = pd.read_csv(recent_team_stats_filepath)
        self.model_home = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model_away = RandomForestRegressor(n_estimators=100, random_state=42)
        self.features = None
        self.train_models()

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

        # Train the models
        self.model_home.fit(X_train, y_train_home)
        self.model_away.fit(X_train, y_train_away)

        # Evaluate the models
        pred_home = self.model_home.predict(X_test)
        pred_away = self.model_away.predict(X_test)

        mae_home = mean_absolute_error(y_test_home, pred_home)
        mse_home = mean_squared_error(y_test_home, pred_home)
        mae_away = mean_absolute_error(y_test_away, pred_away)
        mse_away = mean_squared_error(y_test_away, pred_away)

        print(f"Home Goals - MAE: {mae_home}, MSE: {mse_home}")
        print(f"Away Goals - MAE: {mae_away}, MSE: {mse_away}")
        print(f"Feature columns used for training: {self.features.columns.tolist()}")

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

        # Ensure match_stats aligns with the features used in training
        print(f"Match stats columns before alignment: {match_stats.columns.tolist()}")
        print(f"Match stats values: {match_stats.values}")

        # Reorder columns to match training data
        match_stats = match_stats.reindex(columns=self.features.columns, fill_value=0)

        print(f"Match stats columns after alignment: {match_stats.columns.tolist()}")

        # Predict goals
        home_goals_pred = self.model_home.predict(match_stats)[0]
        away_goals_pred = self.model_away.predict(match_stats)[0]

        return home_goals_pred, away_goals_pred


# Usage
cleaned_data_filepath = r'C:\Users\arhic\PycharmProjects\ZephyrAlpha\machineLearning\cleanUtils\yup.csv'
recent_team_stats_filepath = r'C:\Users\arhic\PycharmProjects\ZephyrAlpha\machineLearning\cleanUtils\recent_stats.csv'
predictor = SoccerGoalPredictor(cleaned_data_filepath, recent_team_stats_filepath)

home_team = 'Orlando City'
away_team = 'Los Angeles FC'
home_goals, away_goals = predictor.predict_goals(home_team, away_team)

print(f"Predicted goals - Home Team ({home_team}): {home_goals}, Away Team ({away_team}): {away_goals}")
