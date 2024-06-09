import json
import pandas as pd
import os
from app.utilities.sport_league_mappings import team_mappings, base_path

class TeamComparison:
    def __init__(self, team1, team2, league):
        # Find the correct league key
        league_key = None
        for key, value in team_mappings.items():
            if value['league_name'] == league:
                league_key = key
                break

        if not league_key:
            raise ValueError(f"League '{league}' not supported")

        # Map the teams using the league key
        self.team1 = team_mappings[league_key]['teams'].get(team1, team1)
        self.team2 = team_mappings[league_key]['teams'].get(team2, team2)
        self.league = league_key

        self.csv_file = os.path.join(base_path, self.league, f'team_stats_{self.league}.csv')
        self.team_stats = pd.read_csv(self.csv_file)
        self.league_averages = {}
        self.league_std_devs = {}
        self.teams = []

    def calculate_league_averages_and_std_devs(self):
        metrics = [
            'home_goals', 'away_goals', 'home_Shots on Target_value', 'away_Shots on Target_value',
            'home_Saves_value', 'away_Saves_value', 'home_Possession_value', 'away_Possession_value'
        ]

        for metric in metrics:
            if 'Possession' in metric:
                # Remove '%' and convert to float
                self.team_stats[metric] = self.team_stats[metric].str.rstrip('%').astype('float') / 100.0
            self.league_averages[metric] = self.team_stats[metric].mean()
            self.league_std_devs[metric] = self.team_stats[metric].std()

    def process_team_data(self):
        teams_of_interest = [self.team1, self.team2]
        filtered_team_stats = self.team_stats[self.team_stats['home_team'].isin(teams_of_interest) | self.team_stats['away_team'].isin(teams_of_interest)]

        for team in teams_of_interest:
            home_team_data = filtered_team_stats[filtered_team_stats['home_team'] == team]
            away_team_data = filtered_team_stats[filtered_team_stats['away_team'] == team]

            team_data = pd.concat([home_team_data, away_team_data])

            metrics = {
                'goals_scored': team_data.apply(lambda row: row['home_goals'] if row['home_team'] == team else row['away_goals'], axis=1).mean(),
                'goals_allowed': team_data.apply(lambda row: row['away_goals'] if row['home_team'] == team else row['home_goals'], axis=1).mean(),
                'shots_on_target': team_data.apply(lambda row: row['home_Shots on Target_value'] if row['home_team'] == team else row['away_Shots on Target_value'], axis=1).mean(),
                'saves': team_data.apply(lambda row: row['home_Saves_value'] if row['home_team'] == team else row['away_Saves_value'], axis=1).mean(),
                'possession': team_data.apply(lambda row: row['home_Possession_value'] if row['home_team'] == team else row['away_Possession_value'], axis=1).mean()
            }

            normalized_metrics = {
                'goals_scored': self.normalize_metric(metrics['goals_scored'], self.league_averages['home_goals'], self.league_std_devs['home_goals']),
                'goals_allowed': self.normalize_metric(metrics['goals_allowed'], self.league_averages['away_goals'], self.league_std_devs['away_goals']),
                'shots_on_target': self.normalize_metric(metrics['shots_on_target'], self.league_averages['home_Shots on Target_value'], self.league_std_devs['home_Shots on Target_value']),
                'saves': self.normalize_metric(metrics['saves'], self.league_averages['home_Saves_value'], self.league_std_devs['home_Saves_value']),
                'possession': self.normalize_metric(metrics['possession'], self.league_averages['home_Possession_value'], self.league_std_devs['home_Possession_value'])
            }

            self.teams.append({
                'name': team,
                'metrics': normalized_metrics
            })

    @staticmethod
    def calculate_weighted_metric(metric):
        return metric  # Update this if weighting is needed

    @staticmethod
    def normalize_metric(value, avg, std_dev):
        return (value - avg) / std_dev

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
    comparison = TeamComparison("Vasco da Gama", "São Paulo", "Brasileirão Série A")
    json_result = comparison.generate_json()
    print(json_result)
