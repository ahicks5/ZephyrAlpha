team_mappings = {
    "major_league_soccer": {
        "league_name": "MLS",
        "teams": {
            "Minnesota United": "Minnesota United",
            "FC Cincinnati": "FC Cincinnati",
            "Sporting Kansas City": "Sporting Kansas City",
            "Austin FC": "Austin FC",
            "Chicago Fire": "Chicago Fire",
            "Inter Miami": "Inter Miami",
            "Los Angeles FC": "Los Angeles FC",
            "Vancouver Whitecaps": "Vancouver Whitecaps FC",
            "Nashville SC": "Nashville SC",
            "DC United": "D.C. United",
            "Real Salt Lake": "Real Salt Lake",
            "Houston Dynamo": "Houston Dynamo",
            "Columbus Crew": "Columbus Crew",
            "Portland Timbers": "Portland Timbers",
            "Seattle Sounders": "Seattle Sounders FC",
            "FC Dallas": "FC Dallas",
            "New York Red Bulls": "New York Red Bulls",
            "St. Louis City SC": "St. Louis City",
            "San Jose Earthquakes": "San Jose Earthquakes",
            "LA Galaxy": "LA Galaxy",
            "Colorado Rapids": "Colorado Rapids",
            "Toronto FC": "Toronto FC",
            "Philadelphia Union": "Philadelphia Union",
            "Orlando City": "Orlando City",
            "New England Revolution": "New England Revolution",
            "Charlotte FC": "Charlotte FC",
            "CF Montréal": "CF Montréal",
            "Atlanta United": "Atlanta United",
            "New York City FC": "New York City FC"
        }
    },
    "campeonato_brasileiro_série_a": {
        "league_name": "Brasileirão Série A",
        "teams": {
            "Vasco da Gama": "Vasco da Gama",
            "São Paulo": "São Paulo",
            "Grêmio": "Grêmio",
            "Criciúma SC": "Criciúma",
            "Cuiabá": "Cuiabá",
            "Atlético Mineiro": "Atlético Mineiro",
            "Fluminense": "Fluminense",
            "Vitória BA": "Vitória",
            "Corinthians": "Corinthians",
            "Fortaleza": "Fortaleza",
            "Palmeiras": "Palmeiras",
            "Internacional": "Internacional",
            "Flamengo": "Flamengo",
            "Athletico Paranaense": "Athletico Paranaense",
            "Cruzeiro MG": "Cruzeiro",
            "RB Bragantino": "Red Bull Bragantino",
            "Botafogo": "Botafogo",
            "Juventude": "Juventude",
            "Atlético Goianiense": "Atlético Goianiense",
            "Bahia": "Bahia",
            "Goiás": "Goiás",
            "Chapecoense": "Chapecoense",
            "Avaí": "Avaí"
        }
    }
}

base_path = "/var/www/html/season_stats/"
#base_path = "C:/Users/arhic/PycharmProjects/ZephyrAlpha/season_stats/"

def sort_team_mappings(team_mappings):
    sorted_team_mappings = {}
    for league_key, league_data in sorted(team_mappings.items(), key=lambda item: item[1]['league_name']):
        sorted_teams = dict(sorted(league_data['teams'].items(), key=lambda item: item[1]))
        sorted_team_mappings[league_key] = {
            'league_name': league_data['league_name'],
            'teams': sorted_teams
        }
    return sorted_team_mappings