from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
import pandas as pd

from .forms import FootballTeamsForm, WelcomeForm
from .models import Team

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
        all_df = pd.read_csv('out.csv', names=labels)
        year1 = teams[0][1]
        year2 = teams[1][1]
        right_year = all_df['year'] == year1 or year2
        plays_df_allteams = all_df[right_year]
        team1 = teams[0][0]
        team2 = teams[1][0]
        right_team = (plays_df_allteams['offense'] == team1 or team2) or (plays_df_allteams['defense'] == team1 or team2)
        plays_df = plays_df_allteams[right_team]
    #create another dataframe for the offensive and defensive epcs
    #run csv through find_optimal_plays for dataframe of plays and best scenarios
        
    #run through simulator with the plays and scenarios and two team names

    #render the list of lists output of simulator
    return render(request, 'simulate.html', {'team_1': teams[1], 'team_2': teams[2], 'simulation': sim})

def welcome(request):
    if request.method == 'POST':
        form = WelcomeForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('selection'))
        else:
            form = WelcomeForm()
    return render(request, 'welcome.html')

