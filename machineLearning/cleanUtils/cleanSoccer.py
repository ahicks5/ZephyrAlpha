import pandas as pd
import os
from machineLearning.soccerLeagueLinks import league_dict

class SoccerDataCleaner:
    def __init__(self, friendly_league_name, year=None):
        self.input_filepath = self.generate_filepath(friendly_league_name, year, 'input')
        self.output_filepath = self.generate_filepath(friendly_league_name, year, 'output')
        self.recent_stats_filepath = self.generate_filepath(friendly_league_name, year, 'recent_stats')
        self.columns_to_aggregate = [
            'Possession_value', 'Passing Accuracy_value', 'Passing Accuracy_attempts',
            'Shots on Target_value', 'Saves_value', 'xg', 'Fouls', 'Corners',
            'Crosses', 'Touches', 'Tackles', 'Interceptions', 'Aerials Won',
            'Clearances', 'Offsides', 'Goal Kicks', 'Throw Ins', 'Long Balls'
        ]

    @staticmethod
    def generate_filepath(friendly_league_name, year, file_type):
        league_long_name = league_dict[friendly_league_name]['league_long_name'].replace(' ', '_').lower()
        base_dir = os.path.join('..', '..', 'season_stats', league_long_name)

        if file_type == 'input':
            if year:
                return os.path.join(base_dir, f'team_stats_{league_long_name}_{year}.csv')
            else:
                return os.path.join(base_dir, f'team_stats_{league_long_name}.csv')
        elif file_type == 'output':
            if year:
                return os.path.join(base_dir, f'cleaned_data_{league_long_name}_{year}.csv')
            else:
                return os.path.join(base_dir, f'cleaned_data_{league_long_name}.csv')
        elif file_type == 'recent_stats':
            return os.path.join(base_dir, f'recent_stats_{league_long_name}.csv')
        else:
            raise ValueError("Invalid file type. Use 'input', 'output', or 'recent_stats'.")

    def load_and_preprocess_data(self):
        # Load the data
        self.data = pd.read_csv(self.input_filepath)

        # Convert percentage values to numerical
        self.data['home_Possession_value'] = self.data['home_Possession_value'].str.rstrip('%').astype('float') / 100.0
        self.data['away_Possession_value'] = self.data['away_Possession_value'].str.rstrip('%').astype('float') / 100.0

        # Convert date column to datetime
        self.data['date'] = pd.to_datetime(self.data['date'])

        # Sort the data by date
        self.data = self.data.sort_values(by='date')

    def calculate_aggregated_statistics(self):
        # Initialize a list to store the rows of the final dataframe
        final_rows = []

        # Iterate through each game
        for i, row in self.data.iterrows():
            # Get the date of the current game
            current_date = row['date']

            # Filter the data to get only past games
            past_games = self.data[self.data['date'] < current_date]

            # Skip if there are not enough past games for either team
            home_team_past_games = past_games[past_games['home_team'] == row['home_team']]
            away_team_past_games = past_games[past_games['away_team'] == row['away_team']]

            if len(home_team_past_games) < 3 or len(away_team_past_games) < 3:
                continue

            # Aggregate past statistics for the home team
            home_aggregated = home_team_past_games.groupby('home_team')[['home_' + col for col in self.columns_to_aggregate]].mean().reset_index()
            home_aggregated.columns = ['team'] + ['home_' + col for col in self.columns_to_aggregate]

            # Aggregate past statistics for the away team
            away_aggregated = away_team_past_games.groupby('away_team')[['away_' + col for col in self.columns_to_aggregate]].mean().reset_index()
            away_aggregated.columns = ['team'] + ['away_' + col for col in self.columns_to_aggregate]

            # Calculate allowed statistics (what teams allow their opponents to achieve)
            for col in self.columns_to_aggregate:
                home_team_past_games['home_Allowed ' + col] = home_team_past_games['away_' + col]
                away_team_past_games['away_Allowed ' + col] = away_team_past_games['home_' + col]

            # Aggregate allowed statistics for home and away teams
            home_allowed_aggregated = home_team_past_games.groupby('home_team')[[col for col in home_team_past_games.columns if 'home_Allowed' in col]].mean().reset_index()
            home_allowed_aggregated.columns = ['team'] + ['home_allowed_' + col.split('home_Allowed ')[1] for col in home_allowed_aggregated.columns if 'home_Allowed' in col]

            away_allowed_aggregated = away_team_past_games.groupby('away_team')[[col for col in away_team_past_games.columns if 'away_Allowed' in col]].mean().reset_index()
            away_allowed_aggregated.columns = ['team'] + ['away_allowed_' + col.split('away_Allowed ')[1] for col in away_allowed_aggregated.columns if 'away_Allowed' in col]

            # Merge allowed statistics
            home_full_stats = pd.merge(home_aggregated, home_allowed_aggregated, on='team')
            away_full_stats = pd.merge(away_aggregated, away_allowed_aggregated, on='team')

            # Add the current game row with the aggregated statistics
            combined_stats = row[['game_id', 'date', 'home_team', 'away_team', 'league']].to_dict()
            combined_stats.update(home_full_stats.set_index('team').to_dict('index')[row['home_team']])
            combined_stats.update(away_full_stats.set_index('team').to_dict('index')[row['away_team']])
            combined_stats['home_goals'] = row['home_goals']
            combined_stats['away_goals'] = row['away_goals']

            final_rows.append(combined_stats)

        # Create the final dataframe
        self.final_data = pd.DataFrame(final_rows)

    def save_cleaned_data(self):
        # Save the cleaned data to a CSV file
        self.final_data.to_csv(self.output_filepath, index=False)
        print("Cleaned data saved successfully to", self.output_filepath)

    def save_recent_team_averages(self):
        # Aggregate the home and away statistics
        home_aggregated = self.data.groupby('home_team')[['home_' + col for col in self.columns_to_aggregate]].mean().reset_index()
        home_aggregated.columns = ['team'] + ['home_' + col for col in self.columns_to_aggregate]

        away_aggregated = self.data.groupby('away_team')[['away_' + col for col in self.columns_to_aggregate]].mean().reset_index()
        away_aggregated.columns = ['team'] + ['away_' + col for col in self.columns_to_aggregate]

        # Calculate allowed statistics (what teams allow their opponents to achieve)
        for col in self.columns_to_aggregate:
            self.data['home_Allowed ' + col] = self.data['away_' + col]
            self.data['away_Allowed ' + col] = self.data['home_' + col]

        # Aggregate allowed statistics for home and away teams
        home_allowed_aggregated = self.data.groupby('home_team')[[col for col in self.data.columns if 'home_Allowed' in col]].mean().reset_index()
        home_allowed_aggregated.columns = ['team'] + ['home_allowed_' + col.split('home_Allowed ')[1] for col in home_allowed_aggregated.columns if 'home_Allowed' in col]

        away_allowed_aggregated = self.data.groupby('away_team')[[col for col in self.data.columns if 'away_Allowed' in col]].mean().reset_index()
        away_allowed_aggregated.columns = ['team'] + ['away_allowed_' + col.split('away_Allowed ')[1] for col in away_allowed_aggregated.columns if 'away_Allowed' in col]

        # Merge all statistics for each team
        full_stats = pd.merge(home_aggregated, home_allowed_aggregated, on='team', how='outer')
        full_stats = pd.merge(full_stats, away_aggregated, on='team', how='outer')
        full_stats = pd.merge(full_stats, away_allowed_aggregated, on='team', how='outer')

        # Save the most recent statistics to a CSV file
        full_stats.to_csv(self.recent_stats_filepath, index=False)
        print("Most recent team averages saved successfully to", self.recent_stats_filepath)

    def get_cleaned_data_filepath(self):
        return self.output_filepath

    def get_recent_team_averages_filepath(self):
        return self.recent_stats_filepath

    def clean_data(self):
        self.load_and_preprocess_data()
        self.calculate_aggregated_statistics()
        self.save_cleaned_data()
        self.save_recent_team_averages()

if __name__ == '__main__':
    # Usage
    friendly_league_name = 'Brazil Serie A'
    year = None
    cleaner = SoccerDataCleaner(friendly_league_name, year)
    cleaner.clean_data()
    cleaned_data_filepath = cleaner.get_cleaned_data_filepath()
    recent_team_averages_filepath = cleaner.get_recent_team_averages_filepath()

    print("Cleaned data available at:", cleaned_data_filepath)
    print("Recent team averages available at:", recent_team_averages_filepath)

    cleaner_current = SoccerDataCleaner(friendly_league_name)
    cleaner_current.clean_data()
    cleaned_data_filepath_current = cleaner_current.get_cleaned_data_filepath()
    recent_team_averages_filepath_current = cleaner_current.get_recent_team_averages_filepath()

    print("Cleaned data available at:", cleaned_data_filepath_current)
    print("Recent team averages available at:", recent_team_averages_filepath_current)
