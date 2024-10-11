import numpy as np
import pandas as pd

def calculate_bin_indices(x, y, bins=(16, 12), field_length=105, field_width=68):
    """
    Calculate the bin indices for given (x, y) coordinates based on the field dimensions.
    
    Arguments:
    x, y -- Coordinates of the event on the field.
    bins -- Number of bins in the x and y directions (default 16x12).
    field_length -- Length of the field (default 105 meters).
    field_width -- Width of the field (default 68 meters).
    
    Returns:
    bin_x, bin_y -- The indices of the bins corresponding to the coordinates (x, y).
    """
    # Calculate the edges of the bins based on field dimensions
    x_edges = np.linspace(0, field_length, bins[0] + 1)
    y_edges = np.linspace(0, field_width, bins[1] + 1)
    
    # Convert coordinates to bin indices using pd.cut
    bin_x = pd.cut(x, x_edges, right=False, labels=np.arange(0, bins[0])).fillna(bins[0] - 1).astype(int)
    bin_y = pd.cut(y, y_edges, right=False, labels=np.arange(0, bins[1])).fillna(bins[1] - 1).astype(int)
    
    return bin_x, bin_y



def calculate_bin_number(events, x_col, y_col, bins=(16, 12), field_length=105, field_width=68):
    """
    Calculate the bin number for events based on their coordinates.

    Arguments:
    events -- DataFrame containing event data.
    x_col, y_col -- Column names for the x and y coordinates.
    bins -- Number of bins in x and y directions (default 16x12).
    field_length -- Length of the field (default 105 meters).
    field_width -- Width of the field (default 68 meters).

    Returns:
    bin_number -- The calculated bin number for each event.
    """
    # Call calculate_bin_indices with the new field dimensions
    bin_x, bin_y = calculate_bin_indices(events[x_col], events[y_col], bins, field_length, field_width)
    
    # Calculate the bin number
    bin_number = bin_x * bins[1] + bin_y
    return bin_number


def calculate_bin_center(bin_number, bins=(16, 12), field_length=105, field_width=68):
    """
    Calculate the center of a bin given its number.

    Arguments:
    bin_number -- Bin number.
    bins -- Number of bins in x and y directions (default 16x12).
    field_length -- Length of the field (default 105 meters).
    field_width -- Width of the field (default 68 meters).

    Returns:
    bin_center_x, bin_center_y -- Coordinates of the bin center.
    """
    # Calculate bin indices (bin_x, bin_y) from the bin number
    bin_x = bin_number // bins[1]
    bin_y = bin_number % bins[1]
    
    # Calculate the center of the bin based on the field dimensions
    bin_center_x = (bin_x + 0.5) * (field_length / bins[0])
    bin_center_y = (bin_y + 0.5) * (field_width / bins[1])
    
    return bin_center_x, bin_center_y


def distance_to_goal(bin_number, bins=(16, 12), goal_x=105, goal_y=34, field_length=105, field_width=68):
    """
    Calculate the distance from the bin center to the goal.

    Arguments:
    bin_number -- Bin number.
    bins -- Number of bins in x and y directions (default 16x12).
    goal_x -- x-coordinate of the goal (default 105).
    goal_y -- y-coordinate of the goal (default 34).
    field_length -- Length of the field (default 105 meters).
    field_width -- Width of the field (default 68 meters).

    Returns:
    distance -- Euclidean distance from the bin center to the goal.
    """
    # Calculate the bin center coordinates
    bin_center_x, bin_center_y = calculate_bin_center(bin_number, bins, field_length, field_width)
    
    # Calculate the Euclidean distance to the goal
    distance = np.sqrt((goal_x - bin_center_x)**2 + (goal_y - bin_center_y)**2)
    
    return distance


