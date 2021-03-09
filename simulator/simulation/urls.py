from django.urls import path
from . import views

'''
urlpattern for the two pages in simulation: the input page, and simulation page
'''
urlpatterns = [
    path('simulation/', views.welcome, name='welcome'), #starting page
    path('simulation/selection', views.get_teams, name='selection'), #pattern for input page
    path('simulation/simulate', views.simulate, name='simulate'), #pattern for the simulation page
]