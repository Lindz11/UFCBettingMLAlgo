import requests 
from bs4 import BeautifulSoup
import pandas as pd
import re
baseurl = 'http://ufcstats.com/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}
r = requests.get('http://ufcstats.com/statistics/events/completed?page=all')
soup = BeautifulSoup(r.content, 'lxml')


## A function to pull and keep all of the hyperlinks to every known UFC event
def UFC_Event_Links(source): 
    fighteventlist = source.find_all('tr', class_='b-statistics__table-row')
    fighteventlinks = []
    ## Loop through fight event links and search for hrefs in css code
    for fightevent in fighteventlist:
        for link in fightevent.find_all('a', href=True):
            fighteventlinks.append(link['href'])
    return fighteventlinks

def UFC_Event_Data_Temp(source): 
    all_data = pd.DataFrame()
    rows = source.find_all('tr')
    
    for row in rows:
        img_element = row.find('img', src="http://1e49bc5171d173577ecd-1323f4090557a33db01577564f60846c.r80.cf1.rackcdn.com/next.png")
        if img_element:
            continue  # Skip this row if it contains the specific image tag
        
        link_element = row.find('a', href=True)
        date_element = row.find('span', class_='b-statistics__date')
        
        if link_element and date_element:
            link = link_element['href']
            date = date_element.get_text(strip=True)
            fight_links = UFC_Fight_Card_Details_Links(link)
            
            for fight in fight_links: 
                df = pd.DataFrame(UFC_Fight_Statistics(fight))
                df.insert(0, 'Date', date)
                df.insert(1, 'UFC Cards', link)
                all_data = pd.concat([all_data, df], ignore_index=True)
    
    return all_data


## A function to get specific fight links that hold data from each card 
## and make sure there are no duplicates or uneeded data
def UFC_Fight_Card_Details_Links(link): 
    fight_links = []
    r = requests.get(link)
    soup = BeautifulSoup(r.content, 'html.parser') 
    links = []
    for row in soup.find_all('tr', class_='b-fight-details__table-row'):
        link_attr = row.get('data-link')
        if link_attr:
            links.append(link_attr)

    return links

## A function to get the dates per each fight card
def UFC_Fight_Card_Date(source):
    date = []
    fighteventdatelist = source.find_all('span', class_='b-statistics__date')
    for fighteventdate in fighteventdatelist: 
        date.append(fighteventdate.get_text(strip = True))
    return date


## A function to look through each specific fight and scrap the 
## sig striks, kd, tds, td attempts, ect.
def UFC_Fight_Statistics(link):
    fighter_data = {
        'Fighter Name': [], 'Knockdowns': [], 'Significant Strikes': [], 
        'Significant Strike Accuracy': [], 'Total Strikes': [],
        'Takedowns': [], 'Takedown Accuracy': [], 'Submission Attempts': [],
        'Number of Reversals': [], 'Total Control Time': []
    }
    
    r = requests.get(link)
    soup = BeautifulSoup(r.content, 'lxml')
    
    details_rows = soup.select('.b-fight-details__table-body .b-fight-details__table-row')
    for row in details_rows:
        cols = row.select('.b-fight-details__table-col')
        for i, col in enumerate(cols):
            col_texts = [p.get_text(strip=True) for p in col.select('.b-fight-details__table-text')]
            if col_texts:
                fighter_data[list(fighter_data.keys())[i]].append(col_texts[0])
                if len(col_texts) > 1:
                    fighter_data[list(fighter_data.keys())[i]].append(col_texts[1])
                else:
                    fighter_data[list(fighter_data.keys())[i]].append('')
    
    # Ensure all arrays have the same length by appending empty strings if necessary
    max_length = max(len(data) for data in fighter_data.values())
    for key in fighter_data:
        fighter_data[key] += [''] * (max_length - len(fighter_data[key]))
    
    # Creating DataFrame from the dictionary
    df = pd.DataFrame(fighter_data)
    
    # Splitting 'Significant Strikes' into 'Significant Strikes Landed' and 'Significant Strikes Attempted'
    if 'Significant Strikes' in df.columns:
        significant_strikes = df['Significant Strikes'].str.split(' of ', expand=True)
        
        def safe_int_conversion(x):
            try:
                return int(x)
            except (ValueError, TypeError):
                return 0
        
        df['Significant Strikes Landed'] = significant_strikes[0].apply(safe_int_conversion)
        df['Significant Strikes Attempted'] = significant_strikes[1].apply(safe_int_conversion)
        df.drop(columns=['Significant Strikes'], inplace=True)
    
    # Splitting 'Total Strikes' into 'Total Strikes Landed' and 'Total Strikes Attempted'
    if 'Total Strikes' in df.columns:
        total_strikes = df['Total Strikes'].str.split(' of ', expand=True)
        
        df['Total Strikes Landed'] = total_strikes[0].apply(safe_int_conversion)
        df['Total Strikes Attempted'] = total_strikes[1].apply(safe_int_conversion)
        df.drop(columns=['Total Strikes'], inplace=True)
    
    # Keep only the first two rows
    df = df.head(2)
    
    return df

def UFC_Fight_Info(link): 
    r = requests.get(link)
    soup = BeautifulSoup(r.content, 'lxml')
    # Parse the HTML

    # Extracting data
    title = soup.select_one('.b-fight-details__fight-title').get_text(strip=True)
    method = soup.select_one('.b-fight-details__text-item_first').get_text(strip=True).split(':')[-1].strip()
    round = soup.select('.b-fight-details__text-item')[1].get_text(strip=True)
    time = soup.select('.b-fight-details__text-item')[2].get_text(strip=True).split(':')[-1].strip()
    referee = soup.select_one('.b-fight-details__label:-soup-contains("Referee") + span').get_text(strip=True)
    details = soup.select('.b-fight-details__text-item')[4:]

    # Extracting judges' names and scores
    judge_names = []
    judge_scores = []
    for item in details:
        name = item.find("span").get_text(strip=True)
        score = item.get_text(strip=True).split(':')[-1].strip()  # Corrected extraction logic
        score = re.sub(re.escape(name), "", score)
        judge_names.append(name)
        judge_scores.append(score)

    # Creating DataFrame
    data = {
        'Title': title,
        'Method': method,
        'Round': round,
        'Time': time,
        'Referee': referee,
    }
    
    # Add judge names and scores as separate columns
    for i in range(3):  # Assuming there are always 3 judges
        data[f'Judge {i+1} Name'] = judge_names[i]
        data[f'Judge {i+1} Score'] = judge_scores[i]

    # Create DataFrame
    df = pd.DataFrame(data, index=[0])
    
    return df

    
fight_info = UFC_Fight_Statistics('http://ufcstats.com/fight-details/894c44c3d04aaf6f');
print(fight_info)
## Testing out functions
## links = UFC_Event_Links(soup)
## dates = UFC_Fight_Card_Date(soup)
## fight_links = UFC_Fight_Card_Details_Links('http://ufcstats.com/event-details/1a49e0670dfaca31')
## print(fight_links)
## print()
## info = UFC_Event_Data_Temp(soup)
## print(info)
## fighters_stats = UFC_Fight_Statistics('http://ufcstats.com/fight-details/323f543eb8abdb36')
## print(fighters_stats)