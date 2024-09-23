import numpy as np
import pandas as pd

def calculate_bin_indices(x, y, bins=(16, 12), field_length=105, field_width=68):
    # Calculate bin edges based on the actual field dimensions
    x_edges = np.linspace(0, field_length, bins[0] + 1)
    y_edges = np.linspace(0, field_width, bins[1] + 1)
    
    # Convert coordinates to bin indices using pd.cut
    bin_x = pd.cut(x, x_edges, right=False, labels=np.arange(0, bins[0])).fillna(bins[0] - 1).astype(int)
    bin_y = pd.cut(y, y_edges, right=False, labels=np.arange(0, bins[1])).fillna(bins[1] - 1).astype(int)
    
    return bin_x, bin_y




def calculate_bin_number(events, x_col, y_col, bins=(16, 12), field_length=105, field_width=68):
    # Appeler calculate_bin_indices avec les nouvelles dimensions du terrain
    bin_x, bin_y = calculate_bin_indices(events[x_col], events[y_col], bins, field_length, field_width)
    # Calculate the bin number
    bin_number = bin_x * bins[1] + bin_y
    return bin_number





def calculate_bin_center(x_col, y_col, bins=(16, 12), field_length=105, field_width=68):
    # Calcul des indices des bins
    bin_x, bin_y = calculate_bin_indices(x_col, y_col, bins, field_length, field_width)
    
    # Calculer les centres des bins en fonction des dimensions réelles du terrain
    bin_center_x = (bin_x + 0.5) * (field_length / bins[0])
    bin_center_y = (bin_y + 0.5) * (field_width / bins[1])
    
    return bin_center_x, bin_center_y




def calculate_distance_to_goal(x_col, y_col, bins=(16, 12), field_length=105, field_width=68, goal_x=105, goal_y=34):
    # Calcul des centres des bins avec les dimensions réelles
    bin_center_x, bin_center_y = calculate_bin_center(x_col, y_col, bins, field_length, field_width)
    
    # Calculer la distance du centre du bin au but (goal_x, goal_y)
    distance_to_goal = np.sqrt((goal_x - bin_center_x)**2 + (goal_y - bin_center_y)**2)
    
    return distance_to_goal




def calculate_angle_to_goal(x, y, goal_x=105, goal_y=34):
    # Calculer la différence en x et y entre le bin et le but
    x_dist = goal_x - x
    y_dist = goal_y - y
    
    # Calculer l'angle à l'aide de arctan2 pour obtenir l'angle en radians
    angle = np.arctan2(y_dist, x_dist)
    
    # Ajuster l'angle si négatif (on veut un angle positif)
    angle = np.where(angle < 0, np.pi + angle, angle)
    
    # Convertir l'angle en degrés
    return np.degrees(angle)



def generate_bins_properties(events, x_col, y_col, bins=(16, 12)):
    # Calculate bin number
    events['bin_number'] = calculate_bin_number(events, x_col, y_col, bins)
    # Calculate bin center
    events['bin_center_x'], events['bin_center_y'] = calculate_bin_center(events[x_col], events[y_col], bins)
    # Calculate distance to goal
    events['distance_to_goal'] = calculate_distance_to_goal(events[x_col], events[y_col])
    # Calculate angle to goal
    events['angle_to_goal'] = calculate_angle_to_goal(events['bin_center_x'], events['bin_center_y'])
    
    return events


  
# Fonction pour ajuster eventSec pour une ligne donnée
def adjust_eventSec(row, last_event_sec_first_half):
    if row['matchPeriod'] == '2H':
        return row['eventSec'] + last_event_sec_first_half
    else:
        return row['eventSec']
    

# Fonction pour ajuster eventSec pour chaque match
def adjust_eventSec_for_match(events):
    # Trouver le temps de l'événement le plus tardif dans la première mi-temps
    last_event_sec_first_half = events[events['matchPeriod'] == '1H']['eventSec'].max()
    
    # Ajuster les temps d'événements directement en utilisant numpy où pandas
    events['adjusted_eventSec'] = np.where(events['matchPeriod'] == '2H', 
                                       events['eventSec'] + last_event_sec_first_half, 
                                       events['eventSec'])
    return events


# Fonction principale pour ajouter la colonne adjusted_eventSec
def add_adjusted_eventSec(events):
    events = events.groupby('matchId', group_keys=False).apply(adjust_eventSec_for_match).reset_index(drop=True)
    return events


def add_previous_event_time(events):
    """
    Calculate the previous event time for each event.
    
    Arguments:
    events -- DataFrame of events with 'matchId', 'teamId', 'matchPeriod', and 'eventSec' columns.
    
    Returns:
    events -- DataFrame with an additional column 'previous_event_time'.
    """
    
    events['previous_event_time'] = events.groupby(['matchId',  'matchPeriod'])['eventSec'].shift(1).fillna(0)
    return events

def add_possession_duration(events):
    """
    Calculate the possession duration between events.
    
    Arguments:
    events -- DataFrame of events with 'matchId', 'teamId', 'matchPeriod', and 'eventSec' columns.
    
    Returns:
    events -- DataFrame with an additional column 'possession_duration'.
    """
    
    # Calculate the previous event time
    events = add_previous_event_time(events)
    
    # Calculate the possession duration between events
    events['possession_duration'] = events['eventSec'] - events['previous_event_time']
    
    # Remove the previous event time column
    events.drop(columns=['previous_event_time'], inplace=True)
    
    return events

def add_team_possession(events):
    """
    Calculate the cumulative possession time for each team in each match.
    
    Arguments:
    events -- DataFrame of events with 'matchId', 'teamId', 'matchPeriod', and 'eventSec' columns.
    
    Returns:
    events -- DataFrame with an additional column 'team_possession' containing the cumulative possession times.
    """
    events = add_previous_event_time(events)
    events = add_possession_duration(events)
    
    # Sort values to ensure proper cumulative summation
    events = events.sort_values(by=['matchId', 'teamId', 'matchPeriod', 'eventSec'])
    
    # Calculate the cumulative possession duration for each team in each match
    events['team_possession'] = events.groupby(['matchId', 'teamId'])['possession_duration'].cumsum()
    
    return events


def update_team_scores(row, team_scores, team_ids):
    if row['is_goal']:
        opponent_team = team_ids[1] if row['teamId'] == team_ids[0] else team_ids[0]
        team_scores[row['teamId']] += 1
        team_scores[opponent_team] -= 1
    return team_scores[row['teamId']]

def calculate_team_scores(events):
    # Initialiser la colonne team_scores à 0
    events['team_scores'] = 0

    # Identifier les buts
    events['is_goal'] = events['subEventName'].eq('Shot') & \
                        events['tags'].apply(lambda x: any(tag['id'] == 101 for tag in x))

    # Parcourir chaque match
    for match_id, match_df in events.groupby('matchId'):
        team_ids = match_df['teamId'].unique()
        if len(team_ids) != 2:
            continue

        # Initialiser les scores des équipes à 0 pour ce match
        team_scores = {team_ids[0]: 0, team_ids[1]: 0}

        # Appliquer la mise à jour des scores
        events.loc[match_df.index, 'team_scores'] = match_df.apply(
            lambda row: update_team_scores(row, team_scores, team_ids), axis=1)

    return events


def adjust_scores_for_shots(events):
    # Soustraire 1 des scores pour les événements 'Shot' où 'is_goal' est True
    events.loc[events['is_goal'], 'team_scores'] -= 1
    return events
