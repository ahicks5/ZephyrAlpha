import pandas as pd
import json
import os

class TeamComparison:
    def __init__(self, team1, team2, league):
        self.team1 = team1
        self.team2 = team2
        self.league = league
        #self.csv_file = os.path.join('..', '..', 'season_stats', 'soccer', league, f'team_stats_{league}.csv')
        self.csv_file = f'/var/www/html/season_stats/soccer/MLS/team_stats_{league}.csv'
        #self.csv_file = os.path.join('var', 'www', 'html', 'season_stats', 'soccer', league, f'team_stats_{league}.csv')
        self.team_stats = pd.read_csv(self.csv_file)
        self.league_averages = {}
        self.league_std_devs = {}
        self.teams = []

    def calculate_league_averages_and_std_devs(self):
        metrics = ['home_goals', 'away_goals', 'home_Shots on Target_value', 'away_Shots on Target_value',
                   'home_Passing Accuracy_value', 'away_Passing Accuracy_value', 'home_Saves_value', 'away_Saves_value',
                   'home_Tackles', 'away_Tackles']

        for metric in metrics:
            self.league_averages[metric] = self.team_stats[metric].astype(float).mean()
            self.league_std_devs[metric] = self.team_stats[metric].astype(float).std()

    @staticmethod
    def calculate_weighted_metric(metric):
        return (
            metric['season'] * 0.5 +
            metric['last10'] * 0.3 +
            metric['last5'] * 0.2
        )

    @staticmethod
    def normalize_metric(value, avg, std_dev):
        return (value - avg) / std_dev + 1

    def process_team_data(self):
        teams_of_interest = [self.team1, self.team2]
        filtered_team_stats = self.team_stats[self.team_stats['home_team'].isin(teams_of_interest) | self.team_stats['away_team'].isin(teams_of_interest)]

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
                'home_Saves_value': {
                    'season': team_data['home_Saves_value'].mean(),
                    'last10': team_data['home_Saves_value'].tail(10).mean(),
                    'last5': team_data['home_Saves_value'].tail(5).mean()
                },
                'away_Saves_value': {
                    'season': team_data['away_Saves_value'].mean(),
                    'last10': team_data['away_Saves_value'].tail(10).mean(),
                    'last5': team_data['away_Saves_value'].tail(5).mean()
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
                }
            }

            weighted_metrics = {metric: self.calculate_weighted_metric(values) for metric, values in metrics.items()}
            normalized_metrics = {metric: self.normalize_metric(value, self.league_averages[metric], self.league_std_devs[metric])
                                  for metric, value in weighted_metrics.items()}

            self.teams.append({
                'name': team,
                'metrics': normalized_metrics
            })

    def generate_json(self):
        self.calculate_league_averages_and_std_devs()
        self.process_team_data()

        # Construct the final JSON data structure
        json_data = {
            'leagueAverages': self.league_averages,
            'leagueStdDevs': self.league_std_devs,
            'teams': self.teams
        }

        # Return the JSON data as a string
        return json.dumps(json_data, indent=4)

# Example usage
if __name__ == '__main__':
    comparison = TeamComparison("Inter Miami", "Seattle Sounders FC", "MLS")
    json_result = comparison.generate_json()
    print(json_result)
