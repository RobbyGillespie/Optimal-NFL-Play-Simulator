import random

def simulator(plays_df, team_1, team_2):
    '''
    Simulates game.
    '''
    # Coin toss
    flip = random.randint(0, 1)
    if flip == 0:
        possession = team_1
    else:
        possession = team_2

    # Initialize game situation
    