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
                game_pages.append(game_url)
    return game_pages

def combine_games():
    game_pages = get_game_pages()
    all_games = scraper.extractor(game_pages[0])
    for url in game_pages[1:]:
        game = scraper.extractor(url)
        all_games = np.concatenate((all_games, game), axis=0)
    return all_games

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


def create_pandas_df(master_array):
    df = pd.DataFrame(master_array, columns = ['Quarter', 'Time', 'Down', \
        'To go', 'Field position', 'Away score', 'Home score', \
        'EPB', 'EPA' 'Team?', 'Play type', 'Direction', 'Yards gained'])


def find_optimal_play(df, quarter, down, to_go, field_position, score_diff):
    same_quarter = df['Quarter'] == quarter
    same_down = df['Down'] == down
    same_to_go = find_yard_range(df['To go']) == find_yard_range(to_go)
    same_field_position = 
    same_score_diff = 
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