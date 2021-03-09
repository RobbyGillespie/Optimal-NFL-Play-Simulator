from django.db import models

class Team(models.Model):
    '''
    model for a team with team name and year
    '''
    team_name = models.CharField(max_length=3)
    team_year = models.IntegerField()
