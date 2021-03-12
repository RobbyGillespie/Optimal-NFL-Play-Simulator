'''
ACJR Project
Crawler for pro-football-reference.com. Starts at the years page and crawls
through each year, and then each week within each year, to return a list of
(url, season) tuples for each game over 11 seasons.
'''

import util_2
import bs4
import scraper
import numpy as np
import pandas as pd
import csv


def get_game_pages():
    '''
    Crawl pro-football-reference to get the url for each game over 11 seasons.

    Outputs:
        game_pages: list of (game url, season) tuples for every game
    '''
    game_pages = []

    # Create soup object and get the updated url from the years page
    seasons_page, season_url = \
        create_soup_object("https://www.pro-football-reference.com/years/")
    # Find and loop through the past 11 years
    years = seasons_page.find_all("th", scope = "row")
    for year in years[0:11]:
        year_url = find_url(year, season_url)
        year_page, updated_year_url = create_soup_object(year_url)
        # Find and loop through every week of the year
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
            # For each game in a week, add its url and season to game pages
            games = week_page.find_all("td", class_="right gamelink")
            for game in games:
                game_url = find_url(game, updated_week_url)
                season = year.text
                game_pages.append((game_url, season))

    return game_pages


def combine_games():
    '''
    Write the plays from every game in the past 11 seasons to a csv.
    '''
    game_pages = get_game_pages()
    game_list = []
    for y in game_pages:
        game_log = scraper.extractor(y)
        game_list += game_log

    write_to_csv(game_list)


def write_to_csv(game_list):
    '''
    Writes to csv

    Inputs:
        game_list: list of lists with every game from every season
    '''
    with open("allgames.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(game_list)


def find_url(tag, current_url):
    '''
    Convert relative url to absolute url.

    Inputs:
        tag: relative url
        current url: absolute url

    Outputs:
        updated url: new absolute url
    '''
    relative_url = tag.find_all("a")[0]["href"]
    updated_url = util_2.convert_if_relative_url(current_url, relative_url)
    return updated_url


def create_soup_object(url):
    '''
    Create a soup object from a url.

    Inputs:
        url: absolute url

    Outputs:
        soup: soup object
        updated_url: true URL extracted from request
    '''
    request = util_2.get_request(url)
    text = util_2.read_request(request)
    updated_url = util_2.get_request_url(request)
    soup = bs4.BeautifulSoup(text, "html5lib")
    return soup, updated_url