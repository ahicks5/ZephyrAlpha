import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import os

class MatchDataExtractor:
    def __init__(self, base_url, schedule_url):
        self.base_url = base_url
        self.schedule_url = schedule_url
        self.urls = self.get_match_report_links()
        self.shots_data = pd.DataFrame()
        self.team_stats_data = pd.DataFrame()

    def get_soup(self, url):
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        return BeautifulSoup(response.content, 'html.parser')

    def get_match_report_links(self):
        soup = self.get_soup(self.schedule_url)
        match_report_links = []

        for td in soup.find_all('td', {'data-stat': 'match_report'}):
            a_tag = td.find('a')
            if a_tag and 'href' in a_tag.attrs and a_tag.get_text(strip=True) == "Match Report":
                match_report_links.append(self.base_url + a_tag['href'])

        return match_report_links

    def extract_game_id_from_url(self, url):
        return url.split('/')[-1]

    def extract_teams_date_and_league_from_h1(self, soup):
        content_div = soup.find('div', {'id': 'content', 'role': 'main', 'class': 'box'})
        h1_tag = content_div.find('h1')
        match_info = h1_tag.get_text(strip=True)

        # Split the string to extract home team, away team, and date
        home_team, away_team = match_info.split(' Match Report – ')[0].split(' vs. ')
        # Extract the date and format it
        date_part = match_info.split(' Match Report – ')[1]
        # Find the comma and take the first 5 characters after it to isolate the year
        comma_index = date_part.find(',')
        date_str = date_part[:comma_index + 6]  # This includes the space and the 4-digit year
        game_date = datetime.strptime(date_str, '%A %B %d, %Y').strftime('%Y-%m-%d')

        # Extract league name
        league_div = h1_tag.find_next_sibling('div')
        league_name = league_div.find('a').get_text(strip=True)

        return home_team, away_team, game_date, league_name

    def extract_shots_data(self, soup, game_id):
        table = soup.find('table', {'id': 'shots_all'})

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

        shots_df = pd.DataFrame(rows, columns=headers)
        shots_df['game_id'] = game_id  # Add game ID to each row

        # Add a column to indicate whether the minute is extra time or not
        def classify_minute(minute):
            if '+' in minute:
                return 'ET'
            return 'RT'

        shots_df['Minute Type'] = shots_df['Minute'].apply(classify_minute)

        # Normalize the minute column to a numerical value
        def normalize_minute(minute):
            if minute.strip() == '':
                return None  # Return None for empty minute values
            if '+' in minute:
                base, extra = minute.split('+')
                return int(base) + int(extra)
            return int(minute)

        shots_df['Minute'] = shots_df['Minute'].apply(normalize_minute)

        # Identify the separation between the halves
        shots_df['Half'] = '2'  # Default to 'Second Half'
        separation_index = shots_df[shots_df['Minute'].isnull()].index

        if len(separation_index) > 0:
            separation_index = separation_index[0]
            shots_df.loc[:separation_index - 1, 'Half'] = '1'  # Set 'First Half' for rows above separation
            shots_df = shots_df.dropna(how='all').reset_index(drop=True)

        # Drop rows with None in 'Minute' column
        shots_df = shots_df.dropna(subset=['Minute'])

        return shots_df

    def extract_team_stats(self, soup, game_id, home_team, away_team, game_date, league_name):
        team_stats = soup.find('div', id='team_stats')
        team_stats = team_stats.find('table')
        stats = {'game_id': game_id, 'date': game_date, 'home_team': home_team, 'away_team': away_team,
                 'league': league_name}

        def clean_text(text):
            return text.replace(u'\xa0', u' ').replace('Â', '').replace('â€”', '—').strip()

        def extract_team_stats(stats_dict, team_stats_div):
            rows = team_stats_div.find_all('tr')
            current_stat = ""

            for i in range(1, len(rows)):
                row = rows[i]
                ths = row.find_all('th')
                tds = row.find_all('td')

                if len(ths) == 1 and len(tds) == 0:
                    # This is a stat header row
                    current_stat = ths[0].get_text(strip=True)
                elif len(tds) == 2 and current_stat:
                    home_team_stat_raw = clean_text(tds[0].get_text(strip=True))
                    away_team_stat_raw = clean_text(tds[1].get_text(strip=True))

                    home_team_value, home_team_attempts = None, None
                    away_team_value, away_team_attempts = None, None

                    ## In cases of possession, just a pure %
                    if len(home_team_stat_raw) == 0:
                        continue

                    if (len(home_team_stat_raw) < 5) and (home_team_stat_raw[-1] == '%') and \
                            (len(away_team_stat_raw) < 5) and (away_team_stat_raw[-1] == '%'):
                        stats_dict[f'home_{current_stat}_value'] = home_team_stat_raw.strip()
                        stats_dict[f'away_{current_stat}_value'] = away_team_stat_raw.strip()
                        continue

                    ## Normal cases
                    if '%' == home_team_stat_raw[-1]:
                        home_team_value = home_team_stat_raw.split('of')[0].strip()
                        home_team_attempts = home_team_stat_raw.split('of')[1].split('—')[0].strip()
                    elif '—' in home_team_stat_raw[:5]:
                        home_team_value = home_team_stat_raw.split('—')[1].split('of')[0].strip()
                        home_team_attempts = home_team_stat_raw.split('of')[1].strip()
                    else:
                        continue

                    ## Normal cases
                    if '%' == away_team_stat_raw[-1]:
                        away_team_value = away_team_stat_raw.split('of')[0].strip()
                        away_team_attempts = away_team_stat_raw.split('of')[1].split('—')[0].strip()
                    elif '—' in away_team_stat_raw[:5]:
                        away_team_value = away_team_stat_raw.split('—')[1].split('of')[0].strip()
                        away_team_attempts = away_team_stat_raw.split('of')[1].strip()

                    stats_dict[f'home_{current_stat}_value'] = home_team_value
                    stats_dict[f'home_{current_stat}_attempts'] = home_team_attempts
                    stats_dict[f'away_{current_stat}_value'] = away_team_value
                    stats_dict[f'away_{current_stat}_attempts'] = away_team_attempts

        # Extract team stats using the dynamic logic
        extract_team_stats(stats, team_stats)

        # Extract goals and expected goals
        stats['home_goals'] = soup.find_all('div', class_='score')[0].get_text(strip=True)
        stats['away_goals'] = soup.find_all('div', class_='score')[1].get_text(strip=True)
        stats['home_xg'] = soup.find_all('div', class_='score_xg')[0].get_text(strip=True)
        stats['away_xg'] = soup.find_all('div', class_='score_xg')[1].get_text(strip=True)

        # Additional stats extraction
        team_stats_extra = soup.find('div', id='team_stats_extra')
        extra_stats = team_stats_extra.find_all('div')  # usually three sections

        for extra_stat_section in extra_stats:
            stat_divs = extra_stat_section.find_all('div')
            for i in range(3, len(stat_divs), 3):
                try:
                    stat_name = stat_divs[i + 1].get_text(strip=True)
                    home_team_stat = clean_text(stat_divs[i].get_text(strip=True))
                    away_team_stat = clean_text(stat_divs[i + 2].get_text(strip=True))
                    stats[f'home_{stat_name}'] = home_team_stat
                    stats[f'away_{stat_name}'] = away_team_stat
                except IndexError:
                    continue

        return pd.DataFrame([stats])

    def extract_and_save_all_data(self):
        estimated_time = len(self.urls) * 6  # Estimate 6 seconds per item
        print(f"Estimated total processing time: {estimated_time // 60} minutes and {estimated_time % 60} seconds")

        for url in self.urls:
            soup = self.get_soup(url)
            game_id = self.extract_game_id_from_url(url)
            home_team, away_team, game_date, league_name = self.extract_teams_date_and_league_from_h1(soup)

            shots_df = self.extract_shots_data(soup, game_id)
            team_stats_df = self.extract_team_stats(soup, game_id, home_team, away_team, game_date, league_name)

            self.shots_data = pd.concat([self.shots_data, shots_df], ignore_index=True)
            self.team_stats_data = pd.concat([self.team_stats_data, team_stats_df], ignore_index=True)

            print(f"Successfully pulled data for {home_team} vs {away_team} on {game_date}")
            time.sleep(4)  # Wait for 4 seconds before making the next request

        # Save data to CSV with league name included in the filename
        self.save_data_to_csv(league_name)

    def save_data_to_csv(self, league_name):
        # Format league name to be filename friendly
        league_name_tag = league_name.replace(' ', '_').lower()

        # Define the directory path
        directory = os.path.join('..', 'season_stats', league_name_tag)

        # Create the directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)

        # Define file paths
        shots_file_path = os.path.join(directory, f'shots_data_{league_name_tag}.csv')
        team_stats_file_path = os.path.join(directory, f'team_stats_{league_name_tag}.csv')

        # Save data to CSV files
        #self.shots_data.to_csv(shots_file_path, index=False)
        self.team_stats_data.to_csv(team_stats_file_path, index=False)


# Example usage
base_url = "https://fbref.com"
schedule_url = "https://fbref.com/en/comps/22/schedule/Major-League-Soccer-Scores-and-Fixtures"

extractor = MatchDataExtractor(base_url, schedule_url)
extractor.extract_and_save_all_data()
