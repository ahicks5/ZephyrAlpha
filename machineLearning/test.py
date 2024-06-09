import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Load data
data = pd.read_csv(r'C:\Users\arhic\PycharmProjects\ZephyrAlpha\season_stats\major_league_soccer\team_stats_major_league_soccer.csv')

# Convert date column to datetime
data['date'] = pd.to_datetime(data['date'])

# Encode categorical variables
data = pd.get_dummies(data, columns=['home_team', 'away_team', 'league'], drop_first=True)

# Convert percentage values to numerical
if 'home_Possession_value' in data.columns:
    data['home_Possession_value'] = data['home_Possession_value'].str.rstrip('%').astype('float') / 100.0
if 'away_Possession_value' in data.columns:
    data['away_Possession_value'] = data['away_Possession_value'].str.rstrip('%').astype('float') / 100.0

# Drop rows with missing values
data = data.dropna()

# Drop non-numeric columns for correlation matrix
numeric_data = data.select_dtypes(include=[float, int])

# Descriptive statistics
print(data.describe())

# Correlation heatmap
plt.figure(figsize=(12, 8))
sns.heatmap(numeric_data.corr(), annot=True, fmt='.2f')
plt.show()

# Example of creating interaction features
if 'home_Possession_value' in data.columns and 'away_Possession_value' in data.columns:
    data['possession_diff'] = data['home_Possession_value'] - data['away_Possession_value']
if 'home_Passing Accuracy_value' in data.columns and 'away_Passing Accuracy_value' in data.columns:
    data['passing_accuracy_diff'] = data['home_Passing Accuracy_value'] - data['away_Passing Accuracy_value']

# Define features and target variables
features = data.drop(columns=['game_id', 'date', 'home_goals', 'away_goals'])
target_home = data['home_goals']
target_away = data['away_goals']

# Split data
X_train, X_test, y_train_home, y_test_home = train_test_split(features, target_home, test_size=0.2, random_state=42)
X_train, X_test, y_train_away, y_test_away = train_test_split(features, target_away, test_size=0.2, random_state=42)

# Train model for home goals
model_home = RandomForestRegressor(n_estimators=100, random_state=42)
model_home.fit(X_train, y_train_home)

# Train model for away goals
model_away = RandomForestRegressor(n_estimators=100, random_state=42)
model_away.fit(X_train, y_train_away)

# Predictions
pred_home = model_home.predict(X_test)
pred_away = model_away.predict(X_test)

# Evaluation
mae_home = mean_absolute_error(y_test_home, pred_home)
mse_home = mean_squared_error(y_test_home, pred_home)
mae_away = mean_absolute_error(y_test_away, pred_away)
mse_away = mean_squared_error(y_test_away, pred_away)

print(f"Home Goals - MAE: {mae_home}, MSE: {mse_home}")
print(f"Away Goals - MAE: {mae_away}, MSE: {mse_away}")
