"""
ACJR project
Scraper for pro-football-reference.com. Takes an input from play_caller.py and
outputs a list of lists in which each element in the 15 element long sublist 
corresponds to the following columns:

Columns: [Quarter, Time, Down, Yards to go, Yards to go category, Field position,
          EPC, Offense, Defense, Score difference, Time of play, Field position 
          category, Play type, Yardage, Year]
"""
import re
from . import util_2
import bs4
import queue
import json
import sys
import csv
import requests
import numpy as np
import re
import datetime
from bs4 import BeautifulSoup,Comment


TEAM_ABBREVIATIONS = {'Browns' : ['CLE'], 'Ravens' : ['BAL', 'RAV'], 'Packers' : ['GNB'], 
                      'Vikings' : ['MIN'], 'Texans' : ['HOU', 'HTX'], 'Chiefs' : ['KAN'], 
                      'Seahawks' : ['SEA'], 'Falcons' : ['ATL'], 'Bears' : ['CHI'],
                      'Lions' : ['DET'], 'Chargers' : ['SDG', 'LAC'], 'Bengals' : ['CIN'],
                      'Buccaneers' : ['TAM'], 'Saints' : ['NOR'], 'Steelers' : ['PIT'],
                      'Giants' : ['NYG'], 'Football' : ['WAS'], 'Eagles' : ['PHI'],
                      'Jets' : ['NYJ'], 'Bills' : ['BUF'], 'Dolphins' : ['MIA'], 'Patriots' : ['NWE'],
                      'Colts' : ['IND', 'CLT'], 'Jaguars' : ['JAX'], 'Raiders' : ['OAK', 'RAI', 'LVR'], 'Panthers' : ['CAR'],
                      'Cardinals' : ['ARI', 'CRD'], '49ers' : ['SFO'], 'Cowboys' : ['DAL'], 'Rams' : ['STL', 'LAR', 'RAM'],
                      'Titans' : ['TEN', 'OTI'], 'Broncos' : ['DEN'], 'Redskins' : ['WAS']}
PASS_TYPES = {'deep left', 'deep middle', 'deep right', 'short left', 'short right', 'short middle'}


def extractor(link_year):
    '''
    Master function for this file. Designed to be called from play_caller.py,
    which provides the input. Makes the necessary calls to all the other
    functions in this file.

    Inputs:
        link_year (tuple): (link (str), year (str))
    Outputs:
        game_table (lst of lsts)
    '''
    link, year = link_year
    request_obj = util_2.get_request(link)
    document = util_2.read_request(request_obj)
    soup = bs4.BeautifulSoup(document, "html5lib")
    teams, teams_lst = team_mapper(soup)
    comments = soup.find_all(text=lambda text:isinstance(text, Comment))
    for comment in comments:
        comment_soup = bs4.BeautifulSoup(comment, "html5lib")
        # Code that searches for the coin toss and interprets the result
        # by assigning the correct possession.
        coin_toss = comment_soup.find("div", class_="table_container",
                    id="div_game_info")
        if coin_toss is not None:
            coiner = coin_toss.find_all("td", {"class":"center", 
                "data-stat":"stat"})[0].text.split()
            for word in coiner:
                if word in TEAM_ABBREVIATIONS.keys():
                    poss = word
                    possession = TEAM_ABBREVIATIONS[word]
                if word == '(deferred)':
                    for team in teams_lst:
                        if team != poss:
                            possession = TEAM_ABBREVIATIONS[team]
                            poss = team
                            break
        play_by_play = comment_soup.find("div", class_="table_container", 
                                        id='div_pbp')
        if play_by_play != None:
            break
    # With play_by_play found, construct and return the game_table.
    return scrape_rows(play_by_play, teams, teams_lst, possession, poss, year)


def team_mapper(soup):
    '''
    Takes in the soup for a pro-football-reference game page, finds the title
    and extracts the two teams that are playing.
    Input:
        soup (soup object)
    Outputs:
        teams (lst of lsts): list of two elements which are lists containing
                             the abbreviations of the two teams
        team_lst (lst): list of two elements w/ unabbreviated team names
    '''
    title_lst = soup.find("title").text.split()
    team_lst = [x for x in title_lst if x in TEAM_ABBREVIATIONS]
    teams = []
    for word in team_lst:
        teams.append(TEAM_ABBREVIATIONS[word])
    return teams, team_lst


