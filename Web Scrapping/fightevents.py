import requests 
from bs4 import BeautifulSoup

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

## A function to get specific fight links that hold data from each card
def UFC_Fight_Info(links): 
    fight_links =  []
    for link in links: 
        r = requests.get(link)
        soup = BeautifulSoup(r.content, 'lxml') 
        fight_links.extend([a['href'] for a in soup.find_all('a', class_='b-flag b-flag_style_green')])
        return(fight_links)

## A function to get the dates per each fight card
def UFC_Fight_Card_Date(source):
    response = requests.get(source)
    soup = BeautifulSoup(response.content, 'html.parser')
    dates = [item.text.split(':')[-1].strip() for item in soup.select('.b-list__box-list-item:nth-child(1)')]
    return dates
    '''
    date = []
    fighteventdatelist = source.find_all('span', class_='b-statistics__date')
    for fighteventdate in fighteventdatelist: 
        date.append(fighteventdate.get_text(strip = True))
    return date
    '''
## A function to look through each specific fight and scrap the 
## method, round, sig striks, kd, tds, td attempts, ect.
def UFC_Fight_Statistics(links):
    fighter1_data = []
    fighter2_data = []
    r = requests.get(links[0])
    soup = BeautifulSoup(r.content, 'lxml')
    

    details_rows = soup.select('.b-fight-details__table-body .b-fight-details__table-row')

    fighter_details = []
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
    return fighter1_data[:10] , fighter2_data[:10]


## Testing out code
links = UFC_Event_Links(soup)
dates = UFC_Fight_Card_Date(soup)
fight_links = UFC_Fight_Info(links)
fighters_stats = UFC_Fight_Statistics(fight_links)
print(fighters_stats)
