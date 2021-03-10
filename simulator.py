import statistics
import random
import datetime

def find_optimal_plays():
    # Get past plays dataframe
    # Needed columns: year, team on offense and their score difference, EPC,
    # and field goals
    plays_df = pd.read_csv('out.csv', names = ['Quarter', 'Time', 'Down', \
        'To go', 'To go category', 'Field position', 'Away score', \
        'Home score', 'Score difference', 'EPB', 'EPA', 'Team 1', 'Team 2', \
        'Field zone', 'Seconds', 'Play type', 'Yards'])

    # Create dataframe with average EPC for each play type in each situation
    # I don't think this will work because the average doesn't exist
    scenarios_df = plays_df[plays_df['EPC sum'] == plays_df.groupby(['Quater', \
        'Down', 'To go category', 'Field zone', 'Score difference', \
        'Play type']).transform(statistics.mean)]
    
    # Create dataframe with optimal play type for each situation
    optimal_play_types_df = scenarios_df[scenarios_df['EPC sum'] == \
        scenarios_df.groupby(['Quarter', 'Down', 'To go category', \
        'Field zone', 'Score difference', 'Play type'])['EPC sum'].transform(max)]

    return optimal_play_types_df

def simulator(plays_df, optimal_plays_df, team_1, team_2):
    '''
    Simulates game.
    '''
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
    score_diff = team_2_score - team_1_score
    quarter = 1
    time = datetime.timedelta(minutes = 15)
    field_pos = 75
    down = 1
    to_go = 10

    while quarter <= 4:
        # Categorize yards to go and field position
        to_go_cat = categorize_to_go(to_go)
        field_zone = categorize_field_pos(field_pos)

        # Run play
        yards_gained, play_time, play_type = run_play(optimal_play_types_df, offense, defense, \
            quarter, down, to_go_cat, field_pos_cat, score_diff, team_1_score, \
            team_2_score, play_tracker, plays_df)

        # Update simulation after play
        quarter, time, to_go, down, offense, defense, team_1_score, \
            team_2_score = update_situation(quarter, time, play_time, to_go, \
            yards_gained, down, offense, defense, team_1_score, team_2_score, \
            team_1, team_2, play_type)

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
    if field_position <= 25:
        field_zone = 'red zone'
    elif 25 < field_position <= 50:
        field_zone = 'green zone'
    elif 50 < field_position <= 75:
        field_zone = 'grey zone'
    elif field_position > 75:
        field_zone = 'black zone'
    
    return field_zone


def run_play(optimal_play_types_df, offense, defense, quarter, down, to_go_cat, 
field_pos_cat, score_diff, team_1_score, team_2_score, play_tracker, plays_df):
    # Set conditions for current situation
    same_offense = optimal_play_types_df['Offense'] == offense
    # same_quarter = optimal_play_types_df['Quarter'] == quarter
    same_down = optimal_play_types_df['Down'] == down
    same_to_go = optimal_play_types_df['To go category'] == to_go_cat
    same_field_pos = optimal_play_types_df['Field zone'] = field_pos_cat
    # same_score_diff = optimal_play_types_df['Score difference'] = score_diff

    # Get play optimal play type for current situation
    optimal_play_row = optimal_play_types_df[same_offense & \
        same_down & same_to_go & same_field_pos]
    optimal_play_type = optimal_play_row.iloc[0]['Play type']

    # Call random play of this type using outcome from offense or defense
    team_to_use = random.randint(0, 1)
    # Use outcome from offensive play history
    if team_to_use == 0:
        same_team = plays_df['Offense'] == offense
    # Use outcome from defensive play history
    else:
        same_team = plays_df['Defense'] == defense

    # Get play outcome
    past_plays = plays_df[same_team & same_down & same_to_go & \
        same_field_pos]
    yards_gained = past_plays.iloc[rand.randint(0, len(plays_df) - \
        1)]['Yards gained']
    play_time = = past_plays.iloc[rand.randint(0, len(plays_df) - \
        1)]['Play time']

    # Create location
    if field_pos >= 50:
        # Not sure if offense is a string or list
        location = offense[0] + ' ' + str(100 - field_pos)
    else:
        location = defense[0] + ' ' + str(field_pos)
    
    # Create play
    # Could also extract and add play detail
    play = [quarter, time, down, to_go, location, team_1_score, team_2_score, \
        yards_gained]
    play_tracker.append(play)

    return yards_gained, play_time, optimal_play_type


def update_situation(quarter, time, play_time, to_go, yards_gained, down, 
offense, defense, team_1_score, team_2_score, team_1, team_2, play_type):
    # Update time
    time = time - play_time
    if time.days <= 0:
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
        if quarter == 5:
            # Not sure if this will end the simulation
            break
        time = datetime.timedelta(minutes = 15)


    # Update field position and score
    # Play gained or lost yards - regular offensive play or punt
    if type(yards_gained) is int:
        field_pos = field_pos - yards_gained
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
    else:
        # Successful field goal
        if play_type == 'field goal' and yards_gained = 'success':
            team_1_score, team_2_score = score_change(team_1_score, \
                team_2_score, team_1, team_2, offense, defense, 3)
            field_pos = 75
        # Unsuccessful field goal, fumble or interception, causing a possession change
        offense, defense, field_pos, down, to_go = turnover_on_downs(team_1, \
            team_2, offense, defense, field_pos)

    return quarter, time, to_go, down, offense, defense, team_1_score, team_2_score


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
    offense, defense = switch_possession(team_1, team_2, offense, defense)
    field_pos = 100 - field_pos
    down = 1
    to_go = 10
    
    return offense, defense, field_pos, down, to_go