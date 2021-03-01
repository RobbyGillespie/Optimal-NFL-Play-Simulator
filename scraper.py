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
from bs4 import BeautifulSoup,Comment

TEAM_ABBREVIATIONS = {'Browns' : ['CLE'], 'Ravens' : ['BAL'], 'Packers' : ['GNB'], 
                      'Vikings' : ['MIN'], 'Texans' : ['HOU'], 'Chiefs' : ['KAN'], 
                      'Seahawks' : ['SEA'], 'Falcons' : ['ATL'], 'Bears' : ['CHI'],
                      'Lions' : ['DET'], 'Chargers' : ['SDG', 'LAC'], 'Bengals' : ['CIN'],
                      'Buccaneers' : ['TAM'], 'Saints' : ['NOR'], 'Steelers' : ['PIT'],
                      'Giants' : ['NYG'], 'Football Team' : ['WAS'], 'Eagles' : ['PHI'],
                      'Jets' : ['NYJ'], 'Bills' : ['BUF'], 'Dolphins' : ['MIA'], 'Patriots' : ['NWE'],
                      'Colts' : ['IND'], 'Jaguars' : ['JAX'], 'Raiders' : ['OAK', 'RAI'], 'Panthers' : ['CAR'],
                      'Cardinals' : ['ARI'], '49ers' : ['SFO'], 'Cowboys' : ['DAL'], 'Rams' : ['STL', 'LAR'],
                      'Titans' : ['TEN'], 'Broncos' : ['DEN']}


def extractor():
    link="https://www.pro-football-reference.com/boxscores/202102070tam.htm"
    request_obj = util_2.get_request(link)
    document = util_2.read_request(request_obj)
    soup = bs4.BeautifulSoup(document, "html5lib")

    title_lst = soup.find("title").text.split()
    teams = []
    for word in title_lst:
        if word in TEAM_ABBREVIATIONS.keys():
            teams.append(word)

    comments = soup.find_all(text=lambda text:isinstance(text, Comment))

    for comment in comments:
        comment_soup = bs4.BeautifulSoup(comment, "html5lib")
        coin_toss = comment_soup.find("div", class_="table_container", id="div_game_info")
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

    return play_by_play, possession

def scrape_one_row(play_by, teams):
    master_lst = []
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
                sub_lst += ([location[0]], [location[1]]) # loc_team and loc_number
            else:
                sub_lst += ['', '']

            # extracting the play info without player names
            sub_play = row.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling
            string = ''
            for sub in sub_play.contents:
                if str(type(sub)) == "<class 'bs4.element.NavigableString'>":
                    string += sub
                else:
                    string += '!??!'

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
            sub_lst.append(teams[switch])
                #print("at divider")

            master_lst.append(sub_lst)
        else:
            print("test")
    
    return len(master_lst)

    #return len(quarter_lst), len(times_lst), len(downs_lst), len(togo_lst)

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
