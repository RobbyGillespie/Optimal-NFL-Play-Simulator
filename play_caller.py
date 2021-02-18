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
    for year in years[0:10]:
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
        if years.index(year) < 5:
            weeks = ul[13].find_all("li")
        else:
            weeks = ul[11].find_all("li")
        num = len(weeks)
        week1 = weeks[0].find_all("a")[0]
        week1_url = week1["href"]
        week_urls = weeks_run(week1_url, 0, abs_updated_url, num, [])
        for url in week_urls:
            print(url)


def weeks_run(week_url, num, year_url, total, urls): ##recursive function to return the list of all week urls from a given year
    abs_week_url = util_2.convert_if_relative_url(year_url, week_url)
    week_request = util_2.get_request(abs_week_url)
    week_text = util_2.read_request(week_request)
    week_soup = bs4.BeautifulSoup(week_text, "html5lib")
    ul = week_soup.find_all("ul", class_="")
    li = ul[11].find_all("li")
    print(li)
    urls = li[num].find_all("a")
    print(urls)
    url = urls[0]["href"]
    if num == total - 1:
        abs_url = util_2.convert_if_relative_url(year_url, url)
        urls.extend(abs_url)
    else:
        num += 1
        urls.extend(weeks_run(url, num, year_url, total, urls))
    print(urls)
    return urls



# General layout
# for year in tag_list:
#    for week in year:
#        for game in week: