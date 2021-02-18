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
        abs_url = util_2.convert_if_relative_url(updated_url, year_url)
        abs_request = util_2.get_request(abs_url)
        abs_text = util_2.read_request(abs_request)
        abs_updated_url = util_2.get_request_url(abs_request)
        abs_soup = bs4.BeautifulSoup(abs_text, "html5lib")

        # Method that didn't work because the listhead order is different each year
        # Over the 10 years, there are three different orders of listheads so if we
        # still can't figure something out, we can do be like for years 0-4, listheads[8],
        # for years 5-8, listheads[7], etc.
        ul = abs_soup.find_all("ul", class_="")
        weeks = None
        if years.index(year) < 3:
            weeks = ul[12].find_all("li")
        elif years.index(year) < 6:
            weeks = ul[11].find_all("li")
        else:
            weeks = ul[10].find_all("li")
        for li in weeks:
            a = li.find_all("a")[0]
            url = a["href"]
            week_url = util_2.convert_if_relative_url(abs_updated_url, url)
            print(week_url)


# General layout
# for year in tag_list:
#    for week in year:
#        for game in week: