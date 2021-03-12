"""
Columns: [Quarter, Time, Down, Yards to go, Yards to go category, Field position, EPC, Offense, Defense,
          Score difference, Time of play, Field position category, Play type, Yardage, Year]
"""
import re
import util_2
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


def team_mapper(soup):
    '''
    '''
    title_lst = soup.find("title").text.split()
    team_lst = [x for x in title_lst if x in TEAM_ABBREVIATIONS]
    teams = []
    for word in team_lst:
        teams.append(TEAM_ABBREVIATIONS[word])
    return teams, team_lst


def extractor(link_year):
    '''
    '''
    link, year = link_year
    request_obj = util_2.get_request(link)
    document = util_2.read_request(request_obj)
    soup = bs4.BeautifulSoup(document, "html5lib")
    teams, teams_lst = team_mapper(soup)
    comments = soup.find_all(text=lambda text:isinstance(text, Comment))
    for comment in comments:
        comment_soup = bs4.BeautifulSoup(comment, "html5lib")
        coin_toss = comment_soup.find("div", class_="table_container", id="div_game_info")
        if coin_toss is not None:
            coiner = coin_toss.find_all("td", {"class":"center", "data-stat":"stat"})[0].text.split()
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
        play_by_play = comment_soup.find("div", class_="table_container", id='div_pbp')
        if play_by_play != None:
            break

    game_table = scrape_rows(play_by_play, teams, teams_lst, possession, poss, year)

    return game_table


def scrape_rows(play_by, teams, teams_lst, possession, poss, year):
    '''
    '''
    master_lst = []
    possession_lst = []
    switch = teams_lst.index(poss)
    quarter_tags = play_by.find_all("th", scope="row", class_="center")
    print(teams, year, poss)
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
            epb = sub_play.nextSibling.nextSibling.nextSibling.text # epb
            epa = sub_play.nextSibling.nextSibling.nextSibling.nextSibling.text # epa
            if quarter != '':
                if epb != '' and epa != '' and len(location) > 1:
                    if current_time != '' and down != '' and togo != '':
                        sub_lst = []
                        sub_lst.append(quarter) # quarter 0
                        sub_lst.append(current_time) # time 1
                        sub_lst.append(down) # down 2
                        sub_lst.append(togo) # togo (str) 3
                        # add yds_togo_category 4
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
                            sub_lst += (str(location[0]), str(location[1])) # loc_team and loc_number 5, 6
                        else:
                            sub_lst += ['', '']

                        # extracting the play info without player names 7
                        string = ''
                        for sub in sub_play.contents:
                            if str(type(sub)) == "<class 'bs4.element.NavigableString'>":
                                string += sub
                            else:
                                string += 'pp'

                        sub_lst.append(string)

                        away_score = sub_play.nextSibling.text # away score
                        home_score = sub_play.nextSibling.nextSibling.text # home score
                        
                        if epa != '' and epb != '':
                            epc = float(epa) - float(epb) # calculate epc 8
                            sub_lst.append(str(epc))
                        sub_lst.append(teams[switch][0]) # 9 offense
                        sub_lst.append(teams[1 - switch][0]) # 10 defense

                        if away_score == '' or home_score == '': # calc score diff
                            sub_lst.append('')
                        else:
                            if switch == 0:
                                score_diff = int(away_score) - int(home_score)
                            else:
                                score_diff = int(home_score) - int(away_score)
                            sub_lst.append(str(score_diff))

                        # calculate time_of_play
                        if len(master_lst) > 0:
                            if quarter == master_lst[-1][0]: # if on same quarter as previous
                                minute_sec = current_time.split(':')
                                #if len(minute_sec) == 2:
                                total_time = datetime.timedelta(minutes = int(minute_sec[0]), seconds = int(minute_sec[1])) #convert 

                                minute_sec_prev = master_lst[-1][1].split(':')

                                total_time_prev = datetime.timedelta(minutes = int(minute_sec_prev[0]), seconds = int(minute_sec_prev[1]))# calc total time in s
                                time_of_play = (total_time_prev - total_time).seconds
                                master_lst[-1].append(str(time_of_play)) # 12 time_of_play

                            else: # case in which you are at new quarter
                                total_time = datetime.timedelta(minutes = int(minute_sec[0]), seconds = int(minute_sec[1]))
                                master_lst[-1].append(str(total_time.seconds))
                        master_lst.append(sub_lst)
                        possession_lst.append(teams[switch])
    # add final time_of_play
    if len(master_lst) <= 1:
        return([])
    else:
        master_lst[-1].append(str(total_time))

    master_lst, detail_column = add_field_position(master_lst, possession_lst)
    master_lst = play_classifier(master_lst, detail_column, year)
    return master_lst


def add_field_position(master_lst, possession_lst):
    '''
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
