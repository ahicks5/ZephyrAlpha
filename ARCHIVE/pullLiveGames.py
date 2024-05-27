import requests
import json
import pandas as pd


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
    all_dataframes = []
    for sport_type in sport_types:
        print(f'Pulling in {sport_type}...')
        bovada_link = f'https://www.bovada.lv/services/sports/event/coupon/events/A/description/{sport_type}?marketFilterId=def&preMatchOnly=false&eventsLimit=5000&lang=en'
        fin_json = get_json(bovada_link)
        if fin_json:
            df = parse_json(fin_json)
            all_dataframes.append(df)
            print('Sport pulled successfully.')
    if all_dataframes:
        return pd.concat(all_dataframes, ignore_index=True)
    else:
        print('Error is pulling sport data.')
        return None


def pull_all_games():
    sport_types = [
        #'basketball/college-basketball',
        'basketball/nba',
        #'basketball/wncaa',
        #'hockey/nhl',
        #'basketball/europe/belarus/belarus-nbbl'
        # Add more sport types here if needed
    ]
    return pull_games(sport_types)


if __name__ == '__main__':
    pull_all_games().to_csv('test.csv')
