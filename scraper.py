"""
<tr ><th scope="row" class="center " data-stat="quarter" >1</th><td class="center " data-stat="qtr_time_remain" ><a href="#pbp_41.000">15:00</a></td><td class="center iz" data-stat="down" ></td><td class="center iz" data-stat="yds_to_go" ></td><td class="left " data-stat="location" csk="35" >KAN 35</td><td class="left " data-stat="detail" ><a name="pbp_41.000"></a><a href="/players/B/ButkHa00.htm">Harrison Butker</a> kicks off 68 yards, returned by <a href="/players/M/MickJa01.htm">Jaydon Mickens</a> for 26 yards (tackle by <a href="/players/O/ODanDo00.htm">Dorian O'Daniel</a>)</td><td class="right iz" data-stat="pbp_score_aw" >0</td><td class="right iz" data-stat="pbp_score_hm" >0</td><td class="right " data-stat="exp_pts_before" >0.000</td><td class="right " data-stat="exp_pts_after" >0.480</td></tr>

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
from bs4 import BeautifulSoup,Comment

TEAM_ABBREVIATIONS = {'Browns' : ['CLE'], 'Ravens' : ['BAL', 'RAV'], 'Packers' : ['GNB'], 
                      'Vikings' : ['MIN'], 'Texans' : ['HOU', 'HTX'], 'Chiefs' : ['KAN'], 
                      'Seahawks' : ['SEA'], 'Falcons' : ['ATL'], 'Bears' : ['CHI'],
                      'Lions' : ['DET'], 'Chargers' : ['SDG', 'LAC'], 'Bengals' : ['CIN'],
                      'Buccaneers' : ['TAM'], 'Saints' : ['NOR'], 'Steelers' : ['PIT'],
                      'Giants' : ['NYG'], 'Football Team' : ['WAS'], 'Eagles' : ['PHI'],
                      'Jets' : ['NYJ'], 'Bills' : ['BUF'], 'Dolphins' : ['MIA'], 'Patriots' : ['NWE'],
                      'Colts' : ['IND', 'CLT'], 'Jaguars' : ['JAX'], 'Raiders' : ['OAK', 'RAI', 'LVR'], 'Panthers' : ['CAR'],
                      'Cardinals' : ['ARI', 'CRD'], '49ers' : ['SFO'], 'Cowboys' : ['DAL'], 'Rams' : ['STL', 'LAR', 'RAM'],
                      'Titans' : ['TEN', 'OTI'], 'Broncos' : ['DEN'], 'Redskins' : ['WAS']}
PASS_TYPES = {'deep left', 'deep middle', 'deep right', 'short left', 'short right', 'short middle'}

def team_mapper(soup):
    title_lst = soup.find("title").text.split()
    team_lst = [x for x in title_lst if x in TEAM_ABBREVIATIONS]
    teams = []
    for word in team_lst:
        teams.append(TEAM_ABBREVIATIONS[word])
    return teams

def extractor(link):
    request_obj = util_2.get_request(link)
    document = util_2.read_request(request_obj)
    soup = bs4.BeautifulSoup(document, "html5lib")
    teams = team_mapper(soup)

    comments = soup.find_all(text=lambda text:isinstance(text, Comment))

    for comment in comments:
        comment_soup = bs4.BeautifulSoup(comment, "html5lib")
        coin_toss = comment_soup.find("div", class_="table_container", id="div_game_info")
        if coin_toss is not None:
            coiner = coin_toss.find_all("td", {"class":"center", "data-stat":"stat"})[0].text.split()
            for word in coiner:
                if word in teams:
                    possession = word
                if word == '(deferred)':
                    for team in teams:
                        if team is not word:
                            possession = team

        #<td class="center" data-stat="stat">Chiefs (deferred)</td>
        play_by_play = comment_soup.find("div", class_="table_container", id='div_pbp')
        if play_by_play is not None:
            break

    game_table = scrape_rows(play_by_play, teams, possession)

    return game_table

def scrape_rows(play_by, teams, possession):
    master_lst = []
    possession_lst = []
    switch = teams.index(possession)
    quarter_tags = play_by.find_all("th", scope="row", class_="center")
    for row in quarter_tags:
        if str(type(row)) == "<class 'bs4.element.Tag'>":
            sub_lst = []

            sub_lst.append(row.text) # quarter
            sub_lst.append(row.nextSibling.text) # time
            sub_lst.append(row.nextSibling.nextSibling.text) # down
            sub_lst.append(row.nextSibling.nextSibling.nextSibling.text) # togo
            location = row.nextSibling.nextSibling.nextSibling.nextSibling.text.split()
            if len(location) > 1:
                sub_lst += (str(location[0]), str(location[1])) # loc_team and loc_number
            else:
                sub_lst += ['', '']

            # extracting the play info without player names
            sub_play = row.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling
            string = ''
            for sub in sub_play.contents:
                if str(type(sub)) == "<class 'bs4.element.NavigableString'>":
                    string += sub
                else:
                    string += 'pp'

            sub_lst.append(string)

            sub_lst.append(sub_play.nextSibling.text) # away score
            sub_lst.append(sub_play.nextSibling.nextSibling.text) # home score
            sub_lst.append(sub_play.nextSibling.nextSibling.nextSibling.text) # epb
            sub_lst.append(sub_play.nextSibling.nextSibling.nextSibling.nextSibling.text) # epa

            try:
                variable = row.parent['class']
            except KeyError:
                variable = []
            if variable is not None:
                if switch == 0:
                    switch = 1
                else:
                    switch = 0
            else:
                sub_lst.append(teams[switch])
                #print("at divider")

            master_lst.append(sub_lst)
        possession_lst.append(teams[switch])
    
    master_array = np.array(master_lst)
    possession_array = np.array([possession_lst])
    possession_array = np.transpose(possession_array)
    master_array = np.concatenate((master_array, possession_array), axis=1)
    print(master_array[0, :])
    master_array = add_field_position(master_array)
    master_array = play_classifier(master_array)
    return master_array

    #return len(quarter_lst), len(times_lst), len(downs_lst), len(togo_lst)

def add_field_position(numpy_array):
    for row in numpy_array:
        if row[4] in row[11]:
            field_position = 100 - int(row[5][0])
            row[5] = str(field_position)
    return numpy_array


def play_classifier(numpy_array):

    detail_column = numpy_array[:, 6]
    numpy_array = np.delete(numpy_array, [4, 9], 1)

    play_classify = []
    for play in detail_column:
        play_info = []
        try:
            play_type = re.findall('(?<=pppp )[a-z]+', play)[0] #find a way to handle special cases
        except IndexError:
            play_type = None
        if play_type == 'pass':
            play_info.append('pass')
            try:
                success = re.findall('(?<=pass )[a-z]+', play)[0]
            except IndexError:
                success = None
            if success == 'complete':
                try:
                    yardage = re.findall('(?<=for )[0-9]+(?=( yard| yards)| no gain)', play)[0]
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
                        play_info.append(location)
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
                    play_info.append(location)
                    play_info.append(str(yardage))
                else:
                    play_info += [''] * 2
            else:
                play_info += [''] * 2
        elif play_type in {'up', 'left', 'right'}:
            play_info.append('run')
            if play_type == 'up':
                play_type = 'middle'
            play_info.append(play_type)
            try:
                yardage = re.findall('(?<=for )[0-9]+(?= (yard|yards)|no gain)', play)[0]
            except IndexError:
                yardage = None
            if yardage == None:
                play_info.append('')
            else:
                if yardage == 'no gain':
                    yardage = 0
                play_info.append(str(yardage))
        else:
            play_info += [''] * 3
        no_play = re.findall('no play', play)
        if no_play != []:
            play_info = [''] * 3
        play_classify.append(play_info)

    detail_array = np.array(play_classify)
    master_array = np.concatenate([numpy_array, detail_array], axis=1)
    return master_array

#<td class="left " data-stat="location" csk="77" >TAM 23</td>
'''
for comment in comments:
    comment_soup = bs4.BeautifulSoup(comment, "html5lib")
    main_title = comment_soup.find("div", class_="table_container", id='div_php')
    comment = BeautifulSoup(str(comment), 'html.parser')

    search_play = comment.find('table', {'id':'pbp'})
'''

#<div class="table_container" id="div_pbp">
#<tr ><th scope="row" class="center " data-stat="quarter" >1</th><td class="center " data-stat="qtr_time_remain" ><a href="#pbp_63.000">14:56</a></td><td class="center " data-stat="down" >1</td><td class="center " data-stat="yds_to_go" >10</td><td class="left " data-stat="location" csk="77" >TAM 23</td><td class="left " data-stat="detail" ><a name="pbp_63.000"></a><a href="/players/B/BradTo00.htm">Tom Brady</a> pass complete short left to <a href="/players/G/GodwCh00.htm">Chris Godwin</a> for 1 yard (tackle by <a href="/players/B/BreeBa00.htm">Bashaud Breeland</a>)</td><td class="right iz" data-stat="pbp_score_aw" >0</td><td class="right iz" data-stat="pbp_score_hm" >0</td><td class="right " data-stat="exp_pts_before" >0.480</td><td class="right " data-stat="exp_pts_after" >0.070</td></tr>


