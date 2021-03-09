from django import forms

class FootballTeamsForm(forms.Form):
    '''
    form for taking user input for two teams with team names and years
    '''
    team_1 = forms.CharField(label="Enter Team 1 to simulate", max_length=3)
    year_1 = forms.IntegerField(label="Enter the year of Team 1", max_value = 2020, min_value=2010)
    team_2 = forms.CharField(label="Enter Team 2 to simulate", max_length=3)
    year_2 = forms.IntegerField(label="Enter the year of Team 2", max_value = 2020, min_value=2010)

class WelcomeForm(forms.Form):
    btn = forms.CharField()