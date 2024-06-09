import statistics

data = {
    "leagueAverages": {
        "home_goals": 1.1875,
        "away_goals": 1.09375,
        "home_Shots on Target_value": 4.46875,
        "away_Shots on Target_value": 3.71875,
        "home_Saves_value": 2.78125,
        "away_Saves_value": 3.3125,
        "home_Possession_value": 0.50125,
        "away_Possession_value": 0.49875
    },
    "leagueStdDevs": {
        "home_goals": 1.0671873729054748,
        "away_goals": 1.1229036906220846,
        "home_Shots on Target_value": 2.481479013660622,
        "away_Shots on Target_value": 2.621454521734796,
        "home_Saves_value": 1.9393072728200393,
        "away_Saves_value": 2.076894812813606,
        "home_Possession_value": 0.1045701708658862,
        "away_Possession_value": 0.1045701708658862
    },
    "teams": [
        {
            "name": "Cruzeiro",
            "metrics": {
                "goals_scored": 0.13665204165253023,
                "goals_allowed": 0.3617852567346528,
                "shots_on_target": -0.12173519569190572,
                "saves": -0.2309673525925211,
                "possession": 0.17930543523781153
            }
        },
        {
            "name": "Cuiabá",
            "metrics": {
                "goals_scored": -1.1127380534563183,
                "goals_allowed": 0.6586346981579576,
                "shots_on_target": -1.263527375974609,
                "saves": 0.19873934990519254,
                "possession": -0.792928480273875
            }
        }
    ]
}


def calculate_percentile(rank, mean, std_dev):
    z_score = (rank - mean) / std_dev
    percentile = (1 + statistics.NormalDist().cdf(z_score)) * 50
    return percentile


def get_team_percentiles(team, league_averages, league_std_devs):
    percentiles = {}
    for stat, value in team['metrics'].items():
        stat_key = stat.replace("goals_scored", "home_goals").replace("goals_allowed", "away_goals").replace(
            "shots_on_target", "home_Shots on Target_value").replace("saves", "home_Saves_value").replace("possession",
                                                                                                          "home_Possession_value")
        mean = league_averages[stat_key]
        std_dev = league_std_devs[stat_key]
        percentiles[stat] = calculate_percentile(value, mean, std_dev)
    return percentiles


def generate_team_description(team, opponent, team_percentiles, opponent_percentiles, home=True):
    team_role = "home" if home else "away"
    description = f"{team['name']} ({team_role}) analysis: "

    # Scoring potential
    scoring_potential = team_percentiles['goals_scored'] > 50
    opponent_defense_weakness = opponent_percentiles['goals_allowed'] > 50

    if scoring_potential and opponent_defense_weakness:
        description += f"{team['name']} is likely to score multiple goals given their strong scoring ability and {opponent['name']}'s weaker defense. "
    elif scoring_potential:
        description += f"{team['name']} has a good scoring potential but will be up against a strong defense. "
    elif opponent_defense_weakness:
        description += f"{team['name']} might struggle to score, but {opponent['name']}'s weak defense could offer opportunities. "

    # Shots on target
    shots_potential = team_percentiles['shots_on_target'] > 50
    opponent_saves_weakness = opponent_percentiles['saves'] < 50

    if shots_potential and opponent_saves_weakness:
        description += f"{team['name']} will likely create many scoring opportunities as {opponent['name']} struggles to make crucial saves. "
    elif shots_potential:
        description += f"{team['name']} is expected to get several shots on target, testing {opponent['name']}'s goalkeeper. "
    elif opponent_saves_weakness:
        description += f"{team['name']} might not get many shots on target, but any they do could be dangerous due to {opponent['name']}'s weak goalkeeping. "

    # Efficiency
    efficiency = team_percentiles['goals_scored'] > 50 and team_percentiles['shots_on_target'] < 50
    if efficiency:
        description += f"{team['name']} is highly efficient with their shots, often converting their few opportunities into goals. "

    # Possession
    possession_dominance = team_percentiles['possession'] > 50
    opponent_possession_weakness = opponent_percentiles['possession'] < 50

    if possession_dominance and opponent_possession_weakness:
        description += f"{team['name']} will dominate possession, controlling the game's pace. "
    elif possession_dominance:
        description += f"{team['name']} is expected to hold the ball more and control the game's tempo. "
    elif opponent_possession_weakness:
        description += f"{team['name']} might not dominate possession but will face an opponent that struggles to keep the ball. "

    return description


# Calculate percentiles for each team
cruzeiro_percentiles = get_team_percentiles(data['teams'][0], data['leagueAverages'], data['leagueStdDevs'])
cuiaba_percentiles = get_team_percentiles(data['teams'][1], data['leagueAverages'], data['leagueStdDevs'])

# Generate game descriptions
cruzeiro_description = generate_team_description(data['teams'][0], data['teams'][1], cruzeiro_percentiles,
                                                 cuiaba_percentiles, home=True)
cuiaba_description = generate_team_description(data['teams'][1], data['teams'][0], cuiaba_percentiles,
                                               cruzeiro_percentiles, home=False)

print(cruzeiro_description)
print(cuiaba_description)

