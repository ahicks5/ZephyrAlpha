import requests
from bs4 import BeautifulSoup
import pandas as pd


class MatchDataExtractor:
    def __init__(self, url):
        self.url = url
        self.soup = self.get_soup()
        self.shots_df = pd.DataFrame()
        self.team_stats_df = pd.DataFrame()
        self.additional_stats_df = pd.DataFrame()

    def get_soup(self):
        response = requests.get(self.url)
        response.raise_for_status()  # Check if the request was successful
        return BeautifulSoup(response.content, 'html.parser')

    def extract_shots_data(self):
        table = self.soup.find('table', {'id': 'shots_all'})

        headers = []
        for th in table.find_all('tr'):
            if 'over_header' in th.get('class', []):
                continue  # Skip the row with class 'over_header'
            for cell in th.find_all('th'):
                header = cell.get_text().strip()
                headers.append(header)
            break  # Only process the first valid header row

        rows = []
        for row in table.find_all('tr')[2:]:  # Skipping the first two header rows
            cells = row.find_all(['th', 'td'])
            row_data = [cell.get_text().strip() for cell in cells]
            rows.append(row_data)

        if len(headers) > len(rows[0]):
            headers = headers[:len(rows[0])]

        self.shots_df = pd.DataFrame(rows, columns=headers)

        # Add a column to indicate whether the minute is extra time or not
        def classify_minute(minute):
            if '+' in minute:
                return 'ET'
            return 'RT'

        self.shots_df['Minute Type'] = self.shots_df['Minute'].apply(classify_minute)

        # Normalize the minute column to a numerical value
        def normalize_minute(minute):
            if minute.strip() == '':
                return None  # Return None for empty minute values
            if '+' in minute:
                base, extra = minute.split('+')
                return int(base) + int(extra)
            return int(minute)

        self.shots_df['Minute'] = self.shots_df['Minute'].apply(normalize_minute)

        # Identify the separation between the halves
        self.shots_df['Half'] = '2'  # Default to 'Second Half'
        separation_index = self.shots_df[self.shots_df['Minute'].isnull()].index

        if len(separation_index) > 0:
            separation_index = separation_index[0]
            self.shots_df.loc[:separation_index - 1, 'Half'] = '1'  # Set 'First Half' for rows above separation
            self.shots_df = self.shots_df.dropna(how='all').reset_index(drop=True)

        # Drop rows with None in 'Minute' column
        self.shots_df = self.shots_df.dropna(subset=['Minute'])

    def extract_team_stats(self):
        team_stats = self.soup.find('div', id='team_stats')
        team_stats = team_stats.find('table')
        stats = {}

        def extract_team_stats(stats_dict, team_stats_div):
            rows = team_stats_div.find_all('tr')

            # Identify team names
            home_team_name = rows[0].find_all('th')[0].get_text(strip=True)
            away_team_name = rows[0].find_all('th')[1].get_text(strip=True)

            current_stat = ""

            for i in range(1, len(rows)):
                row = rows[i]
                ths = row.find_all('th')
                tds = row.find_all('td')

                if len(ths) == 1 and len(tds) == 0:
                    # This is a stat header row
                    current_stat = ths[0].get_text(strip=True)
                elif len(tds) == 2 and current_stat:
                    # This is a stat value row
                    home_team_stat = tds[0].find('strong').get_text(strip=True).replace('%', '') if tds[0].find(
                        'strong') else tds[0].get_text(strip=True)
                    away_team_stat = tds[1].find('strong').get_text(strip=True).replace('%', '') if tds[1].find(
                        'strong') else tds[1].get_text(strip=True)
                    stats_dict[current_stat] = [home_team_stat, away_team_stat]

        # Extract team stats using the dynamic logic
        extract_team_stats(stats, team_stats)

        # Create DataFrame for team stats
        self.team_stats_df = pd.DataFrame.from_dict(stats, orient='index', columns=['home_team', 'away_team'])

    def extract_additional_stats(self):
        team_stats_extra = self.soup.find('div', id='team_stats_extra')
        extra_stats = team_stats_extra.find_all('div') # usually three sections
        additional_stats = []

        for extra_stat_section in extra_stats:
            stat_divs = extra_stat_section.find_all('div')
            for i in range(3, len(stat_divs), 3):
                try:
                    stat_name = stat_divs[i + 1].get_text(strip=True)
                    home_team_stat = stat_divs[i].get_text(strip=True)
                    away_team_stat = stat_divs[i + 2].get_text(strip=True)
                    additional_stats.append([stat_name, home_team_stat, away_team_stat])
                except IndexError:
                    continue

        home_team_name = extra_stats[0].find_all('div')[0].get_text(strip=True)
        away_team_name = extra_stats[0].find_all('div')[2].get_text(strip=True)

        self.additional_stats_df = pd.DataFrame(additional_stats, columns=['Stat', 'home_team', 'away_team'])

    def save_data_to_csv(self):
        # Save the cleaned DataFrame to CSV
        self.shots_df.to_csv('shots_data_cleaned.csv', index=False)
        self.team_stats_df.to_csv('team_stats.csv', index=True)
        self.additional_stats_df.to_csv('additional_team_stats.csv', index=False)

    def extract_and_save_all_data(self):
        self.extract_shots_data()
        self.extract_team_stats()
        self.extract_additional_stats()
        self.save_data_to_csv()


# Example usage
url = "https://fbref.com/en/matches/82e1e5b8/Austin-FC-Minnesota-United-February-24-2024-Major-League-Soccer"
extractor = MatchDataExtractor(url)
extractor.extract_and_save_all_data()

