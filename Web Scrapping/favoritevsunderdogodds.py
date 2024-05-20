import requests
from bs4 import BeautifulSoup
import pandas as pd
import re


url = "http://www.betmma.tips/mma_betting_favorites_vs_underdogs.php?Org=1"
page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')

def UFC_Event_Links(source):
    fighteventlists = source.find_all('tr')
    fighteventoddslinks = []
    seen_links = set()  # To keep track of seen links
    for row in fighteventlists:
        cols = row.find_all('td')
        if len(cols) >= 2:
            event_link = cols[1].find('a')
            if event_link:
                event_link = event_link['href']
                if 'php?Event' in event_link and event_link not in seen_links:
                    fighteventoddslinks.append('https://www.betmma.tips/' + event_link)
                    seen_links.add(event_link)  # Add the link to the set
    return fighteventoddslinks

def scrape_fight_info(link):
    r = requests.get(link)
    soup = BeautifulSoup(r.content, 'lxml')
    tables = soup.find_all('table')
    
    fight_info_list = []
    seen_names = set()  # Keep track of seen fighter names
    
    # Extract event title
    event_title = soup.find('td', bgcolor="#F7F7F7").find('h1').text.strip()

    for table in tables:
        # Extract fighter names
        fighters = [a.text.strip() for a in table.find_all('a', href=lambda href: href and 'fighter_profile.php' in href)]
        
        # Ensure the number of fighters is even
        if len(fighters) % 2 != 0:
            fighters.pop()  # Remove the last fighter
        
        # Pair up the fighters
        fighter_pairs = [(fighters[i], fighters[i+1]) for i in range(0, len(fighters), 2)]

        # Extract odds
        odds_td = table.find_all('td', bgcolor=lambda color: color in ["#A2FC98", "#FB6A6D"])
        odds_a_b = []
        for odds in odds_td:
            odds_text = odds.get_text(strip=True)
            match = re.search(r'@([\d.]+)', odds_text)
            if match:
                odds_a_b.append(match.group(1))
            else:
                odds_a_b.append(None)  # If no match found, append None
        
        # Filter out None values before extracting odds for Fighter A and Fighter B
        odds_a = []
        for odds in odds_a_b[::2]:
            if odds is not None:
                odds_a.append(float(odds))
                break
        
        odds_b = []
        for odds in odds_a_b[1::2]:
            if odds is not None:
                odds_b.append(float(odds))
                break
        
        # Determine the winner based on color
        winners = []
        for odds in odds_td:
            if odds.get('bgcolor') == '#A2FC98':
                winners.append('Fighter A')  # Fighter A is the winner
            else:
                winners.append('Fighter B')  # Fighter B is the winner

        for (fighter_a, fighter_b), winner in zip(fighter_pairs, winners):
            # Check if either fighter is a duplicate
            if fighter_a in seen_names or fighter_b in seen_names:
                break  # Break from loop if a duplicate is found
            else:
                fight_info_list.append({'Event Title': event_title, 'Fighter A': fighter_a, 'Fighter B': fighter_b, 'Winner': fighter_a if winner == 'Fighter A' else fighter_b, 'Odds A': odds_a, 'Odds B': odds_b})
                seen_names.add(fighter_a)  # Add fighter A to seen names
                seen_names.add(fighter_b)  # Add fighter B to seen names

    return pd.DataFrame(fight_info_list)


def scrape_all_fight_info():
    # Get UFC event links
    fighteventoddslinks = UFC_Event_Links(soup)

    # Scrape fight info for each link
    all_fight_info = []
    for link in fighteventoddslinks:
        fight_info = scrape_fight_info(link)
        all_fight_info.append(fight_info)

    # Concatenate all fight info into one DataFrame
    all_fight_info_df = pd.concat(all_fight_info, ignore_index=True)

    return all_fight_info_df

# Example usage
info = scrape_fight_info("https://www.betmma.tips/mma_event_betting_history.php?Event=173")
info

## all_fight_event_odds_data = scrape_all_fight_info()
## all_fight_event_odds_data