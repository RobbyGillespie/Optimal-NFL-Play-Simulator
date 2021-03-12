from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
import pandas as pd
import os

#from simulator.py import simulator, get_optimal_plays

from .forms import FootballTeamsForm, WelcomeForm
from .models import Team

TEAM_NAMES: {'Browns': 'Cleveland Browns', 'Ravens': 'Baltimore Ravens', 'Packers': 'Green Bay Packers', 
'Vikings': 'Minnesota Vikings', 'Texans': 'Houston Texans', 'Chiefs': 'Kansas City Chiefs', 'Seahawks': 'Seattle Seahawks', 
'Falcons': 'Atlanta Falcons', 'Bears': 'Chicago Bears', 'Lions': 'Detroit Lions', 'Chargers': 'Los Angeles Chargers', 
'Bengals': 'Cincinnati Bengals', 'Buccaneers': 'Tampa Bay Buccaneers', 'Saints': 'New Orleans Saints', 
'Steelers': 'Pittsburgh Steelers', 'Giants': 'New York Giants', 'Football': 'Washington Football Team', 
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
    for t in Team.objects.all():
        teams.append((t.team_name, t.team_year))
    #get correct data from the csv for these years
    labels = ['quarter', 'time', 'down', 'togo', 
    'togo_cat', 'position', 'epc', 'offense',
    'defense', 'score_difference', 'time_of_play',
    'field_position_cat', 'play_type', 'yardage', 'year']
    workpath = os.path.dirname(os.path.abspath(__file__))
    all_df = pd.read_csv(os.path.join(workpath, 'out.csv'), names=labels)
    year1 = teams[0][1]
    year2 = teams[1][1]
    right_year = all_df['year'] == year1 or year2
    plays_df_allteams = all_df[right_year]
    team1 = teams[0][0]
    team2 = teams[1][0]
    right_team = (plays_df_allteams['offense'] == team1 or team2) or (plays_df_allteams['defense'] == team1 or team2)
    plays_df = plays_df_allteams[right_team]
    #get optimal plays from simulator.py
    #optimal_plays_df = get_optimal_plays()
    #run through simulator with the plays and scenarios and two team names
    #sim = simulator(plays_df, optimal_plays_df, teams[0], teams[1])
    #convert team names for the roster
    team1_name = TEAM_NAMES[team1]
    team2_name = TEAM_NAMES[team2]
    #get the rosters for the two teams input by the user from rosters.csv
    rosters_df = pd.read_csv('rosters.csv')
    roster1_df = rosters_df[(rosters_df['Name'] == team1_name) & (rosters_df['Year'] == year1)]
    roster2_df = rosters_df[(rosters_df['Name'] == team2_name) & (rosters_df['Year'] == year2)]
    players_positions1 = roster1_df[['player1', 'player2', 'player3', 'Pos']]
    players_positions2 = roster2_df[['player1', 'player2', 'player3', 'Pos']]
    roster1 = players_positions1.set_index('Pos').to_dict('index')
    roster2 = players_positions2.set_index('Pos').to_dict('index')
    print(roster1)
    print(roster2)
    #render the list of lists output of simulator
    dct = {'team_1': teams[0], 'team_2': teams[1], 
    'simulation': sim, 'roster_1': roster1, 
    'roster_2': roster2, 'old_score_1': 0, 
    'old_score_2': 0, 'scored': False}
    return render(request, 'simulate.html', dct)

def welcome(request):
    if request.method == 'POST':
        form = WelcomeForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('selection'))
        else:
            form = WelcomeForm()
    return render(request, 'welcome.html')

