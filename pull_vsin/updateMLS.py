import requests
from bs4 import BeautifulSoup
import csv
from pull_vsin.vsin_match import team_mapping
import pandas as pd
import os

# Function to determine the correct base path
def determine_base_path():
    paths = [
        "/var/www/html/pull_vsin/",
        "C:/Users/arhic/PycharmProjects/ZephyrAlpha//pull_vsin/"
    ]

    for path in paths:
        if os.path.exists(path):
            return path

    raise FileNotFoundError("No valid base path found. Please check the paths.")

# Set the base path dynamically
base_path = determine_base_path()


class WebScraper:
    def __init__(self, url):
        self.url = url

    def fetch_page_content(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()  # Raise an error for bad status codes
            return response.content
        except requests.RequestException as e:
            print(f"Error fetching the page: {e}")
            return None

    def scrape_table(self):
        page_content = self.fetch_page_content()
        if not page_content:
            return None

        try:
            soup = BeautifulSoup(page_content, 'html.parser')
            main_content = soup.find('main', id='main-content')
            if not main_content:
                print("Main content not found")
                return None

            table = main_content.find('table')
            if not table:
                print("Table not found")
                return None

            # Extracting the table rows without further splitting
            table_rows = table.find_all('tr')
            return table_rows
        except Exception as e:
            print(f"Error scraping the table: {e}")
            return None

    def parse_handle_bets(self, value):
        parts = value.split('%')
        team1_val = (parts[0].strip() + '%') if parts[0].strip() else '0%'
        team2_val = (parts[1].strip() + '%') if len(parts) > 1 and parts[1].strip() else '0%'
        return team1_val, team2_val

    def parse_moneyline(self, value):
        if len(value) == 0:
            return '--', '--'
        if value == '--':
            return '--', '--'
        parts = [value[:4].strip(), value[4:].strip()]
        return parts[0] if parts[0] else '--', parts[1] if parts[1] else '--'

    def parse_data(self, table_rows):
        parsed_data = []
        for row in table_rows:
            columns = row.find_all('td')
            row_data = [column.get_text().strip() for column in columns]
            if len(row_data) < 11:
                continue

            games_data = row_data
            for i in range(0, len(games_data), 11):
                if i + 11 > len(games_data):
                    break
                game = games_data[i:i + 11]
                teams = game[0].split('\xa0')
                if len(teams) != 2:
                    continue  # Skip if teams data is not as expected
                team1 = teams[0].strip()
                team2 = teams[1].strip()

                moneyline_team1, moneyline_team2 = self.parse_moneyline(game[1])
                handle_team1, handle_team2 = self.parse_handle_bets(game[2])
                bets_team1, bets_team2 = self.parse_handle_bets(game[3])

                total = game[4].strip()  # Placeholder, to be handled later
                handle_total_team1, handle_total_team2 = self.parse_handle_bets(game[5])
                bets_total_team1, bets_total_team2 = self.parse_handle_bets(game[6])

                spread = game[7].strip()  # Placeholder, to be handled later
                handle_spread_team1, handle_spread_team2 = self.parse_handle_bets(game[8])
                bets_spread_team1, bets_spread_team2 = self.parse_handle_bets(game[9])

                vsin_team1 = team_mapping.get(team1, "Unknown")
                vsin_team2 = team_mapping.get(team2, "Unknown")

                # Append parsed row for both teams in a single line
                parsed_data.append([team1, vsin_team1, team1, moneyline_team1, handle_team1, bets_team1,
                                    total, handle_total_team1, bets_total_team1, spread, handle_spread_team1, bets_spread_team1,
                                    team2, vsin_team2, team2, moneyline_team2, handle_team2, bets_team2, total,
                                    handle_total_team2, bets_total_team2, spread, handle_spread_team2, bets_spread_team2])

        return parsed_data

    def save_to_csv(self, data, filename):
        headers = ['VSIN Team 1', 'Clean Team 1', 'Team 1', 'Moneyline Team 1', 'Handle Team 1', 'Bets Team 1',
                   'Total', 'Handle Total Team 1', 'Bets Total Team 1', 'Spread', 'Handle Spread Team 1', 'Bets Spread Team 1',
                   'VSIN Team 2', 'Clean Team 2', 'Team 2', 'Moneyline Team 2', 'Handle Team 2', 'Bets Team 2', 'Total',
                   'Handle Total Team 2', 'Bets Total Team 2', 'Spread', 'Handle Spread Team 2', 'Bets Spread Team 2']
        try:
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                writer.writerows(data)
            print(f"Data saved to {filename}")
        except Exception as e:
            print(f"Error saving to CSV: {e}")


def get_vsin_data(home_team, away_team):
    csv_path = os.path.join(base_path, 'mls_betting_splits.csv')
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, encoding='ISO-8859-1')

    matching_row = df[(df['VSIN Team 1'] == away_team) & (df['VSIN Team 2'] == home_team)]
    if matching_row.empty:
        return None
    return matching_row.to_dict(orient='records')[0]


# Usage example
if __name__ == "__main__":
    #url = 'https://data.vsin.com/draftkings/betting-splits/?view=soc661'
    #scraper = WebScraper(url)
    #table_rows = scraper.scrape_table()

    #if table_rows:
    #    parsed_data = scraper.parse_data(table_rows)
    #    scraper.save_to_csv(parsed_data, f'mls_betting_splits.csv')
    import json

    try:
        vsin_data = get_vsin_data('NYCFC', 'Orlando City', 'mls_betting_splits.csv')
        vsin_data = json.dumps({str(k): v for k, v in vsin_data.items()})  # Ensure all keys are strings
        print(vsin_data)
    except Exception as e:
        print(f"Error loading VSIN data: {e}")

