import requests
from bs4 import BeautifulSoup

url = "http://www.betmma.tips/mma_betting_favorites_vs_underdogs.php?Org=1"
page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')

# Function to get the dates along with the hyper links of each ufc events along with the odds 
def UFC_Odds_Event_Links(source): 
    fighteventlists = source.find_all('tr')
    fighteventoddslinksinfo = []
    for row in fighteventlists: 
        cols = row.find_all('td')
        if len(cols) >= 2:
            date = cols[0].text.strip()
            event_link = cols[1].find('a')
            if event_link:
                event_link = event_link['href']
                fighteventoddslinksinfo.append({'date': date, 'event_link': event_link})
    return fighteventoddslinksinfo

## def UFC_Odds_Fighter_Info(source): 


event_info = UFC_Odds_Event_Links(soup)
for event in event_info: 
    print("Date", event['date'])
    print("Event Link", event['event_link'])
    print()