ACJR-project README
A directory containing the files needed to crawl, scrape, and analyze data from pro-football-reference.com and profootballarchives.com. This data is used to help simulate a football game between any two teams within the time range our data specifies. This data is presented in the format of a django website.

RUNNING THE CODE: in order to reach the right place to start the team selection and later simulation, the user must attach '/simulation' to the IP address on which the server is being hosted. From there, all other pages are linked together properly

Our code has a very specific structure to allow for django framework implementation. The framework is layed out below, with an indentation indicating a level down in the tree.

simulator
    mysite (this houses all of our functions for crawling, scraping and simulating a game)
        allgames.csv (contains the play-by-play information for every NFL game from the last 10 years)
        play_caller.py -- Given an initial link to pro-football-reference.com, crawls all the games in the years 2010-2020.
                          At each game, it calls scraper.py and incrementally constructs a master list containing all the play by plays for all the games.

        roster_scraper.py
        scraper.py -- Takes a (link, year) tuple corresponding to one game provided by play_caller.py and constructs and returns
                      a play by play of that in the format of a list of lists. Each sub list has 15 elements, one for each column.
        settings.py (django specific file with settings for our project)
        simulator.py
        urls.py (django specific file for establishing connections between our various webpages)
        util_2.py
    simulation (this houses our simulation app, where inputs are taken and a simulation is returned)
        templates (houses the html formatting for our web pages)
            simulate.html (formatting for the table output of our simulation)
            teams.html (formatting for the user input form)
            welcome.html (formatting for the welcome page)
        templatetags (a file used by django to create custom functions for use in the template html)
            simulation_extras.py (this includes the functions get_name, find_player, and update_var)
        apps.py (where we configured the app for use in the project)
        forms.py (the user input form is created with drop down menus for teams and int for year)
        models.py (houses the Team model, which we use to keep inputs in the database)
        rosters.csv (contains the roster of every team for the last 10 years. in simulation because it is called by views.py)
        urls.py (as above, links together the urls of our webpages)
        views.py (this contains the bulk of the work of our django program. The functions on this page, get_teams, simulate, and welcome, as well as the helper function split, are used to create the data to fill the html templates we provide in templates)
    db.sqlite3 (this is our database, which holds the two teams input by the user)