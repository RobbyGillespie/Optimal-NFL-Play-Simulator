from django.shortcuts import render
from django.http import HttpResponseRedirect

from .forms import FootballTeamsForm

def get_teams(request):
    if request.method == 'POST':
        form = FootballTeamsForm(request.POST)
        if form.is_valid():
            team1, year1, team2, year2 = form.cleaned_data
            t1 = Team(team_name=team1, team_year=year1)
            t2 = Team(team_name=team2, team_year=year2)
            return HttpResponseRedirect(reverse('simulation:simulate', args=(t1, t2,)))
    else:
        form = FootballTeamsForm()
    return render(request, 'teams.html', {'form': form})

def simulate(request, t1, t2):
    return render(request, 'simulate.html')