def scrape_rows(play_by, teams, teams_lst, possession, poss, year):
    '''
    Constructs the play by play game table as a list of lists from the HTML
    containing this data.

    Input:
        play_by (BS4 object): HTML containing data to scrape
        teams (lst of lsts): list of two elements which are lists containing
                             the abbreviations of the two teams
        team_lst (lst): list of two elements w/ unabbreviated team names
        possession (str): unabbreviated name of team with possession
        poss (str): abbreviated name of team with possession
        year (str): year that the current game happened in
    Outputs:
        master_lst (lst of lsts): the full play by play
    '''
    master_lst = []
    possession_lst = []
    switch = teams_lst.index(poss)
    quarter_tags = play_by.find_all("th", scope="row", class_="center")
    for row in quarter_tags:
        if str(type(row)) == "<class 'bs4.element.Tag'>":
            variable = None
            try:
                variable = row.parent['class'][0] # success == at divider # variable is 'divider'
            except KeyError:
                variable = None
            if variable == 'divider':
                if switch == 0:
                    switch = 1
                else:
                    switch = 0
            quarter = row.text
            current_time = row.nextSibling.text
            down = row.nextSibling.nextSibling.text
            togo = row.nextSibling.nextSibling.nextSibling.text 
            location = row.nextSibling.nextSibling.nextSibling.nextSibling.text.split()
            sub_play = row.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling
            epb = sub_play.nextSibling.nextSibling.nextSibling.text
            epa = sub_play.nextSibling.nextSibling.nextSibling.nextSibling.text
            if quarter != '' and epb != '' and epa != '' and len(location) > 1 and \
                    current_time != '' and down != '' and togo != '':
                sub_lst = []
                sub_lst.append(quarter) # 0 quarter
                sub_lst.append(current_time) # 1 time
                sub_lst.append(down) # 2 down
                sub_lst.append(togo) # 3 togo (str)
                # 4 add yds_togo_category
                if  togo == '' or togo is None:
                    sub_lst.append('')
                else:
                    tg = int(togo)
                    if tg <= 3:
                        sub_lst.append('short')
                    elif 4 <= tg <= 7:
                        sub_lst.append('middle')
                    elif tg >= 8:
                        sub_lst.append('long')

                if len(location) > 1:
                    sub_lst += (str(location[0]), str(location[1])) # 5,6 loc_team and loc_number
                else:
                    sub_lst += ['', '']

                # 7 extracting the play info without player names
                string = ''
                for sub in sub_play.contents:
                    if str(type(sub)) == "<class 'bs4.element.NavigableString'>":
                        string += sub
                    else:
                        string += 'pp'
                sub_lst.append(string)
                
                if epa != '' and epb != '':
                    epc = float(epa) - float(epb) # 8 calculate epc
                    sub_lst.append(str(epc))
                
                sub_lst.append(teams[switch][0]) # 9 offense
                sub_lst.append(teams[1 - switch][0]) # 10 defense

                away_score = sub_play.nextSibling.text # away score
                home_score = sub_play.nextSibling.nextSibling.text # home score
                # calc score diff
                if away_score == '' or home_score == '': 
                    sub_lst.append('')
                else:
                    if switch == 0:
                        score_diff = int(away_score) - int(home_score)
                    else:
                        score_diff = int(home_score) - int(away_score)
                    sub_lst.append(str(score_diff))

                # calculate time_of_play
                if len(master_lst) > 0:
                    # if on same quarter as previous
                    if quarter == master_lst[-1][0]: 
                        minute_sec = current_time.split(':')
                        #if len(minute_sec) == 2:
                        total_time = datetime.timedelta(minutes = int(
                            minute_sec[0]), seconds = int(minute_sec[1]))

                        minute_sec_prev = master_lst[-1][1].split(':')
                        
                        # calc total time in s
                        total_time_prev = datetime.timedelta(minutes = int(
                            minute_sec_prev[0]), seconds = int(minute_sec_prev[1]))
                        time_of_play = (total_time_prev - total_time).seconds
                        master_lst[-1].append(str(time_of_play)) # 12 time_of_play
                    else: # case in which you are at new quarter
                        total_time = datetime.timedelta(minutes = int(
                            minute_sec[0]), seconds = int(minute_sec[1]))
                        master_lst[-1].append(str(total_time.seconds))
                master_lst.append(sub_lst)
                possession_lst.append(teams[switch])
    # add final time_of_play
    if len(master_lst) <= 1:
        return([])
    else:
        master_lst[-1].append(str(total_time.seconds))
    master_lst, detail_column = add_field_position(master_lst, possession_lst)

    return play_classifier(master_lst, detail_column, year)


