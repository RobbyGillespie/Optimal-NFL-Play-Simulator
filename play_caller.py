# CS122: ACJR-Project
#
# Antony Awad, Cooper Powell, Johann Hatzius, Robert Gillespie

import util_2
import bs4
import scraper
import numpy as np

'''
def crawl_pages():

    game_pages = []

    starting_url  = "https://www.pro-football-reference.com/years/"
    request = util_2.get_request(starting_url)
    text = util_2.read_request(request)
    updated_url = util_2.get_request_url(request)
    soup = bs4.BeautifulSoup(text, "html5lib")
    years = soup.find_all("th", scope = "row")
    for year in years[0:11]:
        year_url = year.find_all("a")[0]["href"]
        year_url = util_2.convert_if_relative_url(updated_url, year_url)
        year_request = util_2.get_request(year_url)
        year_text = util_2.read_request(year_request)
        year_updated_url = util_2.get_request_url(year_request)
        year_soup = bs4.BeautifulSoup(year_text, "html5lib")

        ul = year_soup.find_all("ul", class_="")
        weeks = None
        if years.index(year) < 3:
            weeks = ul[12].find_all("li")
        elif years.index(year) < 6:
            weeks = ul[11].find_all("li")
        else:
            weeks = ul[10].find_all("li")
        for li in weeks:
            a = li.find_all("a")[0]
            weel_url = a["href"]
            final_week_url = util_2.convert_if_relative_url(year_updated_url, week_url)
            week_request = util_2.get_request(final_week_url)
            week_text = util_2.read_request(week_request)
            week_updated_url = util_2.get_request_url(week_request)
            week_soup = bs4.BeautifulSoup(week_text, "html5lib")
            games = week_soup.find_all("td", class_="right gamelink")
            for game in games:
                game_url = game.find_all("a")[0]["href"]
                final_game_url = util_2.convert_if_relative_url(week_updated_url, game_url)
                game_pages.apped(final_game_url)
'''

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