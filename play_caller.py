# CS122: ACJR-Project
#
# Antony Awad, Cooper Powell, Johann Hatzius, Robert Gillespie

import util_2
import bs4
import scraper
import numpy as np
import pandas as pd


def get_game_pages():
    game_pages = []
    seasons_page, season_url = create_soup_object("https://www.pro-football-reference.com/years/")
    years = seasons_page.find_all("th", scope = "row")
    for year in years[0:11]:
        year_url = find_url(year, season_url)
        year_page, updated_year_url = create_soup_object(year_url)
        ul = year_page.find_all("ul", class_="")
        weeks = None
        if years.index(year) < 3:
            weeks = ul[12].find_all("li")
        elif years.index(year) < 6:
            weeks = ul[11].find_all("li")
        else:
            weeks = ul[10].find_all("li")
        for li in weeks:
            week_url = find_url(li, updated_year_url)
            week_page, updated_week_url = create_soup_object(week_url)
            games = week_page.find_all("td", class_="right gamelink")
            for game in games:
                game_url = find_url(game, updated_week_url)
                season = year.text
                game_pages.append((game_url, season))
    return game_pages

def combine_games():
    for year in range(2010, 2021):
        game_pages = get_game_pages()
        season_game_pages = [x[0] for x in game_pages if x[1] == str(year)]
        game_list = []
        for y in season_game_pages:
            game_log = scraper.extractor(y, year)
            game_list += game_log
    write_to_csv(game_list)

    return game_list
    '''
    df = pd.DataFrame(game_list, columns = ['Quarter', 'Time', 'Down', \
        'To go', 'Field position', 'Away score', 'Home score', \
        'EPB', 'EPA', 'Team?', 'Play type', 'Direction', 'Yards gained'])
    '''

def write_to_csv(list):
    with open("out.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(list)

def find_url(tag, current_url):
    relative_url = tag.find_all("a")[0]["href"]
    updated_url = util_2.convert_if_relative_url(current_url, relative_url)
    return updated_url

def create_soup_object(url):
    request = util_2.get_request(url)
    text = util_2.read_request(request)
    updated_url = util_2.get_request_url(request)
    soup = bs4.BeautifulSoup(text, "html5lib")
    return soup, updated_url

def find_optimal_play(df, quarter, down, to_go, field_position, score_diff):
    same_quarter = df['Quarter'] == quarter
    same_down = df['Down'] == down
    same_to_go = find_yard_range(df['To go']) == find_yard_range(to_go)
    same_field_position = 0
    same_score_diff = 0
    similar_plays = df[same_quarter & same_down & same_to_go & \
        same_field_position & same_score_diff]
    similar_plays_grouped = similar_plays.groupby['Play type'].size()

    

def find_yard_range(yards_to_go):
    if yards_to_go in range(0, 4):
        return 'Short'
    elif yards_to_go in range(4, 7):
        return 'Medium'
    else:
        return 'Long'

def find_position_range(field_position):
    x

def find_score_diff_range(score_diff):
    x