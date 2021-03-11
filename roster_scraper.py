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
import play_caller
import itertools
from bs4 import BeautifulSoup,Comment

YEAR=["2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020"]

def crawl_roster():
    rosters = {}
    teams_page, teams_url = play_caller.create_soup_object("https://www.profootballarchives.com/teams.html")
    teams = teams_page.find_all("a")
    for team in teams[8:40]:
        rosters[team.text] = {}
        old_team_url = team["href"]
        team_url = util_2.convert_if_relative_url(teams_url, old_team_url)
        team_page, team_url = play_caller.create_soup_object(team_url)
        years = team_page.find_all("a", string=YEAR)
        for year in years:
            old_roster_url = year["href"]
            roster_url = util_2.convert_if_relative_url(team_url, old_roster_url)
            rosters[team.text][year.text] = extractor(roster_url)
    return rosters

def extractor(link):
    '''
    '''
    request_obj = util_2.get_request(link)
    document = util_2.read_request(request_obj)
    soup = bs4.BeautifulSoup(document, "html5lib")
    table = soup.find_all('table')
    player_list = []
    player_table = None
    for x in table:
        a = x.find_all('tr')
        if len(a) > 0:
            if a[0].text == 'ROSTER':
                player_table = a
    if player_table != None:
        for a in player_table[2:]:
            player_info = a.contents
            player_list.append([player_info[1].text, player_info[2].text,
                                int(player_info[8].text)])
        player_df = pd.DataFrame(player_list, columns=['Name', 'Position', 'GS'])
        player_dict = find_players(player_df)
        return player_dict
    else:
        return {'QB' : None, 'RB' : None, 'TE' : None, 'WR' : None}

def find_players(player_df):
    '''
    '''
    player_dict = {}
    starting_QB = player_df[player_df['Position'] == 'QB'].nlargest(1, ['GS'])
    starting_RB = player_df[player_df['Position'] == 'RB'].nlargest(1, ['GS'])
    starting_TE = player_df[player_df['Position'] == 'TE'].nlargest(1, ['GS'])
    starting_K = player_df[player_df['Position'] == 'K'].nlargest(1, ['GS'])
    starting_WR = player_df[player_df['Position'] == 'WR'].nlargest(3, ['GS'])
    player_dict['QB'] = starting_QB['Name'].tolist()
    player_dict['RB'] = starting_RB['Name'].tolist()
    player_dict['TE'] = starting_TE['Name'].tolist()
    player_dict['K'] = starting_K['Name'].tolist()
    player_dict['WR'] = starting_WR['Name'].tolist()
    return player_dict

def dict_writer(dictionary):
    '''
    '''
    with open('dict.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    for key, value in dictionary.items():
       writer.writerow([key, value])

'''
    w = csv.DictWriter(sys.stdout, ['years'] + YEAR)
    for key,val in sorted(dictionary.items()):
        row = {'years': key}
        row.update(val)
        w.writerow(row)
'''