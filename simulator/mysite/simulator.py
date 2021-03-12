'''
ACJR Project
Simulate an entire game between two teams, each representing an NFL team in a
single season. So, teams from two different seasons can play each other. This
simulation is meant to demonstrate what would happen if each team were to call
the best play possible in each scenario, not just choose the play they
would have most likely run themselves. We seek to know who would win if each
team had the best play-calling possible, not the play calling they actually had.

The simulated plays are determined by finding the best play type (pass deep left,
run middle, etc.) based on how often the team ran the play (if they ran it more
often it is better) and how good the outcomes were (measured by the increase in
the points the team was expected to score after the play). From there, we call the
play and randomly choose an outcome from when the offense ran that play or the
defense defended against that play in the past. We then update the situation
and continue simulating until the end of the game.
'''

import statistics
import random
import datetime
import pandas as pd
import math
import os

def get_dataframes(team_1_info, team_2_info):
    '''
    Create dataframes with all relevant past plays and the optimal play type 
    for each team.

    Inputs:
        team_1_info (tuple): team 1 abbreviation and season of interest
        team_2_info (tuple): team 1 abbreviation and season of interest

    Outputs:
        team_1 (string): team 1 abbreviation
        team_2 (string): team 2 abbreviation
        t1_optimal_plays: dataframe with team 1's optimal play per scenario
        t2_optimal_plays: dataframe with team 2's optimal play per scenario
        plays_df: dataframe of past plays where each team is on offense or
            defense during their season
    '''

    # Get dataframe of every play in the last 11 seasons
    csv_path = os.path.join(os.path.dirname(__file__), 'allgames.csv')
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
    '''
    Create a dataframe with the optimal offensive play for a team on offense
    against another team on defense.

    Inputs:
        team_A_info (tuple): team 1 abbreviation and season of interest
        team_B_info (tuple): team 1 abbreviation and season of interest
        all_plays_df: dataframe of every play in the last 11 seasons

    Outputs:
        team_A (string): team A abbreviation
        tA_optimal_plays: dataframe of team A's best plays vs team B's defense
        team_A_is_offense: column of booleans that are True where Team A is off
        team_B_is_defense: column of booleans that are True where Team B is off
    '''

    # Load in team information
    team_A, team_A_year = team_A_info
    team_B, team_B_year = team_B_info

    # Create dataframes of team A's offensive plays and team B's defensive plays
    team_A_is_offense = (all_plays_df['Offense'] == team_A) & \
        (all_plays_df['Year'] == team_A_year)
    tAo_plays = all_plays_df[team_A_is_offense]
    team_B_is_defense = (all_plays_df['Defense'] == team_B) & \
        (all_plays_df['Year'] == team_B_year)
    tBd_plays = all_plays_df[team_B_is_defense]

    # Create a column for the mean EPC per play type in each scenario for each
    # team, as well as the count of each play type per scenario, then merge
    tAo_means = tAo_plays.groupby(['Offense', 'Down', \
        'To go category', 'Field zone', 'Play type'])['EPC'].agg(['mean', 'count'])
    tBd_means = tBd_plays.groupby(['Defense', 'Down', \
        'To go category', 'Field zone', 'Play type'])['EPC'].agg(['mean', 'count'])
    tAo_v_tBd = pd.merge(tAo_means, tBd_means, on = ['Down', 'To go category', \
        'Field zone', 'Play type'])
    
    # Create a column for the sum of each team's EPC, weighted by how often
    # that play was run, and make the optimal play the one with the highest val
    sum_weighted_EPC = ((tAo_v_tBd['count_x']**2) * tAo_v_tBd['mean_x']) + \
        ((tAo_v_tBd['count_y']**2) * tAo_v_tBd['mean_y'])
    tAo_v_tBd['sum_weighted_EPC'] = sum_weighted_EPC
    tA_optimal_plays = tAo_v_tBd[tAo_v_tBd['sum_weighted_EPC'] == \
        tAo_v_tBd.groupby(['Down', 'To go category', \
        'Field zone'])['sum_weighted_EPC'].transform(max)]

    return team_A, tA_optimal_plays, team_A_is_offense, team_B_is_defense


