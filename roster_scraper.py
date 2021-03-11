'''
'''
import re
import util_2
import bs4
import queue
import json
import sys
import csv
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup,Comment

def extractor(link):
    '''
    '''
    request_obj = util_2.get_request(link)
    document = util_2.read_request(request_obj)
    soup = bs4.BeautifulSoup(document, "html5lib")
    table = soup.find_all('table')
    player_table = table[5].find_all('tr')
    player_list = []
    for a in player_table[2:]:
        player_info = a.contents
        player_list.append([player_info[1].text, player_info[2].text,
                            int(player_info[8].text)])
    player_df = pd.DataFrame(player_list, columns=['Name', 'Position', 'GS'])
    return player_df

def find_players(link):
    '''
    '''
    player_df = extractor(link)
    player_dict = {}
    starting_QB = player_df[player_df['Position'] == 'QB'].max()
    starting_RB = player_df[player_df['Position'] == 'RB'].max()
    starting_TE = player_df[player_df['Position'] == 'TE'].max()
    WR_df = player_df[player_df['Position'] == 'WR']
    starting_WR = WR_df.nlargest(3, ['GS'])
    player_dict['QB'] = starting_QB['Name']
    player_dict['RB'] = starting_RB['Name']
    player_dict['TE'] = starting_TE['Name']
    player_dict['WR'] = starting_WR['Name'].tolist()
    return player_dict
