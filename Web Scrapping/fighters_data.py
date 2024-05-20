import requests
from bs4 import BeautifulSoup
import string
import pandas as pd
import re
import os

url = "http://ufcstats.com/statistics/fighters?char=a&page=all"
page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')

def UCF_Fighter_Links():
    all_hrefs = set()

    # Loop through all characters in the alphabet and collect fighter links
    for char in string.ascii_lowercase:
        url = f"http://ufcstats.com/statistics/fighters?char={char}&page=all"
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            fighter_links = soup.find_all('a', class_='b-link_style_black')
            hrefs = set(link['href'] for link in fighter_links)
            all_hrefs.update(hrefs)
        else:
            print(f"Failed to fetch data for character '{char}'")

    return all_hrefs


def UFC_Fighter_Info(fighter_link):
    # Make request to the URL
    page = requests.get(fighter_link)
    soup = BeautifulSoup(page.content, 'html.parser')
    list_items = soup.find_all("li", class_="b-list__box-list-item")
    
    # Extract name
    name_element = soup.find('span', class_='b-content__title-highlight')
    name = name_element.get_text(strip=True) if name_element else None

    # Initialize an empty dictionary to store the information
    info_dict = {}

    # Iterate through each <li> element and extract the information
    for item in list_items:
        # Extract the title and value
        title = item.find("i").get_text(strip=True).replace(":", "")
        value = item.get_text(strip=True, separator=" ").replace(title, "", 1).strip()

        # Clean the value
        clean_value = re.sub(r'[,/]|(lbs\.)', '', value)
        clean_value = re.sub(r'\\', '', clean_value).replace(":", "")
        
        # Store the value in the dictionary
        info_dict[title] = clean_value

    # Insert name into the dictionary
    info_dict['name'] = name

    # Create a DataFrame from the dictionary
    df = pd.DataFrame([info_dict])

    # Reorder columns to have "name" at the start
    df = df[['name'] + [col for col in df.columns if col != 'name']]

    # Rename columns
    column_names_mapping = {
        'Height': 'height',
        'Weight': 'weight',
        'Reach': 'reach',
        'Stance': 'stance',
        'DOB': 'date_of_birth',
        'SLpM': 'SLPM',
        'Str. Acc.': 'Str Acc',
        'SApM': 'SApm',
        'TD Avg.': 'TD Avg',
        'TD Acc.': 'TD Acc',
        'TD Def.': 'TD Def',
        'Sub. Avg.': 'Sub Avg'
    }
    df = df.rename(columns=column_names_mapping)

    return df
 

def UCF_Fighter_DataFrame_Info(links):
    all_data = pd.DataFrame()
    for link in links:
        df = UFC_Fighter_Info(link)
        all_data = pd.concat([all_data, df], ignore_index=True)

    return all_data

info = UFC_Fighter_Info('http://ufcstats.com/fighter-details/792be9a24df82ed6')
info
## links = UCF_Fighter_Links()
## Call the function to get the DataFrame
## all_data = UCF_Fighter_DataFrame_Info(links)
## all_data