import random
import datetime

def find_optimal_plays(scenarios_df):
    # Get past plays dataframe
    plays_df = pd.read_csv('out.csv', cols = [])

    # Create dataframe with optimal play type for each situation
    optimal_play_types_df = scenarios_df[scenarios_df['EPA sum'] == \
        scenarios_df.groupby(['Quarter', 'Down', 'To go', 'Score difference', \
        'Field position', 'Play type'])['EPA sum'].transform(max)]

    return optimal_play_types_df

def simulator(plays_df, optimal_plays_df, team_1, team_2):
    '''
    Simulates game.
    '''
    # Coin toss
    flip = random.randint(0, 1)
    if flip == 0:
        offense = team_1
        defense = team_2
    else:
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
    
    # Set conditions for current situation
    same_offense = optimal_play_types_df['Offense'] == offense
    same_quarter = optimal_play_types_df['Quarter'] == quarter
    same_down = optimal_play_types_df['Down'] == down
    same_to_go = optimal_play_types_df['To go'] == to_go
    same_field_pos = optimal_play_types_df['Field position'] = field_pos
    same_score_diff = optimal_play_types_df['Score difference'] = score_diff

    # Get play optimal play type for current situation
    optimal_play_row = optimal_play_types_df[same_offense & same_quarter & \
        same_down & same_to_go & same_field_pos & same_score_diff]
    optimal_play_type = optimal_play_row.iloc[0]['Play type']

    # Call random play of this type
    team_to_use = random.randint(0, 1)
    # Use outcome from offensive play history
    if team_to_use == 0:
        same_team = plays_df['Offense'] == offense
    # Use outcome from defensive play history
    else:
        same_team = plays_df['Defense'] == defense

    # Get play outcome
    past_plays = plays_df[same_team & same_quarter & same_down & same_to_go & \
        same_field_pos & same_score_diff]
    yards_gained = past_plays.iloc[rand.randint(0, len(plays_df) - \
        1)]['Yards gained']

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