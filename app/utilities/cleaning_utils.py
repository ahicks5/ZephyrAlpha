def american_odds_to_probability(odds):
    if odds == "EVEN":
        return 0.5  # Return as a fraction
    else:
        odds = int(odds)
        probability = 100 / (odds + 100) if odds > 0 else abs(odds) / (abs(odds) + 100)
        return probability  # Keep as a fraction

def calculate_juice(odds_list):
    probabilities = [american_odds_to_probability(odds) for odds in odds_list]
    total_market_probability = sum(probabilities)
    juice_percentage = (total_market_probability - 1) * 100  # Calculate juice in percentage
    return round(juice_percentage, 2), total_market_probability  # Return both juice and total market probability

def adjust_probabilities_for_juice(odds_list):
    raw_probabilities = [american_odds_to_probability(odds) for odds in odds_list]
    total_market_probability = sum(raw_probabilities)
    implied_probabilities = [(prob / total_market_probability) * 100 for prob in raw_probabilities]
    return implied_probabilities
