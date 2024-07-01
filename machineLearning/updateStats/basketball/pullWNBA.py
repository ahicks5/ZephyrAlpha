import requests
from bs4 import BeautifulSoup, Comment
import pandas as pd
from datetime import datetime
import time
import os
from machineLearning.soccerLeagueLinks import league_dict

class MatchDataExtractor:
    def __init__(self, friendly_league_name, year=None):
        self.base_url = 'https://www.basketball-reference.com'
        self.schedule_url = self.get_season_link(friendly_league_name, year)
        self.urls = self.get_match_report_links()
        self.shots_data = pd.DataFrame()
        self.team_stats_data = pd.DataFrame()
        self.year = year

    @staticmethod
    def get_season_link(friendly_league_name, year=None):
        base_url = f'https://www.basketball-reference.com/{friendly_league_name}/years'
        if year:
            season_link = f"{base_url}/{year}_games.html"
        else:
            current_year = datetime.now().year
            season_link = f"{base_url}/{current_year}_games.html"
        return season_link

    def get_soup(self, url):
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        html_content = response.content.decode('utf-8')

        # Replace comment delimiters with empty strings
        html_content = html_content.replace('<!--', '').replace('-->', '')

        return BeautifulSoup(html_content, 'html.parser')

    def get_match_report_links(self):
        soup = self.get_soup(self.schedule_url)
        match_report_links = []
        for td in soup.find_all('td', {'data-stat': 'box_score_text'}):
            a_tag = td.find('a')
            if a_tag and 'href' in a_tag.attrs and a_tag.get_text(strip=True) == "Box Score":
                match_report_links.append(self.base_url + a_tag['href'])
        return match_report_links

    def extract_game_id_from_url(self, url):
        return url.split('/')[-1].split('.')[0]

    def extract_game_info(self, soup):
        # Extract date, teams, and score
        game_info = {}

        scorebox = soup.find('div', class_='scorebox')
        teams = scorebox.find_all('strong')
        scores = scorebox.find_all('div', class_='score')

        game_info['home_team'] = teams[1].get_text()
        game_info['away_team'] = teams[0].get_text()
        game_info['home_score'] = int(scores[1].get_text())
        game_info['away_score'] = int(scores[0].get_text())

        return game_info

    def extract_four_factors(self, soup):
        # Print all tables on the page
        tables = soup.find_all('table')
        for i, table in enumerate(tables):
            print(f"Table {i}:")
            print(table.prettify())

        # Extract Four Factors table data
        four_factors_data = []

        # Locate the table using the precise CSS selector path
        four_factors_table = soup.find('table', {'id': 'four-factors'})
        if not four_factors_table:
            print("Four Factors table not found using the precise CSS selector path.")
            return pd.DataFrame(four_factors_data)  # Return an empty DataFrame if table is not found
        print("Four Factors table found.")

        # Extract rows from the table
        print("Extracting rows from the Four Factors table")
        rows = four_factors_table.find('tbody').find_all('tr')

        for row in rows:
            factors = {}
            factors['team'] = row.find('th').get_text()
            factors.update({stat['data-stat']: stat.get_text() for stat in row.find_all('td')})
            four_factors_data.append(factors)

        return pd.DataFrame(four_factors_data)

    def extract_and_save_all_data(self):
        estimated_time = len(self.urls) * 4  # Estimate 4 seconds per item
        print(f"Estimated total processing time: {estimated_time // 60} minutes and {estimated_time % 60} seconds")

        for url in self.urls:
            try:
                soup = self.get_soup(url)
                game_info = self.extract_game_info(soup)
                four_factors_df = self.extract_four_factors(soup)

                print(game_info)
                print(four_factors_df)

                # You can store the extracted data as needed, e.g., concatenating to a DataFrame.
                self.team_stats_data = pd.concat([self.team_stats_data, four_factors_df], ignore_index=True)
                print(f"Successfully pulled data for {game_info['home_team']} vs {game_info['away_team']} on {game_info['date']}")
            except Exception as e:
                print(f'Error: {e}, skipping game and continuing.')

            time.sleep(5)  # Wait for 5 seconds before making the next request

        self.save_data_to_csv('wnba', self.year)

    def save_data_to_csv(self, league_name, year=None):
        league_name_tag = league_name.replace(' ', '_').lower()
        directory = os.path.join('..', '..', 'season_stats', league_name_tag)
        os.makedirs(directory, exist_ok=True)

        if year:
            team_stats_file_path = os.path.join(directory, f'team_stats_{league_name_tag}_{year}.csv')
        else:
            team_stats_file_path = os.path.join(directory, f'team_stats_{league_name_tag}.csv')

        self.team_stats_data.to_csv(team_stats_file_path, mode='a', index=False, header=not os.path.exists(team_stats_file_path))

if __name__ == '__main__':
    # Example usage
    extractor = MatchDataExtractor('wnba')  # For historical data
    url = extractor.urls[0]
    soup = extractor.get_soup(url)
    game_info = extractor.extract_game_info(soup)
    four_factors_df = extractor.extract_four_factors(soup)
    print(url)
    print(game_info)
    print(four_factors_df)
