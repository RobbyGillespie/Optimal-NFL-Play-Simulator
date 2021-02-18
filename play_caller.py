import util_2
import bs4
def crawl_pages():
    # Import modules

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