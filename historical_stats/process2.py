import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL of the match
url = "https://fbref.com/en/matches/82e1e5b8/Austin-FC-Minnesota-United-February-24-2024-Major-League-Soccer"

# Send a request to the URL
response = requests.get(url)
response.raise_for_status()  # Check if the request was successful

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Process 1: Extract Shots Data
table = soup.find('table', {'id': 'shots_all'})

# Process 3: Extract Additional Stats
team_stats_extra = soup.find('div', id='team_stats_extra')
extra_stats = team_stats_extra.find_all('div')
additional_stats = {}

for i in range(0, len(extra_stats), 5):
    try:
        stat_name = extra_stats[i+1].text.strip()
        home_team_stat = extra_stats[i+2].text.strip()
        away_team_stat = extra_stats[i+4].text.strip()
        additional_stats[stat_name] = [home_team_stat, away_team_stat]
    except IndexError:
        continue

additional_stats_df = pd.DataFrame.from_dict(additional_stats, orient='index', columns=['home_team', 'away_team'])
additional_stats_df.to_csv('additional_team_stats.csv', index=False)
