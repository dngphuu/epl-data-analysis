import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import os
import time

def scrape_transfermarkt_values():
    base_url = "https://www.transfermarkt.co.uk"
    league_url = f"{base_url}/premier-league/startseite/wettbewerb/GB1"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    
    print("Fetching club URLs from Transfermarkt...")
    player_values = {}
    
    try:
        response = requests.get(league_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        club_links = set()
        for a in soup.select('div.box table.items tbody tr td.hauptlink a'):
            href = a.get('href')
            if href and 'spielplan' not in href:
                club_links.add(href)
                
        # Some links might be wrong, ensure we have about 20 clubs
        # Format usually /club-name/startseite/verein/123/saison_id/2024
        club_urls = [link for link in club_links if '/startseite/verein/' in link]
        if not club_urls:
            # Fallback to another selector if layout changed
            for a in soup.select('table.items tbody tr td:nth-child(2) a'):
                href = a.get('href')
                if href and '/startseite/verein/' in href:
                    club_urls.append(href)
        
        club_urls = list(set(club_urls))
        print(f"Found {len(club_urls)} clubs to scrape.")
        
        for club in club_urls:
            club_url = f"{base_url}{club}"
            print(f"Scraping club: {club_url}")
            c_resp = requests.get(club_url, headers=headers, timeout=10)
            c_soup = BeautifulSoup(c_resp.text, 'html.parser')
            
            # Players table
            table = c_soup.find('table', {'class': 'items'})
            if table:
                rows = table.find('tbody').find_all('tr', recursive=False)
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) > 3:
                        # Name is usually in a td with class 'hauptlink' inside the player info section
                        name_td = row.select_one('td.hauptlink a')
                        if name_td:
                            player_name = name_td.text.strip()
                        else:
                            continue
                            
                        val_td = row.find('td', class_='rechts hauptlink')
                        if val_td:
                            val_str = val_td.text.strip().replace('€', '').replace('m', 'm').replace('k', 'k')
                            player_values[player_name] = val_str
                            
            time.sleep(1) # gentle to the server
            
    except Exception as e:
        print(f"Exception during scraping: {e}")
            
    print(f"Scraped {len(player_values)} player values.")
    return player_values

def convert_value(val_str):
    if not isinstance(val_str, str):
        return None
    val_str = val_str.replace('€', '').strip()
    if 'm' in val_str:
        return float(val_str.replace('m', '')) * 1000000
    elif 'k' in val_str:
        return float(val_str.replace('k', '')) * 1000
    return None

def main():
    os.makedirs('data/processed', exist_ok=True)
    
    # 1. Load the three datasets
    print("Loading datasets...")
    df_main = pd.read_csv('data/raw/epl_player_stats_24_25.csv')
    df_fbref = pd.read_csv('data/raw/fbref_PL_2024-25.csv')
    df_db = pd.read_csv('data/raw/database.csv')
    
    # 2. Aggregate SCA and GCA from database.csv
    print("Aggregating SCA and GCA from database.csv...")
    df_actions = df_db.groupby('Player')[['Shot-Creating Actions', 'Goal-Creating Actions']].sum().reset_index()
    df_actions.rename(columns={'Shot-Creating Actions': 'SCA', 'Goal-Creating Actions': 'GCA'}, inplace=True)
    
    # 3. Clean fbref data to extract xG and xAG
    print("Extracting xG, xAG from fbref...")
    df_fbref = df_fbref[['Player', 'xG', 'xAG']].copy()
    df_fbref = df_fbref.groupby('Player')[['xG', 'xAG']].sum().reset_index()
    
    # 4. Merge datasets
    print("Merging datasets...")
    if 'Player Name' in df_main.columns:
        df_main.rename(columns={'Player Name': 'Player'}, inplace=True)
        
    df_merged = pd.merge(df_main, df_fbref, on='Player', how='left')
    df_merged = pd.merge(df_merged, df_actions, on='Player', how='left')
    
    # 5. Scrape transfermarkt per club
    tm_values = scrape_transfermarkt_values()
    df_tm = pd.DataFrame(list(tm_values.items()), columns=['Player', 'TransferValue_Str'])
    df_tm['TransferValue_EUR'] = df_tm['TransferValue_Str'].apply(convert_value)
    
    def match_names(name, names_list):
        from difflib import get_close_matches
        matches = get_close_matches(name, names_list, n=1, cutoff=0.7)
        return matches[0] if matches else name
        
    tm_players = df_tm['Player'].tolist()
    if tm_players:
        print("Matching player names with Transfermarkt...")
        df_merged['TM_Player_Match'] = df_merged['Player'].apply(lambda x: match_names(x, tm_players) if pd.notna(x) else x)
        df_merged = pd.merge(df_merged, df_tm, left_on='TM_Player_Match', right_on='Player', how='left', suffixes=('', '_tm'))
        if 'Player_tm' in df_merged.columns:
            df_merged.drop(columns=['Player_tm'], inplace=True)
    
    # Save the final dataset
    output_path = 'data/processed/merged_epl_24_25.csv'
    df_merged.to_csv(output_path, index=False)
    print(f"Data preparation complete. Final dataset saved to {output_path}")

if __name__ == "__main__":
    main()
