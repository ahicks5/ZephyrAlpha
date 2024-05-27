# bet_data_processing.py
from app.utilities.data_fetching import get_bet_data
from app.utilities.cleaning_utils import calculate_juice, adjust_probabilities_for_juice


def organize_game_data(data):
    relevant_data = {
        "spread_bets": {},
        "over_under_bets": {},
        "moneyline_bets": {}
    }

    for event in data[0]['events']:
        for displayGroup in event['displayGroups']:
            if displayGroup['description'] == 'Game Lines':
                for market in displayGroup['markets']:
                    if market['period']['abbreviation'] == 'G':
                        odds_list = [outcome['price']['american'] for outcome in market['outcomes']]
                        juice, total_market_probability = calculate_juice(odds_list)  # Calculate juice for the market
                        implied_probabilities = adjust_probabilities_for_juice(odds_list)  # Adjust probabilities for juice

                        if ('Point Spread' in market['description']) or ('Puck Line' in market['description']):
                            for i, outcome in enumerate(market['outcomes']):
                                key = "home" if outcome['type'] == 'H' else "away"
                                relevant_data["spread_bets"][key] = {
                                    "odds": outcome['price']['american'],
                                    "spread": outcome['price']['handicap'],
                                    "probability": implied_probabilities[i],
                                    "juice": juice
                                }
                        elif 'Total' in market['description']:
                            for i, outcome in enumerate(market['outcomes']):
                                key = "over" if outcome['type'] == 'O' else "under"
                                relevant_data["over_under_bets"][key] = {
                                    "odds": outcome['price']['american'],
                                    "total": outcome['price']['handicap'],
                                    "probability": implied_probabilities[i],
                                    "juice": juice
                                }
                        elif 'Moneyline' in market['description']:
                            for i, outcome in enumerate(market['outcomes']):
                                key = "home" if outcome['type'] == 'H' else "away"
                                relevant_data["moneyline_bets"][key] = {
                                    "odds": outcome['price']['american'],
                                    "probability": implied_probabilities[i],
                                    "juice": juice
                                }

    return relevant_data


def calculate_assumed_final_score(spread_bets, over_under_bets):
    if not spread_bets or not over_under_bets:
        return None  # Return None or an appropriate message if the necessary bets are not available

    # Assuming spread is for the home team and adjusting based on that
    spread = float(spread_bets.get('home', {}).get('spread', 0))
    total = float(over_under_bets.get('over', {}).get('total', 0))  # Assuming 'over' and 'under' have the same total

    # Initial split of the total
    base_score = total / 2

    # Adjusting based on the spread
    home_score = base_score - spread / 2
    away_score = base_score + spread / 2

    return {
        "proj_home_score": round(home_score, 2),
        "proj_away_score": round(away_score, 2)
    }


def get_organize_bet_data(link):
    data = get_bet_data(link)
    organized_data = organize_game_data(data)

    # Calculate assumed final score
    final_score_assumption = calculate_assumed_final_score(organized_data['spread_bets'],
                                                           organized_data['over_under_bets'])
    organized_data['assumed_final_score'] = final_score_assumption

    print(organized_data)

    return organized_data


if __name__ == '__main__':
    get_organize_bet_data('hockey/nhl/new-jersey-devils-san-jose-sharks-202402272242')