import json
import os

def load_json_mappings(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Get the directory where this script is located
base_dir = os.path.dirname(__file__)
# Build the full path to the names.json file
file_path = os.path.join(base_dir, 'names.json')

MAPPINGS = load_json_mappings(file_path)

def get_mapped_name(entry_name, entry_type, exit_type, mappings=MAPPINGS):
    """
    Retrieve the mapped name for a given entry name and type, returning the name of the desired exit type.

    :param entry_name: The name to look up.
    :param entry_type: The type of the entry name (e.g., 'bovada_name', 'vsin_name', 'stats_name').
    :param exit_type: The desired type of the exit name (e.g., 'bovada_name', 'vsin_name', 'stats_name').
    :param mappings: The mappings dictionary loaded from JSON.
    :return: The mapped name if found, otherwise the original entry name.
    """
    for league in mappings['leagues']:
        for team_name, team_data in league['teams'].items():
            if team_data.get(entry_type) == entry_name:
                return team_data.get(exit_type, entry_name)
    return entry_name

def get_mapped_league_name(entry_name, entry_type, exit_type, mappings=MAPPINGS):
    """
    Retrieve the mapped league name for a given entry name and type, returning the name of the desired exit type.

    :param entry_name: The league name to look up.
    :param entry_type: The type of the entry league name (e.g., 'bovada_league_name', 'stats_league_short_name').
    :param exit_type: The desired type of the exit league name (e.g., 'stats_league_long_name', 'stats_league_code').
    :param mappings: The mappings dictionary loaded from JSON.
    :return: The mapped league name if found, otherwise the original entry name.
    """
    for league in mappings['leagues']:
        if league.get(entry_type) == entry_name:
            return league.get(exit_type, entry_name)
    return entry_name

def listed_teams_for_dashboard(mappings=MAPPINGS):
    sorted_team_mappings = {}
    for league in sorted(mappings['leagues'], key=lambda x: x['bovada_league_name']):
        sorted_teams = dict(sorted(league['teams'].items(), key=lambda item: item[1]['stats_name']))
        sorted_team_mappings[league['stats_league_long_name']] = {
            'league_name': league['bovada_league_name'],
            'teams': sorted_teams
        }
    return sorted_team_mappings

# Example usage for debugging
if __name__ == "__main__":
    # Test team name mapping
    entry_name = "Criciúma SC"
    entry_type = "bovada_name"
    exit_type = "stats_name"
    mapped_name = get_mapped_name(entry_name, entry_type, exit_type)
    print(f"The {exit_type} for {entry_type} '{entry_name}' is '{mapped_name}'")

    entry_name = "Vitória BA"
    mapped_name = get_mapped_name(entry_name, entry_type, exit_type)
    print(f"The {exit_type} for {entry_type} '{entry_name}' is '{mapped_name}'")

    # Test league name mapping
    league_entry_name = "Brasileirão Série A"
    league_entry_type = "bovada_league_name"
    league_exit_type = "stats_league_long_name"
    mapped_league_name = get_mapped_league_name(league_entry_name, league_entry_type, league_exit_type)
    print(f"The {league_exit_type} for {league_entry_type} '{league_entry_name}' is '{mapped_league_name}'")

    # Test sorting
    sorted_mappings = listed_teams_for_dashboard(MAPPINGS)
    print(f"Sorted team mappings: {json.dumps(sorted_mappings, indent=4)}")
