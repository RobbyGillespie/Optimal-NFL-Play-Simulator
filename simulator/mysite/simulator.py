import statistics
import random
import datetime
import pandas as pd
import math
import os

def get_dataframes(team_1_info, team_2_info):

    team_1, team_1_year = team_1_info
    team_2, team_2_year = team_2_info

    # Get past plays dataframe
    csv_path = os.path.join(os.path.dirname(__file__), 'out.csv')
    all_plays_df = pd.read_csv(csv_path, names = ['Quarter', 'Time', 'Down', \
        'To go', 'To go category', 'Field position', 'EPC', 'Offense', \
        'Defense', 'Score difference', 'Play time', 'Field zone', \
        'Play type', 'Yards gained', 'Year'])

    # Create dataframes with each team's optimal offensive play in each scenario
    team_1, t1_optimal_plays, t1_is_offense, t2_is_defense = \
        create_optimal_plays(team_1_info, team_2_info, all_plays_df)
    team_2, t2_optimal_plays, t2_is_offense, t1_is_defense = \
        create_optimal_plays(team_2_info, team_1_info, all_plays_df)

    # Create a dataframe with all of the plays from each team in their season
    plays_df = all_plays_df[t1_is_offense | t1_is_defense | t2_is_offense | \
        t2_is_defense]

    return team_1, team_2, t1_optimal_plays, t2_optimal_plays, plays_df


def create_optimal_plays(team_A_info, team_B_info, all_plays_df):

    team_A, team_A_year = team_A_info
    team_B, team_B_year = team_B_info

    team_A_is_offense = (all_plays_df['Offense'] == team_A) & \
        (all_plays_df['Year'] == team_A_year)
    tAo_plays = all_plays_df[team_A_is_offense]
    team_B_is_defense = (all_plays_df['Defense'] == team_B) & \
        (all_plays_df['Year'] == team_B_year)
    tBd_plays = all_plays_df[team_B_is_defense]
    tAo_means = tAo_plays.groupby(['Offense', 'Down', \
        'To go category', 'Field zone', 'Play type'])['EPC'].agg(['mean', 'count'])
    tBd_means = tBd_plays.groupby(['Defense', 'Down', \
        'To go category', 'Field zone', 'Play type'])['EPC'].agg(['mean', 'count'])
    tAo_v_tBd = pd.merge(tAo_means, tBd_means, on = ['Down', 'To go category', \
        'Field zone', 'Play type'])
    sum_EPC = tAo_v_tBd['mean_x'] + tAo_v_tBd['mean_y']
    tAo_v_tBd['EPC_sum'] = sum_EPC
    sum_weighted_EPC = ((tAo_v_tBd['count_x']**2) * tAo_v_tBd['mean_x']) + \
        ((tAo_v_tBd['count_y']**2) * tAo_v_tBd['mean_y'])
    tAo_v_tBd['sum_weighted_EPC'] = sum_weighted_EPC
    tA_optimal_plays = tAo_v_tBd[tAo_v_tBd['EPC_sum'] == \
        tAo_v_tBd.groupby(['Down', 'To go category', \
        'Field zone'])['EPC_sum'].transform(max)]

    return team_A, tA_optimal_plays, team_A_is_offense, team_B_is_defense


def simulator(team_1_info, team_2_info):
    '''
    Simulates game.
    '''
    # Get dataframes and teams
    team_1, team_2, t1_optimal_plays, t2_optimal_plays, plays_df = \
        get_dataframes(team_1_info, team_2_info)

    # Coin toss
    flip = random.randint(0, 1)
    if flip == 0:
        ball_first = team_1
        offense = team_1
        defense = team_2
    else:
        ball_first = team_2
        offense = team_2
        defense = team_1

    # Initialize game-long variables
    play_tracker = []

    # Initialize game situation - skip kickoff and go to 1st and 10
    team_1_score = 0
    team_2_score = 0
    quarter = 1
    time = datetime.timedelta(minutes = 15)
    field_pos = 75
    down = 1
    to_go = 10

    while quarter <= 4:
        # Categorize yards to go and field position
        to_go_cat = categorize_to_go(to_go)
        field_pos_cat = categorize_field_pos(field_pos)

        # Run play
        if offense == team_1:
            optimal_plays_df = t1_optimal_plays
        else:
            optimal_plays_df = t2_optimal_plays
        
        yards_gained, play_time, play_type = run_play(optimal_plays_df, offense, defense, \
            quarter, down, time, to_go, to_go_cat, field_pos, field_pos_cat, team_1_score, \
            team_2_score, play_tracker, plays_df)

        # Update simulation after play
        quarter, time, to_go, field_pos, down, offense, defense, team_1_score, \
            team_2_score = update_situation(quarter, time, play_time, to_go, \
            yards_gained, down, offense, defense, team_1_score, team_2_score, \
            team_1, team_2, play_type, field_pos, ball_first)

    return play_tracker


def categorize_to_go(to_go):
    '''
    Categorizes yards to go into one of three categories.
    '''
    if to_go <= 3:
        to_go_cat = 'short'
    elif 4 <= to_go <= 7:
        to_go_cat = 'middle'
    else:
        to_go_cat = 'long'
    
    return to_go_cat


