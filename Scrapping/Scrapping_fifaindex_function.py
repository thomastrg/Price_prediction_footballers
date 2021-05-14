# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests

import re
import pandas as pd


def scrapp_fifa_index(page_start=1, page_end=2):
    
    assert page_start >= 1
    assert page_end >= page_start
    
    all_data = []
    url_base ="https://www.fifaindex.com"
    
    #Wanted description informations
    wanted = ['Age','Valeur','Salaire']
    
    url = f'https://www.fifaindex.com/fr/players/fifa19/?page={page_start}'
    
    while(page_start <= page_end and requests.get(url).status_code == 200):
        
        main_page = requests.get(url).content
        main_page_html = BeautifulSoup(main_page, 'html.parser')

        players_soup = main_page_html.find_all('a', class_='link-player')
        players = {player['href'] for player in players_soup}

        for player in players:
            data_dict = {}
            
            page_html = requests.get(url_base+player).content #go to player's page and retrieve content
            soup = BeautifulSoup(page_html,'html.parser')
            
            #Get the player's name
            result = soup.find('div', class_='card mb-5').find('h5', class_='card-header').get_text()
            player_name = re.split(r'(\d+)', result)[0]
            data_dict['Name'] = player_name
            
            # Get the player's description
            result = soup.find('div', class_='card-body')
            description = result.get_text()
            description_data = re.split(r'\n+', description)
            
            for elm in description_data:
                if any(word in elm for word in wanted):
                    temp = re.split(r'([\d\.]+)', elm)
                    temp[1] = temp[1].replace('.','')
                    temp[0] = re.sub(r'\s+$','', temp[0]).replace(r'\s+',' ')
                    temp[0] = re.sub(r'\s+',' ', temp[0])
                    data_dict[temp[0]] = int(temp[1])
                
            
            # Get player's stats
            result = soup.find_all('div', class_='col-12 col-md-4 item')
            first_text = [elm.get_text() for elm in result]
            data = [re.split(r'\n+', sub_text) for sub_text in first_text]
            for sub_data in data:
                for attribute in sub_data :
                    if bool(re.search(r'\d', attribute)): 
                        temp = re.split(r' (\d+)', attribute)
                        data_dict[temp[0]] = int(re.search('(\d+)$', attribute).group(1))
                        
            # Add player data to our main list
            all_data.append(data_dict)
            
        # Go to the next page
        page_start += 1
        url = f'https://www.fifaindex.com/fr/players/fifa19/?page={page_start}'
    
    #RETURN THE FINAL LIST
    return all_data


if __name__ =="__main__":
    data = scrapp_fifa_index(1, 10)

    columns_names = ['Name', 'Age', 'Value €', 'Value $', 'Value £', 'Wage €', 'Wage $',
        'Wage £', 'Ball Control', 'Dribbling', 'Marking', 'Slide Tackle',
        'Stand Tackle', 'Aggression', 'Reactions', 'Att. Position',
        'Interceptions', 'Vision', 'Composure', 'Crossing', 'Short Pass',
        'Long pass', 'Acceleration', 'Stamina', 'Strength', 'Balance',
        'Sprint Speed', 'Agility', 'Jumping', 'Heading', 'Shot Power', 'Finishing',
        'Long Shots', 'Curve', 'FK Acc.', 'Penalties', 'Volleys',
        'GK Positioning', 'GK Diving', 'GK Handling', 'GK Kicking', 'GK Reflexes']

    df = pd.DataFrame(data)
    df.columns = columns_names
    df.to_csv('fifaindex_21.csv', index=False)
