from django import forms

TEAMS = [('Browns', 'Browns'), ('Ravens', 'Ravens'), ('Packers', 'Packers'), 
('Vikings', 'Vikings'), ('Texans', 'Texans'), ('Chiefs', 'Chiefs'), ('Seahawks', 'Seahawks'), 
('Falcons', 'Falcons'), ('Bears', 'Bears'), ('Lions', 'Lions'), ('Chargers', 'Chargers'), 
('Bengals', 'Bengals'), ('Buccaneers', 'Buccaneers'), ('Saints', 'Saints'), 
('Steelers', 'Steelers'), ('Giants', 'Giants'), ('Redskins', 'Redskins'), 
('Eagles', 'Eagles'), ('Jets', 'Jets'), ('Bills', 'Bills'), 
('Dolphins', 'Dolphins'), ('Patriots', 'Patriots'), ('Colts', 'Colts'), 
('Jaguars', 'Jaguars'), ('Raiders', 'Raiders'), ('Panthers', 'Panthers'), 
('Cardinals', 'Cardinals'), ('49ers', '49ers'), ('Cowboys', 'Cowboys'), ('Rams', 'Rams'), 
('Titans', 'Titans'), ('Broncos', 'Broncos')]
class FootballTeamsForm(forms.Form):
    '''
    form for taking user input for two teams with team names and years
    '''
    team_1 = forms.ChoiceField(label="Enter Team 1 to simulate", choices=TEAMS)
    year_1 = forms.IntegerField(label="Enter the year of Team 1", max_value = 2020, min_value=2010)
    team_2 = forms.ChoiceField(label="Enter Team 2 to simulate", choices=TEAMS)
    year_2 = forms.IntegerField(label="Enter the year of Team 2", max_value = 2020, min_value=2010)

class WelcomeForm(forms.Form):
    '''
    form for a button that takes the user to the simulation page
    '''
    btn = forms.CharField()