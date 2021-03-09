import random
import datetime

def find_optimal_plays(scenarios_df)
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
        possession = team_1
    else:
        possession = team_2

    # Initialize game situation - skip kickoff and go to 1st and 10
    team_1_score = 0
    team_2_score = 0
    quarter = 1
    time = datetime.timedelta(minutes = 15)
    field_position = 75
    down = 1
    to_go = 10
    
    # Find optimal play for current situation
    same_quarter = optimal_play_types_df['Quarter'] == quarter
    same_down = optimal_play_types_df['Down'] == down
    same_to_go = find_yard_range(df['To go']) == find_yard_range(to_go)
    same_field_position = 
    same_score_diff = 
    similar_plays = df[same_quarter & same_down & same_to_go & \
    same_field_position & same_score_diff]
    similar_plays_grouped = similar_plays.groupby['Play type'].size()
    