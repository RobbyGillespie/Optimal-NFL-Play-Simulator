OVERVIEW:
This is a directory containing all of the files needed to crawl, scrape, and analyze data from pro-football-reference.com and profootballarchives.com. The data is used to simulate an NFL game between any two NFL teams within from the 2010-2020 seasons if each team had the "optimal play" called on every down. The program uses NFL play-by-play data from the past 11 seasons to determine what each team's best offensive play type would be given situational factors like field position, down, quarter, etc. The simulation then assumes that play is called and randomly outputs a real-life outcome from when that play was called either for the offense or against the defense during their seasons. The program continues to call the optimal play and simulate the subsequent game conditions until the game ends, theoretically outputting a play-by-play simulaiton of the teams if play-calling were perfect.

FOOTBALL ANALYSIS SPECIFICS:


A directory containing the files needed to crawl, scrape, and analyze data from pro-football-reference.com and profootballarchives.com. This data is used to help simulate a football game between any two NFL teams within the past 11 seasons (dating back to the 2010-2011 season). This data is presented in the format of a django website. The purpose of this project is to determine which of two teams would win an NFL game if they had the optimal play called for them in each situation throughout the game. We used past NFL data to figure out what each team's best offensive play type would be against the other team chosen for the simulation, then used random outcomes from when those plays were called for the offense or against the defense in real life. The django website displays our approximation of how a game would play out between the two given teams if they called the plays that are most likely to score them points each drive down the field.

RUNNING THE CODE:
To run the server, make sure you are in the simulator directory, then run "python3 manage.py runserver". If you recieve some kind of error that the port is already in use, running python3 manage.py runserver 8001 should do the trick. After running the server, go to the IP address the port was set to on your web page.
In order to reach the right place to start the team selection and later simulation, the user must attach '/simulation' to the IP address on which the server is being hosted. From there, all other pages are linked together properly.

The code has a very specific structure to allow for django framework implementation. The framework is layed out below, with an indentation indicating a level down in the tree.

simulator
    mysite -- Directory that houses all of our functions for crawling, scraping and simulating a game.
        allgames.csv -- Contains the play-by-play information for every NFL game from the last 10 years.

        play_caller.py -- Given an initial link to the pro-football-reference.com seasons homepage, crawls all the games in the years 2010-2020. At each game, it calls scraper.py and incrementally constructs a master list containing containing every play from every game, writing them to allgames.csv.

        roster_scraper.py -- Scrapes profootballarchives.com for information on starting players sorted by team and year and 
        writes this information into a csv file. 

        scraper.py -- Takes a (link, year) tuple corresponding to one game provided by play_caller.py and constructs and returns a play by play in the format of a list of lists. Each sub list has 15 elements, one for each column.
        settings.py (django specific file with settings for our project)

        simulator.py -- Takes two teams and a season for each, then returns the play-by-play of a simulated game based on the successes and failures of their plays in the given season assigned to them. The play-by-play is a list of lists with elements corresponding to each information about the play.

        urls.py -- Django specific file for establishing connections between our various webpages.

        util_2.py -- File containing helper functions such as get_request and read_request for the BS4 inside the scrapers.

    simulation -- App Directory that houses our simulation app, where inputs are taken and a simulation is returned.
        templates -- Houses the html formatting for our web pages.

            simulate.html -- Formatting for the table output of our simulation.

            teams.html -- Formatting for the user input form.

            welcome.html -- Formatting for the welcome page.

        templatetags -- A file used by django to create custom functions for use in the template html.
            simulation_extras.py -- This includes the functions get_name, find_player, and update_var.

        apps.py -- Where we configured the app for use in the project.

        forms.py -- The user input form is created with drop down menus for teams and int for year.

        models.py -- Houses the Team model, which we use to keep inputs in the database.

        rosters.csv -- Contains the roster of every team for the last 10 years. in simulation because it is called by views.py.

        urls.py -- As above, links together the urls of our webpages.

        views.py -- This contains the bulk of the work of our django program. The functions on this page, get_teams, simulate, 
        and welcome, as well as the helper function split, are used to create the data to fill the html templates we provide in templates.
        
    db.sqlite3 -- This is our database, which holds the two teams input by the user, and then deletes them after being used in views.simulate(), to not affect the next input.
    manage.py -- helper functions for working with the server, migrating, and running it
