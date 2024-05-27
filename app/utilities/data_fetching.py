import requests

def get_live_game_data(event_id):
    url = f"https://services.bovada.lv/services/sports/results/api/v2/scores/{event_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept': 'application/json',
        'Connection': 'keep-alive',
        # Add other headers if necessary
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError if the response status code is 4XX/5XX
        data = response.json()
        return data
    except requests.RequestException as e:
        print(f"Error fetching live game data for event ID {event_id}: {e}")
        return None


def get_bet_data(link):
    # Base URL for detailed data, adjust as necessary
    base_url = "https://www.bovada.lv/services/sports/event/coupon/events/A/description"

    # Transform the link into the required API endpoint format
    detailed_url = f"{base_url}/{link}?lang=en"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept': 'application/json',
        'Connection': 'keep-alive',
    }
    try:
        response = requests.get(detailed_url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError if the response status code is 4XX/5XX
        data = response.json()
        return data
    except requests.RequestException as e:
        print(f"Error fetching detailed game data from {detailed_url}: {e}")
        return None
