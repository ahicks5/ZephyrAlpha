import requests


def get_live_scores(sport_key, api_key):
    base_url = "https://api.the-odds-api.com/v4/sports/{sport}/scores/"
    params = {
        'apiKey': api_key,
        'daysFrom': 1,  # Adjust based on your requirements.
    }

    request_url = base_url.format(sport=sport_key)

    response = requests.get(request_url, params=params)

    if response.status_code == 200:
        games = response.json()
        print(games)
        live_games = [game for game in games if not game['completed']]

        if live_games:
            print("Live Games:")
            for game in live_games:
                home_team = game['home_team']
                away_team = game['away_team']
                # Check if 'scores' is not None before iterating
                if game['scores'] is not None:
                    home_score = next((score['score'] for score in game['scores'] if score['name'] == home_team), 'N/A')
                    away_score = next((score['score'] for score in game['scores'] if score['name'] == away_team), 'N/A')
                    print(f"{home_team} vs. {away_team}: {home_score} - {away_score}")
                else:
                    print(f"{home_team} vs. {away_team}: Scores not available yet")
        else:
            print("There are no live games at the moment.")
    else:
        print("Failed to retrieve data. Status code:", response.status_code)


if __name__ == "__main__":
    API_KEY = 'f1ceefc4c695f35ad27ec1a83dfa69c3'
    SPORT_KEY = 'basketball_ncaab'  # Use your specific sport key here
    get_live_scores(SPORT_KEY, API_KEY)
