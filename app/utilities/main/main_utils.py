# game_data.py
import requests
import json
import pandas as pd
import pytz
from datetime import datetime, timedelta
from app.extensions import cache  # Adjust the import path based on your project structure

sport_types = [
    'basketball/nba',
    #'basketball/wncaa',
    'basketball/wnba',
    'soccer/north-america/united-states/mls',
    'hockey/nhl',
    #'basketball/europe/belarus/belarus-nbbl',
    #'basketball/college-basketball',
    'soccer/south-america/brazil/brasileirao-serie-a'
    # Add more sport types here if needed
]

CACHE_TIMEOUT = 60 * 15  # 15 minutes

def pull_all_games_cached():
    games_df = cache.get('games_df')
    if games_df is None:
        games_df = pull_all_games()
        cache.set('games_df', games_df, timeout=CACHE_TIMEOUT)
        print("Cache miss: fetched new games data.")
    return games_df


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
    all_games = [
        {
            'id': game['id'],
            'description': game['description'],
            'link': game['link'],
            'sport': response[0]['path'][0]['description'],
            'startTime': game['startTime'],
            'live': game['live'],
            'competitionId': game['competitionId'],
            'lastModified': game['lastModified'],
            'awayTeam': next(team['name'] for team in game['competitors'] if not team['home']),
            'homeTeam': next(team['name'] for team in game['competitors'] if team['home'])
        }
        for game in response[0]['events']
    ]
    return pd.DataFrame(all_games)


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


def split_and_group_games_by_sport(games_list):
    # Sort games_list by 'startTime' in ascending order
    games_list = sorted(games_list, key=lambda x: x['startTime'])

    central_tz = pytz.timezone('America/Chicago')
    current_time = datetime.now(central_tz)
    upcoming_time = current_time + timedelta(hours=24)

    games_by_sport = {}

    for game in games_list:
        game_time = datetime.fromtimestamp(game['startTime'] / 1000, tz=central_tz)
        game['formatted_start_time'] = game_time.strftime('%-m/%-d %-I:%M%p').lower()
        game['upcoming_game'] = game_time <= upcoming_time

        sport = game['sport']
        if sport not in games_by_sport:
            games_by_sport[sport] = {'upcoming': [], 'later': []}

        if game['upcoming_game']:
            games_by_sport[sport]['upcoming'].append(game)
        else:
            games_by_sport[sport]['later'].append(game)

    return games_by_sport


def pull_all_games():
    return pull_games(sport_types)


if __name__ == '__main__':
    #pull_all_games().to_csv('games.csv')
    parse_json(get_json(f'https://www.bovada.lv/services/sports/event/coupon/events/A/description/soccer/north-america/united-states/mls?marketFilterId=def&preMatchOnly=false&eventsLimit=5000&lang=en'))