def simulator(team_1_info, team_2_info):
    '''
    Simulates game from coin toss to the end of the fourth quarter.

    Inputs:
        team_1_info (string): team 1 abbreviation
        team_2_info (string): team 2 abbreviation

    Outputs:
        play_tracker: list of each play throughout the game
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

    # Initialize game-long variable
    play_tracker = []

    # Initialize game situation - skip kickoff and go to 1st and 10
    team_1_score = 0
    team_2_score = 0
    quarter = 1
    time = datetime.timedelta(minutes = 15)
    field_pos = 75
    down = 1
    to_go = 10

    # Play until the fourth quarter ends
    while quarter <= 4:
        # Categorize yards to go and field position
        to_go_cat = categorize_to_go(to_go)
        field_pos_cat = categorize_field_pos(field_pos)

        # Run play
        if offense == team_1:
            optimal_plays_df = t1_optimal_plays
        else:
            optimal_plays_df = t2_optimal_plays
        
        yards_gained, play_time, play_type, play_tracker = run_play(optimal_plays_df, offense, defense, \
            quarter, down, time, to_go, to_go_cat, field_pos, field_pos_cat, team_1_score, \
            team_2_score, play_tracker, plays_df)

        # Update simulation after play
        quarter, time, to_go, field_pos, down, offense, defense, team_1_score, \
            team_2_score = update_situation(quarter, time, play_time, to_go, \
            yards_gained, down, offense, defense, team_1_score, team_2_score, \
            team_1, team_2, play_type, field_pos, ball_first, play_tracker)

    return play_tracker


def categorize_to_go(to_go):
    '''
    Categorize yards to go into one of three categories.

    Inputs:
        to_go (int): yards until a first down
    
    Outputs:
        to_go_cat (string): category of yards to go
    '''
    if to_go <= 3:
        to_go_cat = 'short'
    elif 4 <= to_go <= 7:
        to_go_cat = 'middle'
    else:
        to_go_cat = 'long'
    
    return to_go_cat


def categorize_field_pos(field_pos):
    '''
    Categorize field position into four different zones.

    Inputs:
        field_pos (int): offense's distance from a touchdown

    Outputs:
        field_zone (string): field position category
    '''
    if field_pos <= 25:
        field_zone = 'red zone'
    elif 25 < field_pos <= 50:
        field_zone = 'green zone'
    elif 50 < field_pos <= 75:
        field_zone = 'grey zone'
    elif field_pos > 75:
        field_zone = 'black zone'
    
    return field_zone


def run_play(optimal_plays_df, offense, defense, quarter, down, time, to_go,
to_go_cat, field_pos, field_pos_cat, team_1_score, team_2_score, play_tracker,
plays_df):
    '''
    Simulate a play from the offense or defense's past plays in their
    respective season, chosen based on the optimal play type.

    Inputs:
        optimal_plays_df: dataframe of optimal play per situation
        offense (string): team currently on offense
        defense (string): team currently on defense
        quarter (int): one of four quarters of the game
        down (int): one of four downs
        time: datetime object representing the number of minutes and seconds
            left in the quarter
        to_go (int): number of yards to go until a first down or touchdown
        to_go_cat (string): category of yards to go
        field_pos (int): yards until the offense reaches a touchdown
        field_pos_cat (string): category of field position
        team_1_score (int): team 1's total points in the game
        team_2_score (int): team 2's total points in the game
        play_tracker: list of plays previously ran
        play_df: dataframe of each team's past plays in their respective season

    Outputs:
        yards_gained: number of yards on a play, or the success/failure of a
            field goal
        play_time (int): the number of seconds the play took
        optimal_play: the best play choice in the given scenario
        play_tracker: list of plays previously ran
    '''
    
    # Get play optimal play type for current situation
    try:
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

        # Find plays in this situation from offensie or defensie play history
        past_plays = plays_df[same_team & same_down & same_to_go & \
            same_field_pos & same_play]
    
    # A team did not encounter this situation all season, so find all plays
    # that were a pass or run.
    except KeyError:
        past_plays = plays_df[(plays_df['Play type'].str.contains('pass')) | \
            (plays_df['Play type'].str.contains('run'))]

    # Choose random play outcome from the previous plays of the same play type
    play_outcome = past_plays.iloc[random.randint(0, len(past_plays) - \
        1)]
    optimal_play = play_outcome['Play type']
    yards_gained = play_outcome['Yards gained']
    play_time = play_outcome['Play time']

    # If there was no value for yards gained, the offense gained 0 yards
    if type(yards_gained) is float:
        yards_gained = 0

    # Create location
    if field_pos >= 50:
        location = offense + ' ' + str(100 - field_pos)
    else:
        location = defense + ' ' + str(field_pos)

    # Create play
    play = [quarter, time, down, to_go, location, optimal_play, yards_gained, \
        offense]
    play_tracker.append(play)

    return yards_gained, play_time, optimal_play, play_tracker


def update_situation(quarter, time, play_time, to_go, yards_gained, down, 
offense, defense, team_1_score, team_2_score, team_1, team_2, play_type,
field_pos, ball_first, play_tracker):
    '''
    Update the game conditions in response to the previous play.

    Inputs:
        quarter (int): one of four quarters of the game
        time: datetime object representing the number of minutes and seconds
            left in the quarter
        play_time (int): number of seconds to complete the previous play
        to_go (int): number of yards to go until a first down or touchdown
        yards_gained: number of yards on a play, or the success/failure of a
            field goal
        down (int): one of four downs
        offense (string): team currently on offense
        defense (string): team currently on defense
        field_pos (int): yards until the offense reaches a touchdown
        team_1_score (int): team 1's total points in the game
        team_2_score (int): team 2's total points in the game
        team_1 (string): team 1 abbreviation
        team_2 (string): abbreviation
        play_type (string): the type of play previously ran
        ball_first (sring): the team that started the game with possession
        play_tracker: list of plays previously ran

    Outputs:
        quarter (int): one of four quarters of the game
        time: datetime object representing the number of minutes and seconds
            left in the quarter
        to_go (int): number of yards to go until a first down or touchdown
        field_pos (int): yards until the offense reaches a touchdown
        down (int): one of four downs
        offense (string): team currently on offense
        defense (string): team currently on defense
        team_1_score (int): team 1's total points in the game
        team_2_score (int): team 2's total points in the game
    '''
    # Update time
    play_time = datetime.timedelta(seconds = int(play_time))
    time = time - play_time
    if time.days < 0 or time.seconds == 0:
        # Halftime
        if quarter == 2:
            # Team that didn't start on offense starts second half on offense
            # with restarted field position
            if ball_first == offense:
                offense, defense, down, to_go = switch_possession(team_1, \
                    team_2, offense, defense)
                field_pos = 75
        # Next quarter
        quarter += 1
        time = datetime.timedelta(minutes = 15)

    # Assume a touchdown was not scored
    touchdown = False
    try:
        # Update field position
        yardage = int(yards_gained)
        field_pos = field_pos - yardage
        if field_pos <= 0:
            # Touchdown
            if play_type != 'punt':
                team_1_score, team_2_score = score_change(team_1_score, \
                    team_2_score, team_1, team_2, offense, defense, 7)
                touchdown = True
            # Touchback, so switch possession and change field position
            offense, defense, down, to_go = switch_possession(team_1, team_2, offense, defense)
            field_pos = 75
        # A punt that did not result in a touchback
        elif play_type == 'punt':
            offense, defense = switch_possession(team_1, team_2, offense, defense)
            field_pos = 100 - field_pos
        # Continuation of offensive drive
        else:
            to_go = to_go - yardage
            if to_go <= 0:
                # First down and 10 yards to go
                down = 1
                to_go = 10
                # Down and goal
                if to_go > field_pos:
                    to_go = field_pos
            else:
                down += 1
                # Turnover on downs
                if down == 5:
                    offense, defense, field_pos, down, to_go = \
                        turnover_on_downs(team_1, team_2, offense, defense, \
                        field_pos)

    # Play was a field goal, fumble, or interception
    except ValueError:
        # Successful field goal
        if play_type == 'field goal' and yards_gained == 'success':
            team_1_score, team_2_score = score_change(team_1_score, \
                team_2_score, team_1, team_2, offense, defense, 3)
            offense, defense, down, to_go = switch_possession (team_1, \
                team_2, offense, defense)
            field_pos = 75
        # Unsuccessful field goal, fumble or interception, so possession changes
        else:
            offense, defense, field_pos, down, to_go = turnover_on_downs(team_1, \
                team_2, offense, defense, field_pos)

    # Add updated scores and whether a touchdown waas scored to the previous play
    [play_tracker[-1].append(stat) for stat in [team_1_score, team_2_score, \
        touchdown]]

    return quarter, time, to_go, field_pos, down, offense, defense, \
        team_1_score, team_2_score


def switch_possession (team_1, team_2, offense, defense):
    '''
    Switch team that is on offense to defense and vice versa.

    Inputs:
        team_1 (string): team 1 abbreviation
        team_2 (string): team 2 abbreviation
        offense (string): team that was on offenes previously
        defense (string): team that was on defense previously

    Outputs:
        offense (string): team that was on offenes previously
        defense (string): team that was on defense previously
        down (int): one of four downs
        to_go (int): yards to go until a first down
    '''
    if offense == team_1:
        offense = team_2
        defense = team_1
    else:
        offense = team_1
        defense = team_2

    # New offensive team starts with first down and 10 yards to go
    down = 1
    to_go = 10

    return offense, defense, down, to_go


def score_change(team_1_score, team_2_score, team_1, team_2, offense, 
defense, points):
    '''
    Add points to the offensive team's score

    Inputs:
        team_1_score (int): team 1's points
        team_2_score (int): team 2's points
        team_1 (string): team 1 abbreviation
        team_2 (string): team 2 abbreviation
        offense (string): team that was on offenes previously
        defense (string): team that was on defense previously
        points (int): number of points to be added to offense's score

    Outputs:
        team_1_score (int): team 1's points
        team_2_score (int): team 2's points
    '''
    if offense == team_1:
        team_1_score += points
    else:
        team_2_score += points

    return team_1_score, team_2_score


def turnover_on_downs(team_1, team_2, offense, defense, field_pos):
    '''
    Update scenario when a team fails to convert a fourth down to a first down

    Inputs:
        team_1 (string): team 1 abbreviation
        team_2 (string): team 2 abbreviation
        offense (string): team that was on offenes previously
        defense (string): team that was on defense previously
        field_pos (int): field position of team that was on offense

    Outputs:
        offense (string): team that is now on offense
        defense (string): team that is now on offense
        field_pos (int): field position of team that is now on offense
        down (int): down out of four possibilities
        to_go (int): yards to go until the offense reaches a first down
    '''
    offense, defense, down, to_go = switch_possession(team_1, team_2, \
        offense, defense)
    field_pos = 100 - field_pos
    
    return offense, defense, field_pos, down, to_go