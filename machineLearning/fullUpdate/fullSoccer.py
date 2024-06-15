from machineLearning.updateStats.soccer.pullSoccer import MatchDataExtractor
from machineLearning.cleanUtils.cleanSoccer import SoccerDataCleaner
from machineLearning.models.soccer import SoccerGoalPredictor

def fullUpdateSoccer(league_friendly_name, year=None):
    ## Pull stats and update season metrics
    extractor = MatchDataExtractor(league_friendly_name, year)  # For historical data
    extractor.extract_and_save_all_data()

    ## Clean up stats
    cleaner = SoccerDataCleaner(league_friendly_name, year)
    cleaner.clean_data()
    cleaned_data_filepath = cleaner.get_cleaned_data_filepath()
    recent_team_averages_filepath = cleaner.get_recent_team_averages_filepath()

    print("Cleaned data available at:", cleaned_data_filepath)
    print("Recent team averages available at:", recent_team_averages_filepath)

    cleaner_current = SoccerDataCleaner(league_friendly_name)
    cleaner_current.clean_data()
    cleaned_data_filepath_current = cleaner_current.get_cleaned_data_filepath()
    recent_team_averages_filepath_current = cleaner_current.get_recent_team_averages_filepath()

    print("Cleaned data available at:", cleaned_data_filepath_current)
    print("Recent team averages available at:", recent_team_averages_filepath_current)

    # generate final model and export
    predictor_model = SoccerGoalPredictor(league_friendly_name, year)


if __name__ == '__main__':
    league_friendly_name = 'Brazil Serie A'
    year = None
    fullUpdateSoccer(league_friendly_name, year)

