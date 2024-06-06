import pandas as pd
import json

# Load the CSV files
shots_data = pd.read_csv('shots_data_combined_mls.csv')
team_stats = pd.read_csv('team_stats_combined_mls.csv')

# Define the league averages and standard deviations (example values, adjust as needed)
league_averages = {
    'goalsPerGame': 2.5,
    'shotsOnTargetPerGame': 5.5,
    'passingAccuracy': 80,
    'goalsConcededPerGame': 1.5,
    'tacklesPerGame': 20,
    'savesPerGame': 3
}

league_std_devs = {
    'goalsPerGame': 0.5,
    'shotsOnTargetPerGame': 1,
    'passingAccuracy': 5,
    'goalsConcededPerGame': 0.4,
    'tacklesPerGame': 5,
    'savesPerGame': 1
}

# Function to calculate weighted metric
def calculate_weighted_metric(metric):
    return (
        metric['season'] * 0.5 +
        metric['last10'] * 0.3 +
        metric['last5'] * 0.2
    )

# Function to normalize the metric value
def normalize_metric(value, avg, std_dev):
    return (value - avg) / std_dev + 1

# Example teams data structure
teams = []

# Process the team stats
for team in team_stats['Squad'].unique():
    team_data = team_stats[team_stats['Squad'] == team]
    metrics = {
        'goalsPerGame': {
            'season': team_data['Goals'].mean(),
            'last10': team_data['Goals'].tail(10).mean(),
            'last5': team_data['Goals'].tail(5).mean()
        },
        'shotsOnTargetPerGame': {
            'season': team_data['ShotsOnTarget'].mean(),
            'last10': team_data['ShotsOnTarget'].tail(10).mean(),
            'last5': team_data['ShotsOnTarget'].tail(5).mean()
        },
        'passingAccuracy': {
            'season': team_data['PassAccuracy'].mean(),
            'last10': team_data['PassAccuracy'].tail(10).mean(),
            'last5': team_data['PassAccuracy'].tail(5).mean()
        },
        'goalsConcededPerGame': {
            'season': team_data['GoalsConceded'].mean(),
            'last10': team_data['GoalsConceded'].tail(10).mean(),
            'last5': team_data['GoalsConceded'].tail(5).mean()
        },
        'tacklesPerGame': {
            'season': team_data['Tackles'].mean(),
            'last10': team_data['Tackles'].tail(10).mean(),
            'last5': team_data['Tackles'].tail(5).mean()
        },
        'savesPerGame': {
            'season': team_data['Saves'].mean(),
            'last10': team_data['Saves'].tail(10).mean(),
            'last5': team_data['Saves'].tail(5).mean()
        }
    }

    weighted_metrics = {metric: calculate_weighted_metric(values) for metric, values in metrics.items()}
    normalized_metrics = {metric: normalize_metric(value, league_averages[metric], league_std_devs[metric])
                          for metric, value in weighted_metrics.items()}

    teams.append({
        'name': team,
        'metrics': normalized_metrics
    })

# Construct the final JSON data structure
json_data = {
    'leagueAverages': league_averages,
    'leagueStdDevs': league_std_devs,
    'teams': teams
}

# Save the JSON data to a file
with open('league_data.json', 'w') as json_file:
    json.dump(json_data, json_file, indent=4)

print("JSON data has been successfully created and saved to 'league_data.json'.")
