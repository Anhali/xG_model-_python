import pandas as pd
import numpy as np

def coords_to_bins(df, x_col, y_col, bins=(12, 16)):
    # Calculate bin edges
    x_edges = np.linspace(0, 100, bins[0] + 1)
    y_edges = np.linspace(0, 100, bins[1] + 1)
    
    # Convert coordinates to bins using pd.cut
    bin_x = pd.cut(df[x_col], x_edges, right=False, labels=np.arange(0, bins[0]))
    bin_y = pd.cut(df[y_col], y_edges, right=False, labels=np.arange(0, bins[1]))
    
    # Handle the edge case where x or y equals 100
    bin_x = bin_x.fillna(bins[0] - 1).astype(int)
    bin_y = bin_y.fillna(bins[1] - 1).astype(int)
    
    # Calculate the bin number
    bin_number = bin_x * bins[1] + bin_y
    
    return  bin_number

  
   # Fonction pour ajuster eventSec pour une ligne donnée
def adjust_eventSec(row, last_event_sec_first_half):
    if row['matchPeriod'] == '2H':
        return row['eventSec'] + last_event_sec_first_half
    else:
        return row['eventSec']
    

# Fonction pour ajuster eventSec pour chaque match
def adjust_eventSec_for_match(df):
    last_event_sec_first_half = df[df['matchPeriod'] == '1H']['eventSec'].max()
    df['adjusted_eventSec'] = df.apply(adjust_eventSec, axis=1, last_event_sec_first_half=last_event_sec_first_half)
    return df


# Fonction principale pour ajouter la colonne adjusted_eventSec
def add_adjusted_eventSec(data_event):
    data_event = data_event.groupby('matchId', group_keys=False).apply(adjust_eventSec_for_match).reset_index(drop=True)
    return data_event


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

