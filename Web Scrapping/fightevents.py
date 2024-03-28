import requests 
from bs4 import BeautifulSoup
import pandas as pd

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
    data = []
    for row in source.find_all('tr'):
        link_element = row.find('a', href=True)
        date_element = row.find('span', class_='b-statistics__date')
        
        if link_element and date_element:
            link = link_element['href']
            date = date_element.get_text(strip=True)
            ## fight_links = UFC_Fight_Card_Details_Links(link)
            data.append({'Date': date, 'UFC Cards': link})
    return data


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
'''
def UFC_Fight_Statistics(links):
    fighter1_data = []
    fighter2_data = []
    r = requests.get(links[0])
    print(links[0])
    print()
    soup = BeautifulSoup(r.content, 'lxml')
    
    details_rows = soup.select('.b-fight-details__table-body .b-fight-details__table-row')


    for row in details_rows:
        cols = row.select('.b-fight-details__table-col')
        for col in cols:
            col_texts = [p.get_text(strip=True) for p in col.select('.b-fight-details__table-text')]
            if col_texts:  # Check if col_texts is not empty
                fighter1_data.append(col_texts[0])
                if len(col_texts) > 1:  # Ensure col_texts has more than one element before accessing index 1
                    fighter2_data.append(col_texts[1])
                else:
                    fighter2_data.append('')  # Append an empty string if col_texts has only one element 
                
                # Check if both arrays are of length 10, if so, return immediately
                if len(fighter1_data) == 10 and len(fighter2_data) == 10:
                    return fighter1_data, fighter2_data

    return fighter1_data[:10] , fighter2_data[:10]
'''

def UFC_Fight_Statistics(links):
    fighter_data = {'Fighter Name': [], 'Knockdowns': [], 'Significant Strikes': [], 
                    'Significant Strike Accuracy': [], 'Total Strikes': [],
                    'Takedowns': [], 'Takedown Accuracy': [], 'Submission Attempts': [],
                    'Number of Reversals': [], 'Total Control Time': []}
    
    r = requests.get(links[0])
    print(links[0])
    print()
    soup = BeautifulSoup(r.content, 'lxml')
    
    details_rows = soup.select('.b-fight-details__table-body .b-fight-details__table-row')
    row = details_rows[0]; 
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

    # Creating DataFrame from dictionary
    df = pd.DataFrame(fighter_data)
    return df

## Testing out functions
links = UFC_Event_Links(soup)
## dates = UFC_Fight_Card_Date(soup)
fight_links = UFC_Fight_Card_Details_Links('http://ufcstats.com/event-details/1a49e0670dfaca31')
print(fight_links)
print()
## info = UFC_Event_Data_Temp(soup)
## print(info)
fighters_stats = UFC_Fight_Statistics(fight_links)
print(fighters_stats)