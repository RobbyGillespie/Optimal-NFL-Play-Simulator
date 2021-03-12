from django import template
import random

register = template.Library()

@register.simple_tag
def update_var(value):
    '''updates existing vars in template'''
    return value

@register.simple_tag
def cut_play_type(play_type):
    '''cuts the play type to determine a play subtype'''
    return play_type

@register.simple_tag
def find_player(player_list):
    '''returns a random player for the specific positions'''
    player = random.randint(0, len(player_list) - 1)
    return player_list[player]

@register.simple_tag
def pass_output(yards_gained):
    '''outputs a string based on yardage for passes'''
    if yards_gained == 'fumble':
        return 'fumbled by'
    elif yards_gained == 'interception':
        return 'intercepted, intended for'
    elif yards_gained == '0':
        return 'incomplete to'
    elif yards_gained == '1':
        return 'for 1 yard to'
    else:
        return 'for ' + str(yards_gained) + ' yards to'

@register.simple_tag
def run_output(yards_gained):
    '''outputs a string based on yardage for runs'''
    if yards_gained == 'fumble':
        return 'fumbled'
    elif yards_gained == '1':
        return 'for 1 yard'
    else:
        return 'for ' + str(yards_gained) + ' yards'

@register.simple_tag
def get_name(tup):
    '''gets the team name from a Team tuple'''
    return tup[0]