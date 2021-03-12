from django import template
import random

register = template.Library()

@register.simple_tag
def update_var(value):
    '''updates existing vars in template'''
    return value

@register.simple_tag
def find_player(player_list):
    '''returns a random player for the specific positions'''
    player = random.randint(0, len(player_list) - 1)
    return player_list[player]

@register.simple_tag
def get_name(tup):
    '''gets the team name from a Team tuple'''
    return tup[0]

@register.simple_tag
def first_higher(first, second):
    '''returns true if the first value is larger than the second'''
    return first > second