def categorize_field_pos(field_pos):
    if field_pos <= 25:
        field_zone = 'red zone'
    elif 25 < field_pos <= 50:
        field_zone = 'green zone'
    elif 50 < field_pos <= 75:
        field_zone = 'grey zone'
    elif field_pos > 75:
        field_zone = 'black zone'
    
    return field_zone


def run_play(optimal_plays_df, offense, defense, quarter, down, time, to_go, to_go_cat, 
field_pos, field_pos_cat, team_1_score, team_2_score, play_tracker, plays_df):
    
    # Get play optimal play type for current situation
    optimal_play_row = optimal_plays_df.loc[down, to_go_cat, field_pos_cat]
    optimal_play = optimal_play_row.index[0]

    # Call random play of this type using outcome from offense or defense
    team_to_use = random.randint(0, 1)
    # Use outcome from offensive play history
    if team_to_use == 0:
        same_team = plays_df['Offense'] == offense
    # Use outcome from defensive play history
    else:
        same_team = plays_df['Defense'] == defense

    # Set conditions for current situation
    same_down = plays_df['Down'] == down
    same_to_go = plays_df['To go category'] == to_go_cat
    same_field_pos = plays_df['Field zone'] == field_pos_cat
    same_play = plays_df['Play type'] == optimal_play

    # Get play outcome
    past_plays = plays_df[same_team & same_down & same_to_go & \
        same_field_pos & same_play]
    play_outcome = past_plays.iloc[random.randint(0, len(past_plays) - \
        1)]
    yards_gained = play_outcome['Yards gained']
    play_time = play_outcome['Play time']

    # Create location
    if field_pos >= 50:
        # Not sure if offense is a string or list
        location = offense + ' ' + str(100 - field_pos)
    else:
        location = defense + ' ' + str(field_pos)
    
    # Create play
    # Could also extract and add play detail
    play = [quarter, time, down, to_go, location, team_1_score, team_2_score, \
        optimal_play, yards_gained]
    play_tracker.append(play)

    return yards_gained, play_time, optimal_play


def update_situation(quarter, time, play_time, to_go, yards_gained, down, 
offense, defense, team_1_score, team_2_score, team_1, team_2, play_type,
field_pos, ball_first):
    # Update time
    play_time = datetime.timedelta(seconds = int(play_time))
    time = time - play_time
    if time.days < 0 or time.seconds == 0:
        # Halftime
        if quarter == 2:
            # Team that didn't start on offense starts second half on offense 
            if ball_first == offense:
                offense, defense, down, to_go = switch_possession(team_1, \
                    team_2, offense, defense)
                field_pos = 75
        # Next quarter
        quarter += 1
        # Simulating regular season games, so no overtime
        time = datetime.timedelta(minutes = 15)


    # Update field position and score
    # Play gained or lost yards - regular offensive play or punt
    try:
        yards_gained = int(yards_gained)
        field_pos = field_pos - yards_gained
        print(yards_gained)
        print(field_pos)
        if field_pos <= 0:
            # Touchdown
            if play_type != 'punt':
                team_1_score, team_2_score = score_change(team_1_score, \
                    team_2_score, team_1, team_2, offense, defense, 7)
            # Touchback, so switch possession and change field position
            offense, defense, down, to_go = switch_possession(team_1, team_2, offense, defense)
            field_pos = 75
        # Regular punt
        elif play_type == 'punt':
            offense, defense = switch_possession(team_1, team_2, offense, defense)
            field_pos = 100 - field_pos
        # Continue offensive drive
        else:
            to_go = to_go - yards_gained
            if to_go <= 0:
                # First down and 10 yards to go
                down = 1
                to_go = 10
                # Down and goal
                if to_go > field_pos:
                    to_go = field_pos
            else:
                down = down + 1
                # Turnover on downs
                if down == 5:
                    offense, defense, field_pos, down, to_go = \
                        turnover_on_downs(team_1, team_2, offense, defense, field_pos)

    # Play was a field goal, fumble, or interception
    except ValueError:
        # Successful field goal
        if play_type == 'field goal' and yards_gained == 'success':
            team_1_score, team_2_score = score_change(team_1_score, \
                team_2_score, team_1, team_2, offense, defense, 3)
            field_pos = 75
        # Unsuccessful field goal, fumble or interception, causing a possession change
        offense, defense, field_pos, down, to_go = turnover_on_downs(team_1, \
            team_2, offense, defense, field_pos)

    return quarter, time, to_go, field_pos, down, offense, defense, team_1_score, team_2_score


def switch_possession (team_1, team_2, offense, defense):
    if offense == team_1:
        offense = team_2
        defense = team_1
    else:
        offense = team_1
        defense = team_2

    down = 1
    to_go = 10

    return offense, defense, down, to_go


def score_change(team_1_score, team_2_score, team_1, team_2, offense, defense, points):
    if offense == team_1:
        team_1_score += points
    else:
        team_2_score += points

    return team_1_score, team_2_score


def turnover_on_downs(team_1, team_2, offense, defense, field_pos):
    offense, defense, down, to_go = switch_possession(team_1, team_2, offense, defense)
    field_pos = 100 - field_pos
    
    return offense, defense, field_pos, down, to_go