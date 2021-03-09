from django.db import models

class Team(models.Model):
    team_name = models.CharField(max_length=100)
    team_year = models.IntegerField()
