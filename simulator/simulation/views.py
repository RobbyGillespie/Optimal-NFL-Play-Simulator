from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
import pandas as pd
import os

from mysite import simulator
from mysite import scraper

from .forms import FootballTeamsForm, WelcomeForm
from .models import Team

TEAM_ABBREVIATIONS = {'Browns' : 'CLE', 'Ravens' : 'BAL', 'Packers' : 'GNB', 
'Vikings' : 'MIN', 'Texans' : 'HOU', 'Chiefs' : 'KAN', 
'Seahawks' : 'SEA', 'Falcons' : 'ATL', 'Bears' : 'CHI',
'Lions' : 'DET', 'Chargers' : 'SDG', 'Bengals' : 'CIN',
'Buccaneers' : 'TAM', 'Saints' : 'NOR', 'Steelers' : 'PIT',
'Giants' : 'NYG', 'Redskins' : 'WAS', 'Eagles' : 'PHI',
'Jets' : 'NYJ', 'Bills' : 'BUF', 'Dolphins' : 'MIA', 'Patriots' : 'NWE',
'Colts' : 'IND', 'Jaguars' : 'JAX', 'Raiders' : 'OAK', 'Panthers' : 'CAR',
'Cardinals' : 'ARI', '49ers' : 'SFO', 'Cowboys' : 'DAL', 'Rams' : 'STL',
'Titans' : 'TEN', 'Broncos' : 'DEN'}
TEAM_NAMES = {'Browns': 'Cleveland Browns', 'Ravens': 'Baltimore Ravens', 'Packers': 'Green Bay Packers', 
'Vikings': 'Minnesota Vikings', 'Texans': 'Houston Texans', 'Chiefs': 'Kansas City Chiefs', 'Seahawks': 'Seattle Seahawks', 
'Falcons': 'Atlanta Falcons', 'Bears': 'Chicago Bears', 'Lions': 'Detroit Lions', 'Chargers': 'Los Angeles Chargers', 
'Bengals': 'Cincinnati Bengals', 'Buccaneers': 'Tampa Bay Buccaneers', 'Saints': 'New Orleans Saints', 
'Steelers': 'Pittsburgh Steelers', 'Giants': 'New York Giants', 'Redskins': 'Washington Football Team', 
'Eagles': 'Philadelphia Eagles', 'Jets': 'New York Jets', 'Bills': 'Buffalo Bills', 
'Dolphins': 'Miami Dolphins', 'Patriots': 'New England Patriots', 'Colts': 'Indianapolis Colts', 
'Jaguars': 'Jacksonville Jaguars', 'Raiders': 'Las Vegas Raiders', 'Panthers': 'Carolina Panthers', 
'Cardinals': 'Arizona Cardinals', '49ers': 'San Francisco 49ers', 'Cowboys': 'Dallas Cowboys', 'Rams': 'Los Angeles Rams', 
'Titans': 'Tennessee Titans', 'Broncos': 'Denver Broncos'}

def get_teams(request):
    '''
    view for the user input of two teams from specific years, when
    given a proper input it redirects to the results of the simulation
    '''
    if request.method == 'POST':
        form = FootballTeamsForm(request.POST)
        if form.is_valid(): #checks that a valid input has been given
            year1 = form.cleaned_data['year_1']
            team1 = form.cleaned_data['team_1']
            year2 = form.cleaned_data['year_2']
            team2 = form.cleaned_data['team_2']
            print(form.cleaned_data)
            t1 = Team(team_name=team1, team_year=year1)
            t2 = Team(team_name=team2, team_year=year2)
            t1.save()
            t2.save() #updates our database with team objects
            #redirects to the simulate view, with parameters of the two teams
            return HttpResponseRedirect(reverse('simulate'))
    else:
        form = FootballTeamsForm()
    return render(request, 'teams.html', {'form': form})

def simulate(request):
    '''
    view for displaying the results of a given simulation
    '''
    #get team names and years
    teams = []
    team_names = []
    for t in Team.objects.all():
        team_names.append(t.team_name)
        teams.append((TEAM_ABBREVIATIONS[t.team_name], t.team_year))
        t.delete()
    #run through the simulator with the correct team tuples of ([List of Abbreviations], Year)
    sim = simulator.simulator(teams[0], teams[1])
    #convert team names for the roster
    team1_name = TEAM_NAMES[team_names[0]]
    team2_name = TEAM_NAMES[team_names[1]]
    #get the rosters for the two teams input by the user from rosters.csv
    csv_path = os.path.join(os.path.dirname(__file__), 'rosters.csv')
    rosters_df = pd.read_csv(csv_path)
    roster1_df = rosters_df[(rosters_df['Name'] == team1_name) & (rosters_df['Year'] == teams[0][1])]
    roster2_df = rosters_df[(rosters_df['Name'] == team2_name) & (rosters_df['Year'] == teams[1][1])]
    players_positions1 = roster1_df[['player1', 'player2', 'player3', 'Pos']]
    players_positions2 = roster2_df[['player1', 'player2', 'player3', 'Pos']]
    players_positions1 = players_positions1.fillna(value='')
    players_positions2 = players_positions2.fillna(value='')
    #create dictionaries with structure {Position: Player(s)}
    roster1 = players_positions1.set_index('Pos').to_dict('index')
    roster2 = players_positions2.set_index('Pos').to_dict('index')
    #split the rosters into players, for ease in the html
    qb1, wr1, rb1, k1 = split(roster1)
    qb2, wr2, rb2, k2 = split(roster2)
    #render the list of lists output of simulator
    dct = {'team_1': teams[0], 'team_2': teams[1], 
    'simulation': sim, 'old_score_1': 0, 
    'old_score_2': 0, 'scored': False,
    'qb1': qb1, 'wr1': wr1, 'rb1': rb1, 'k1': k1,
    'qb2': qb2, 'wr2': wr2, 'rb2': rb2, 'k2': k2}
    return render(request, 'simulate.html', dct)

def welcome(request):
    '''
    view for our welcome page
    '''
    if request.method == 'POST':
        form = WelcomeForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('selection'))
        else:
            form = WelcomeForm()
    return render(request, 'welcome.html')


def split(roster):
    '''
    helper function for splitting roster dictionaries into lists of players
    '''
    qb = []
    wr = []
    rb = []
    k = []
    for position, players in roster.items():
        for key, player in players.items():
            if position == 'QB' and player != '':
                qb.append(player)
            elif position == 'WR' and player != '':
                wr.append(player)
            elif position == 'RB' and player != '':
                rb.append(player)
            elif position == 'K' and player != '':
                k.append(player)
    return (qb, wr, rb, k)

