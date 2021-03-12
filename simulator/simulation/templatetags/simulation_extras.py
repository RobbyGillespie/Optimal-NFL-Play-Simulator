from django import template
import random

register = template.Library()

@register.simple_tag
def update_var(value):
    '''updates existing vars in template'''
    return value

@register.simple_tag
def find_player(player_list):
    player = random.randint(0, len(player_list))
    return player_list[player]