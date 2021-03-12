'''
ACJR Project
Scraper for profootballarchives.com. Scrapes the website for information on
starting players sorted by team and year and writes this information into a
csv file. 
'''
import re
from . import util_2
import bs4
import queue
import json
import sys
import csv
import requests
import numpy as np
import pandas as pd
from . import play_caller
import itertools
from bs4 import BeautifulSoup,Comment

YEAR=["2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020"]

def crawl_roster():
    '''
    Simultaneously crawls the given webpage for links and builds a dictionary
    of starting players at certain positions for those links.

    Output:
     roster(dict): a nested dictionary containing all info on starting players
      at certain positions for all teams and all years between 2010-2020. 
    '''
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
    Extracts players for each needed position on a webpage.

    Inputs:
     link(url)

    Returns:
     player_dict(dict)
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
        player_df = pd.DataFrame(player_list,
                                 columns=['Name', 'Position', 'GS'])
        player_dict = find_players(player_df)
        return player_dict
    else:
        return {'QB' : [None], 'RB' : [None],
                'TE' : [None], 'K' : [None], 'WR' : [None]}

def find_players(player_df):
    '''
    Sorts players in a dataframe into a dictionary with only starts from
    certain needed positions.

    Inputs:
     player_df: a pandas dataframe containing player information

    Returns:
     player_dict(dict)
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
    if player_dict['RB'] == []:
        starting_RB = player_df[player_df['Position'] == 'FB'].nlargest(1, ['GS'])
        player_dict['RB'] = starting_RB['Name'].tolist()
    if len(player_dict['QB']) == 0:
        player_dict['QB'] = [None]
    if len(player_dict['RB']) == 0:
        player_dict['RB'] = [None]
    if len(player_dict['TE']) == 0:
        player_dict['TE'] = [None]
    if len(player_dict['K']) == 0:
        player_dict['K'] = [None]
    if len(player_dict['WR']) == 0:
        player_dict['WR'] = [None]
    return player_dict

def dict_writer(dictionary):
    '''
    Writes a nested dictionary of roster information into a csv file.

    Inputs:
     dictionary(dict)
    '''
    x = pd.DataFrame.from_dict({(i, j, k): dictionary[i][j][k]
                           for i in dictionary.keys()
                           for j in dictionary[i].keys()
                           for k in dictionary[i][j].keys()},
                           orient='index', columns=['player1', 'player2', 'player3'])
    x = x.reset_index()
    x[['Name', 'Year', 'Pos']] = pd.DataFrame(x['index'].tolist(), index=x.index)
    del x['index']
    x.to_csv('rosters.csv')
    return x