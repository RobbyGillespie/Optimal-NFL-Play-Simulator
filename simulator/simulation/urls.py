from django.urls import path
from . import views

urlpatterns = [
    path('simulation/', views.get_teams, name='team_selector'),
]