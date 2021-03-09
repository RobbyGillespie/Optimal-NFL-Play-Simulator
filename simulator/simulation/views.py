from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
import csv

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
            team1, year1, team2, year2 = form.cleaned_data
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
        team = t.get()
        teams.append((team.team_name, team.team_year))
    #get correct csv files for these years

    #run csv through find_optimal_plays for dataframe of plays and best scenarios

    #run through simulator with the plays and scenarios and two team names

    return render(request, 'simulate.html') #render the list of lists output of simulator

def welcome(request):
    if request.method == 'POST':
        form = WelcomeForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('selection'))
        else:
            form = WelcomeForm()
    return render(request, 'welcome.html')

