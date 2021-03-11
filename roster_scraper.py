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
from bs4 import BeautifulSoup,Comment

YEAR=["2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020"]

def crawl_roster():
    roster_pages = []
    teams_page, teams_url = play_caller.create_soup_object("https://www.profootballarchives.com/teams.html")
    teams = teams_page.find_all("a")
    for team in teams[0:32]:
        old_team_url = team["href"]
        team_url = util_2.convert_if_relative_url(teams_url, old_team_url)
        team_page, team_url = play_caller.create_soup_object(team_url)
        years = team_page.find_all("a", string=YEAR)
        for year in years:
            old_roster_url = year["href"]
            roster_url = util_2.convert_if_relative_url(team_url, old_roster_url)
            roster_pages.append(roster_url)
    return roster_pages

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
