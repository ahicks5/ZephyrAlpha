import pandas as pd
import json

# Load the CSV file
team_stats = pd.read_csv('team_stats_major_league_soccer.csv')

# Adjust the metric names to match the actual column names in the DataFrame
metrics = ['home_goals', 'away_goals', 'home_Shots on Target_value', 'away_Shots on Target_value',
           'home_Passing Accuracy_value', 'away_Passing Accuracy_value', 'home_Saves_value', 'away_Saves_value',
           'home_Tackles', 'away_Tackles']

# Calculate league averages and standard deviations
league_averages = {}
league_std_devs = {}

for metric in metrics:
    league_averages[metric] = team_stats[metric].astype(float).mean()
    league_std_devs[metric] = team_stats[metric].astype(float).std()

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

# Extract data for Inter Miami and Seattle Sounders
teams_of_interest = ["Inter Miami", "Seattle Sounders FC"]
filtered_team_stats = team_stats[team_stats['home_team'].isin(teams_of_interest) | team_stats['away_team'].isin(teams_of_interest)]

# Example teams data structure
teams = []

for team in teams_of_interest:
    home_team_data = filtered_team_stats[filtered_team_stats['home_team'] == team]
    away_team_data = filtered_team_stats[filtered_team_stats['away_team'] == team]

    team_data = pd.concat([home_team_data, away_team_data])

    metrics = {
        'home_goals': {
            'season': team_data['home_goals'].mean(),
            'last10': team_data['home_goals'].tail(10).mean(),
            'last5': team_data['home_goals'].tail(5).mean()
        },
        'away_goals': {
            'season': team_data['away_goals'].mean(),
            'last10': team_data['away_goals'].tail(10).mean(),
            'last5': team_data['away_goals'].tail(5).mean()
        },
        'home_Shots on Target_value': {
            'season': team_data['home_Shots on Target_value'].mean(),
            'last10': team_data['home_Shots on Target_value'].tail(10).mean(),
            'last5': team_data['home_Shots on Target_value'].tail(5).mean()
        },
        'away_Shots on Target_value': {
            'season': team_data['away_Shots on Target_value'].mean(),
            'last10': team_data['away_Shots on Target_value'].tail(10).mean(),
            'last5': team_data['away_Shots on Target_value'].tail(5).mean()
        },
        'home_Passing Accuracy_value': {
            'season': team_data['home_Passing Accuracy_value'].mean(),
            'last10': team_data['home_Passing Accuracy_value'].tail(10).mean(),
            'last5': team_data['home_Passing Accuracy_value'].tail(5).mean()
        },
        'away_Passing Accuracy_value': {
            'season': team_data['away_Passing Accuracy_value'].mean(),
            'last10': team_data['away_Passing Accuracy_value'].tail(10).mean(),
            'last5': team_data['away_Passing Accuracy_value'].tail(5).mean()
        },
        'home_Tackles': {
            'season': team_data['home_Tackles'].mean(),
            'last10': team_data['home_Tackles'].tail(10).mean(),
            'last5': team_data['home_Tackles'].tail(5).mean()
        },
        'away_Tackles': {
            'season': team_data['away_Tackles'].mean(),
            'last10': team_data['away_Tackles'].tail(10).mean(),
            'last5': team_data['away_Tackles'].tail(5).mean()
        },
        'home_Saves_value': {
            'season': team_data['home_Saves_value'].mean(),
            'last10': team_data['home_Saves_value'].tail(10).mean(),
            'last5': team_data['home_Saves_value'].tail(5).mean()
        },
        'away_Saves_value': {
            'season': team_data['away_Saves_value'].mean(),
            'last10': team_data['away_Saves_value'].tail(10).mean(),
            'last5': team_data['away_Saves_value'].tail(5).mean()
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
with open('team_comparison_data.json', 'w') as json_file:
    json.dump(json_data, json_file, indent=4)

print("JSON data has been successfully created and saved to 'team_comparison_data.json'.")
