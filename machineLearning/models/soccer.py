import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler

class SoccerGoalPredictor:
    def __init__(self, data_filepath, recent_team_stats_filepath):
        self.data = pd.read_csv(data_filepath)
        self.recent_team_stats = pd.read_csv(recent_team_stats_filepath)
        self.features = None
        self.model_home = None
        self.model_away = None
        self.train_models()

    def train_models(self):
        # Prepare features and target variables
        self.features = self.data.drop(
            columns=['game_id', 'date', 'league', 'home_goals', 'away_goals', 'home_team', 'away_team'])
        target_home = self.data['home_goals']
        target_away = self.data['away_goals']

        # Split data into training and test sets
        X_train, X_test, y_train_home, y_test_home = train_test_split(self.features, target_home, test_size=0.2, random_state=42)
        X_train, X_test, y_train_away, y_test_away = train_test_split(self.features, target_away, test_size=0.2, random_state=42)

        # Standardize the data for models that require it
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Hyperparameter tuning for RandomForest
        rf_params = {
            'n_estimators': [50, 100, 200],
            'max_depth': [10, 20, None],
            'min_samples_split': [2, 5, 10]
        }
        rf_home = GridSearchCV(RandomForestRegressor(random_state=42), rf_params, cv=3, n_jobs=-1)
        rf_away = GridSearchCV(RandomForestRegressor(random_state=42), rf_params, cv=3, n_jobs=-1)
        rf_home.fit(X_train, y_train_home)
        rf_away.fit(X_train, y_train_away)

        # Train SVM
        svm_home = SVR(kernel='rbf')
        svm_away = SVR(kernel='rbf')
        svm_home.fit(X_train_scaled, y_train_home)
        svm_away.fit(X_train_scaled, y_train_away)

        # Store the best models
        self.model_home = {
            'RandomForest': rf_home.best_estimator_,
            'SVM': svm_home
        }
        self.model_away = {
            'RandomForest': rf_away.best_estimator_,
            'SVM': svm_away
        }

        # Evaluate models
        self.evaluate_models(X_test, y_test_home, y_test_away, X_test_scaled)

    def evaluate_models(self, X_test, y_test_home, y_test_away, X_test_scaled):
        for model_name, model in self.model_home.items():
            pred_home = model.predict(X_test_scaled if model_name != 'RandomForest' else X_test)
            pred_away = self.model_away[model_name].predict(X_test_scaled if model_name != 'RandomForest' else X_test)
            mae_home = mean_absolute_error(y_test_home, pred_home)
            mse_home = mean_squared_error(y_test_home, pred_home)
            mae_away = mean_absolute_error(y_test_away, pred_away)
            mse_away = mean_squared_error(y_test_away, pred_away)
            print(f"{model_name} - Home Goals - MAE: {mae_home}, MSE: {mse_home}")
            print(f"{model_name} - Away Goals - MAE: {mae_away}, MSE: {mse_away}")

    def get_latest_team_stats(self, team, home=True):
        if home:
            team_stats = self.recent_team_stats[self.recent_team_stats['team'] == team].filter(regex='^home_|^home_allowed_')
        else:
            team_stats = self.recent_team_stats[self.recent_team_stats['team'] == team].filter(regex='^away_|^away_allowed_')
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

        # Standardize the match stats for models that require it
        scaler = StandardScaler()
        match_stats_scaled = scaler.fit_transform(match_stats)

        predictions = {}
        for model_name, model in self.model_home.items():
            home_goals_pred = model.predict(match_stats_scaled if model_name != 'RandomForest' else match_stats)[0]
            away_goals_pred = self.model_away[model_name].predict(match_stats_scaled if model_name != 'RandomForest' else match_stats)[0]
            predictions[model_name] = (home_goals_pred, away_goals_pred)

        return predictions


# Usage
cleaned_data_filepath = r'C:\Users\arhic\PycharmProjects\ZephyrAlpha\machineLearning\cleanUtils\yup.csv'
recent_team_stats_filepath = r'C:\Users\arhic\PycharmProjects\ZephyrAlpha\machineLearning\cleanUtils\recent_stats.csv'
predictor = SoccerGoalPredictor(cleaned_data_filepath, recent_team_stats_filepath)

teams = [
    ('Colorado Rapids', 'Austin FC'),
    ('Houston Dynamo', 'Atlanta United'),
    ('Houston Dynamo', 'Austin FC')
]

for home_team, away_team in teams:
    predictions = predictor.predict_goals(home_team, away_team)
    for model_name, (home_goals, away_goals) in predictions.items():
        print(f"{model_name} - Predicted goals - Home Team ({home_team}): {home_goals}, Away Team ({away_team}): {away_goals}")
