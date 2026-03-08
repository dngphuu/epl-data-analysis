import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def main():
    os.makedirs('reports/figures', exist_ok=True)
    df = pd.read_csv('data/processed/merged_epl_24_25.csv')
    
    # Identify numeric columns for statistics
    # Filtering out identifiers like Player, Club, Nationality, Position
    exclude_cols = ['Player', 'Club', 'Nationality', 'Position', 'TransferValue_Str', 'TM_Player_Match']
    numeric_df = df.select_dtypes(include=[np.number]).drop(columns=[c for c in exclude_cols if c in df.columns], errors='ignore')
    
    stats_cols = numeric_df.columns.tolist()
    
    print("Finding top 3 and bottom 3 players for each statistic...")
    with open('reports/top_3.txt', 'w', encoding='utf-8') as f:
        for col in stats_cols:
            f.write(f"=== {col} ===\n")
            # dropna is important to not consider NaNs as top or bottom
            valid_data = df[['Player', col]].dropna().sort_values(by=col, ascending=False)
            if valid_data.empty:
                continue
            
            top_3 = valid_data.head(3)
            bottom_3 = valid_data.tail(3).iloc[::-1]  # lowest first
            
            f.write("Top 3:\n")
            for _, row in top_3.iterrows():
                f.write(f"  {row['Player']}: {row[col]}\n")
                
            f.write("Bottom 3:\n")
            for _, row in bottom_3.iterrows():
                f.write(f"  {row['Player']}: {row[col]}\n")
            f.write("\n")
            
    print("Calculating Median, Mean, and Std Dev...")
    # Calculate for 'all'
    all_median = numeric_df.median()
    all_mean = numeric_df.mean()
    all_std = numeric_df.std()
    
    # We will build rows for results2.csv
    # Structure: 0 | all | Median1 | Mean1 | Std1 | Median2 | Mean2 | Std2 ...
    
    results2_rows = []
    
    # 'all' row
    row_all = {'Team': 'all'}
    for col in stats_cols:
        row_all[f'Median of {col}'] = all_median[col]
        row_all[f'Mean of {col}'] = all_mean[col]
        row_all[f'Std of {col}'] = all_std[col]
    results2_rows.append(row_all)
    
    # team rows
    teams = df['Club'].dropna().unique()
    team_scores = {}
    for team in teams:
        team_df = df[df['Club'] == team]
        team_numeric = team_df[stats_cols]
        
        t_median = team_numeric.median()
        t_mean = team_numeric.mean()
        t_std = team_numeric.std()
        
        row_team = {'Team': team}
        # to find best performing team, we can sum standardized means of positive stats
        score = 0
        for col in stats_cols:
            row_team[f'Median of {col}'] = t_median[col]
            row_team[f'Mean of {col}'] = t_mean[col]
            row_team[f'Std of {col}'] = t_std[col]
            
            # Simple scoring metric: normalize the mean using global mean and std
            if all_std[col] > 0 and 'Conceded' not in col and 'Missed' not in col:
                score += (t_mean[col] - all_mean[col]) / all_std[col]
            elif all_std[col] > 0: # negative stats
                score -= (t_mean[col] - all_mean[col]) / all_std[col]
        
        team_scores[team] = score
        results2_rows.append(row_team)
        
    df_results2 = pd.DataFrame(results2_rows)
    # The format required has the index as 0 for all, 1 for Team 1...
    df_results2.reset_index(drop=True, inplace=True)
    df_results2.to_csv('reports/results2.csv')
    
    best_team = max(team_scores, key=team_scores.get)
    print(f"Based on a simple z-score sum of stats, the best performing team is: {best_team}")
    
    print("Plotting histograms for each statistic...")
    # Assignment asks for "distribution of each statistic for all players in the league and each team"
    for stat in stats_cols:
        # 1. Overall Distribution
        plt.figure(figsize=(10, 6))
        # Ensure we have valid numeric data
        data_to_plot = df[stat].apply(pd.to_numeric, errors='coerce').dropna()
        if data_to_plot.empty:
            plt.close()
            continue
            
        plt.hist(data_to_plot, bins=20, alpha=0.7, color='blue', edgecolor='black')
        plt.title(f'Overall Distribution of {stat}')
        plt.xlabel(stat)
        plt.ylabel('Frequency')
        safe_stat_name = stat.replace(" ", "_").replace("/", "").replace("%", "pct").replace("#", "num")
        plt.savefig(f'reports/figures/hist_overall_{safe_stat_name}.png')
        plt.close()
        
        # 2. Team Distribution (on one plot)
        plt.figure(figsize=(15, 10))
        for team in teams:
            team_data = df[df['Club'] == team][stat].apply(pd.to_numeric, errors='coerce').dropna()
            if not team_data.empty:
                plt.hist(team_data, bins=15, alpha=0.5, label=team, density=True, histtype='step')
        
        plt.title(f'Team Comparison Distribution of {stat}')
        plt.xlabel(stat)
        plt.ylabel('Density')
        plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1.05), fontsize='small')
        plt.tight_layout()
        plt.savefig(f'reports/figures/hist_teams_{safe_stat_name}.png')
        plt.close()
        
    print(f"Histograms generated in reports/figures/")

if __name__ == "__main__":
    main()