def calculate_shot_angle(bin_number, goal_width=7.32, bins=(16, 12), field_length=105, field_width=68):
    """
    Calculate the shooting angle from the bin center to the goal.

    Arguments:
    bin_number -- Bin number.
    goal_width -- Width of the goal (default 7.32 meters).
    bins -- Number of bins in x and y directions (default 16x12).
    field_length -- Length of the field (default 105 meters).
    field_width -- Width of the field (default 68 meters).

    Returns:
    angle -- Shooting angle in degrees.
    """
    # Calculate the bin center coordinates
    bin_center_x, bin_center_y = calculate_bin_center(bin_number, bins, field_length, field_width)
    
    # Calculate the shot angle using the provided formula
    angle = np.arctan((goal_width * bin_center_x) / (bin_center_x**2 + bin_center_y**2 - (goal_width / 2)**2))
    
    # Adjust negative angles
    angle = np.where(angle < 0, np.pi + angle, angle)
    
    # Convert from radians to degrees
    return np.degrees(angle)

def generate_bins_properties(events, bin_number, bins=(16, 12)):
    
    """
    Generate various bin properties (bin center, distance to goal, and shot angle) for events.

    Arguments:
    events -- DataFrame containing event data.
    bin_number -- Column name for the bin number.
    bins -- Number of bins in x and y directions (default 16x12).

    Returns:
    events -- Updated DataFrame with new columns for bin center, distance to goal, and shot angle.
    """
    # Calculate bin center
    events['bin_center_x'], events['bin_center_y'] = zip(*events[bin_number].apply(calculate_bin_center, bins=bins))
    
    # Calculate distance to goal
    events['distance_to_goal'] = distance_to_goal(events[bin_number])
    # Calculate angle to goal
    events['angle_to_goal'] = calculate_shot_angle(events['bin_center_x'], events['bin_center_y'])
    
    return events

  
# Fonction pour ajuster eventSec pour une ligne donnée
def adjust_eventSec(row, last_event_sec_first_half):
    if row['matchPeriod'] == '2H':
        return row['eventSec'] + last_event_sec_first_half
    else:
        return row['eventSec']
    

# Function to adjust eventSec for each match
def adjust_eventSec_for_match(events):
    """
    Adjust event times based on the match period (first or second half).

    Arguments:
    events -- DataFrame containing event data.

    Returns:
    events -- Updated DataFrame with adjusted event times.
    """
    # Find the latest event time in the first half
    last_event_sec_first_half = events[events['matchPeriod'] == '1H']['eventSec'].max()
    
    # Adjust event times using numpy
    events['adjusted_eventSec'] = np.where(events['matchPeriod'] == '2H', 
                                           events['eventSec'] + last_event_sec_first_half, 
                                           events['eventSec'])
    return events


# Main function to add adjusted_eventSec to the events DataFrame
def add_adjusted_eventSec(events):
    """
    Apply eventSec adjustments across matches.

    Arguments:
    events -- DataFrame containing event data.

    Returns:
    events -- Updated DataFrame with adjusted eventSec values.
    """
    events = events.groupby('matchId', group_keys=False).apply(adjust_eventSec_for_match).reset_index(drop=True)
    return events


def add_previous_event_time(events):
    """
    Calculate the time of the previous event for each event.

    Arguments:
    events -- DataFrame containing event data.

    Returns:
    events -- Updated DataFrame with 'previous_event_time' column.
    """
    events['previous_event_time'] = events.groupby(['matchId', 'matchPeriod'])['eventSec'].shift(1).fillna(0)
    return events


def add_possession_duration(events):
    """
    Calculate possession duration between events.

    Arguments:
    events -- DataFrame containing event data.

    Returns:
    events -- Updated DataFrame with possession duration column.
    """
    # Calculate the previous event time
    events = add_previous_event_time(events)
    
    # Calculate possession duration
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
        
    # Soustraire 1 des scores pour les événements 'Shot' où 'is_goal' est True
    events.loc[events['is_goal'], 'team_scores'] -= 1

    return events
