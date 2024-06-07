# game_data.py
import requests
import json
import pandas as pd
from .chosen_sports import sport_types
import pytz
from datetime import datetime, timedelta

def get_json(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    try:
        return response.json()
    except json.decoder.JSONDecodeError:
        print(f"Failed to decode JSON from response. Response text was:\n{response.text}")
        return None

def parse_json(response):
    all_games = []
    for game in response[0]['events']:
        away_team = home_team = 'n/a'
        for team in game['competitors']:
            if team['home'] is True:
                home_team = team['name']
            else:
                away_team = team['name']
        all_games.append({
            'id': game['id'],
            'description': game['description'],
            'link': game['link'],
            'sport': response[0]['path'][0]['description'],
            'startTime': game['startTime'],
            'live': game['live'],
            'competitionId': game['competitionId'],
            'lastModified': game['lastModified'],
            'awayTeam': away_team,
            'homeTeam': home_team
        })
    df = pd.DataFrame(all_games)
    return df


def pull_games(sport_types):
    sport_data = []

    for sport_type in sport_types:
        print(f'Pulling in {sport_type}...')
        bovada_link = f'https://www.bovada.lv/services/sports/event/coupon/events/A/description/{sport_type}?marketFilterId=def&preMatchOnly=false&eventsLimit=5000&lang=en'
        fin_json = get_json(bovada_link)
        if fin_json:
            df = parse_json(fin_json)
            sport_data.append(df)
            print('Sport pulled successfully.')

    if sport_data:
        # Concatenate all DataFrames
        combined_df = pd.concat(sport_data, ignore_index=True)
        # Sort by 'sport' column
        combined_df = combined_df.sort_values(by='sport', ascending=True).reset_index(drop=True)
        return combined_df
    else:
        print('Error in pulling sport data.')
        return None


def split_games_by_upcoming(games_list):
    central_tz = pytz.timezone('America/Chicago')
    current_time = datetime.now(central_tz)
    upcoming_time = current_time + timedelta(hours=24)

    all_games = []
    upcoming_games = []
    not_upcoming_games = []

    for game in games_list:
        game_time = datetime.fromtimestamp(game['startTime'] / 1000, tz=central_tz)
        game['formatted_start_time'] = game_time.strftime('%-m/%-d %-I:%M%p').lower()
        game['upcoming_game'] = game_time <= upcoming_time
        all_games.append(game)
        if game['upcoming_game']:
            upcoming_games.append(game)
        else:
            not_upcoming_games.append(game)

    return all_games, upcoming_games, not_upcoming_games


def pull_all_games():
    return pull_games(sport_types)


if __name__ == '__main__':
    pull_all_games().to_csv('games.csv')