import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the datasets
cleaned_data = pd.read_csv('../../season_stats/major_league_soccer/cleaned_data_major_league_soccer.csv')
team_stats = pd.read_csv('../../season_stats/major_league_soccer/team_stats_major_league_soccer.csv')

# Convert cleaned_data possession values to numeric
cleaned_data['home_Possession_value'] = pd.to_numeric(cleaned_data['home_Possession_value'], errors='coerce')
cleaned_data['away_Possession_value'] = pd.to_numeric(cleaned_data['away_Possession_value'], errors='coerce')

# Remove percentage sign and convert to numeric in team_stats
team_stats['home_Possession_value'] = team_stats['home_Possession_value'].str.rstrip('%').astype(float) / 100
team_stats['away_Possession_value'] = team_stats['away_Possession_value'].str.rstrip('%').astype(float) / 100

# Merge the datasets on game_id and date
merged_data = pd.merge(cleaned_data, team_stats, on=['game_id', 'date', 'home_team', 'away_team', 'league'], suffixes=('_pre', '_actual'))

# Function to categorize possession scenarios based on pre-match possession
def categorize_possession(row):
    if row['home_Possession_value_pre'] > .5 and row['away_Possession_value_pre'] > .5:
        return 'Both Above 50%'
    elif row['home_Possession_value_pre'] < .5 and row['away_Possession_value_pre'] < .5:
        return 'Both Below 50%'
    elif row['home_Possession_value_pre'] > .5 and row['away_Possession_value_pre'] < .5:
        return 'Home Above 50%'
    elif row['home_Possession_value_pre'] < .5 and row['away_Possession_value_pre'] > .5:
        return 'Away Above 50%'
    else:
        return 'Mixed'

# Apply the categorization function
merged_data['possession_scenario'] = merged_data.apply(categorize_possession, axis=1)

# Calculate average possession values for each scenario
possession_means = merged_data.groupby('possession_scenario').agg({
    'home_Possession_value_pre': 'mean',
    'away_Possession_value_pre': 'mean',
    'home_Possession_value_actual': 'mean',
    'away_Possession_value_actual': 'mean'
}).reset_index()

# Melt the dataframe for easier plotting
possession_means_melted = possession_means.melt(id_vars='possession_scenario',
                                                value_vars=['home_Possession_value_pre', 'away_Possession_value_pre',
                                                            'home_Possession_value_actual', 'away_Possession_value_actual'],
                                                var_name='Type', value_name='Possession')

# Update the Type column for better legend titles
possession_means_melted['Type'] = possession_means_melted['Type'].map({
    'home_Possession_value_pre': 'Home Pre-Match',
    'away_Possession_value_pre': 'Away Pre-Match',
    'home_Possession_value_actual': 'Home Actual',
    'away_Possession_value_actual': 'Away Actual'
})

# Set custom colors for the bars
palette = ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78']

# Bar plot
plt.figure(figsize=(14, 8))
sns.barplot(data=possession_means_melted, x='possession_scenario', y='Possession', hue='Type', palette=palette)
plt.title('Average Pre-Match vs Actual Possession for Different Scenarios')
plt.ylabel('Possession (%)')
plt.xlabel('Possession Scenario')

# Move the legend outside the plot
plt.legend(title='Possession Type', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()