def add_field_position(master_lst, possession_lst):
    '''
    Helper function for scrape_rows. Takes the master_lst scrape_rows
    is constructing, standardizes the field position, and adds a category.

    Input:
        master_lst (lst of lsts): the full play by play
        possession_lst (lst of lsts): list containing the possession at
                                    every play
    Output:
        master_lst (lst of lsts)
        detail_column (lst): play detail info
    '''
    detail_column = []
    field_position = None
    for i, row in enumerate(master_lst):
        if row[5] in possession_lst[i]:
            field_position = 100 - int(row[6])
            row[6] = str(field_position)
        field_position = int(row[6])
        # adding field_category
        if field_position is not None:
            if field_position <= 25:
                row.append('red zone')
            elif 25 < field_position <= 50:
                row.append('green zone')
            elif 50 < field_position <= 75:
                row.append('grey zone')
            elif field_position > 75:
                row.append('black zone')
        else:
            row.append('')

        detail_column.append(row[7])
        del row[7]
        del row[5]
    return master_lst, detail_column


def play_classifier(master_lst, detail_column, year):
    '''
    Classifies plays based on the play detail provided. 

    Input:
     master_lst (lst of lsts): the full play by play
     detail_column (lst): list of the detail column
      corresponding to the play by play
     year: the year of the game

     Output:
      master_lst (lst of lsts)
    '''
    for i, play in enumerate(detail_column):
        play_info = []
        try:
            play_type = re.findall('(?<=pppp )[a-z]+', play)[0]
        except IndexError:
            play_type = None
            field_goal_check = re.findall('field goal', play)
            if len(field_goal_check) > 0:
                play_info.append('field goal')
                success_check = re.findall('(?<=field goal )no good', play)
                if len(success_check) > 0:
                    play_info.append('failure')
                else:
                    play_info.append('success')
        if play_type == 'pass':
            try:
                success = re.findall('(?<=pass )[a-z]+', play)[0]
            except IndexError:
                success = None
            if success == 'complete':
                try:
                    yardage = re.findall('(?<=for )(-?[0-9]+(?=yards | yard)|no gain)', play)[0]
                except IndexError:
                    yardage = None
                if yardage == None:
                    play_info += [''] * 2
                else:
                    if yardage == 'no gain':
                        yardage = 0
                    try:
                        location = re.findall('(?<=complete )[a-z]+ [a-z]+', play)[0]
                    except IndexError:
                        location = None
                    if location in PASS_TYPES:
                        play_info.append('pass ' + location)
                        play_info.append(yardage)
                    else:
                        play_info += [''] * 2
            elif success == 'incomplete':
                yardage = '0'
                try:
                    location = re.findall('(?<=complete )[a-z]+ [a-z]+', play)[0]
                except IndexError:
                    location = None
                if location in PASS_TYPES:
                    play_info.append('pass ' + location)
                    play_info.append(str(yardage))
                else:
                    play_info += [''] * 2
            elif len(re.findall('is intercepted', play)) > 0:
                try:
                    location = re.findall('(?<=pass )[a-z]+ [a-z]+', play)[0]
                except IndexError:
                    location = None
                if location in PASS_TYPES:
                    play_info.append('pass ' + location)
                else:
                    play_info.append('')
                play_info.append('interception')
            else:
                play_info += [''] * 2
        elif play_type in {'up', 'left', 'right'}:
            if play_type == 'up':
                play_type = 'middle'
            play_info.append('run ' + play_type)
            try:
                yardage = re.findall('(?<=for )(-?[0-9]+| no gain)(?=yards | yard)', play)[0]
            except IndexError:
                yardage = None
            if yardage == None:
                play_info.append('')
            else:
                if yardage == 'no gain':
                    yardage = 0
                play_info.append(str(yardage))
        elif play_type == 'punts':
            play_info += ['punt']
            try:
                yardage = re.findall('(?<=punts )(-?[0-9]+| no gain)(?=yards | yard)', play)[0]
                return_yardage = re.findall('(?<=for )(-?[0-9]+)(?=yards | yard)', play)
                if len(return_yardage) > 0:
                    yardage = int(yardage) - int(return_yardage[0])
                play_info.append(str(yardage))
            except IndexError:
                play_info.append('')
        elif play_type == 'kicks':
            kickoff_check = re.findall('(?<=kicks )extra point', play)
            if len(kickoff_check) > 0:
                play_info.append('extra point')
                success_check = re.findall('(?<=extra point )good', play)
                if len(success_check) > 0:
                    play_info.append('success')
                else:
                    play_info.append('failure')
            else:
                play_info += [''] * 2
        else:
            if len(play_info) == 0:
                play_info += [''] * 2
        fumble_check = re.findall('fumbles', play)
        if len(fumble_check) > 0:
            recovery_check = re.findall('recovered', play)
            if len(recovery_check) == 0:
                play_info[-1] = 'fumble'
        no_play = re.findall('no play', play)
        if len(no_play) > 0:
            play_info = [''] * 2
        master_lst[i] += play_info
        master_lst[i] += [str(year)]
    return master_lst
