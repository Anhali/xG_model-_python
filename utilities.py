import pandas as pd
import numpy as np

def coords_to_bins(df, x_col, y_col, bins=(10, 10)):
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
    
    return bin_number


def add_previous_event_time(events):
    """
    Calculate the previous event time for each event.
    
    Arguments:
    events -- DataFrame of events with 'matchId', 'teamId', 'matchPeriod', and 'eventSec' columns.
    
    Returns:
    events -- DataFrame with an additional column 'previous_event_time'.
    """
    
    events['previous_event_time'] = events.groupby(['matchId', 'teamId', 'matchPeriod'])['eventSec'].shift(1).fillna(0)
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
    events['previous_event_time'] = events.groupby(['matchId', 'teamId', 'matchPeriod'])['eventSec'].shift(1).fillna(0)
    
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
    
    # Calculate the previous event time and possession duration
    events['previous_event_time'] = events.groupby(['matchId', 'teamId', 'matchPeriod'])['eventSec'].shift(1).fillna(0)
    events['possession_duration'] = events['eventSec'] - events['previous_event_time']
    events.drop(columns=['previous_event_time'], inplace=True)
    
    # Sort values to ensure proper cumulative summation
    events = events.sort_values(by=['matchId', 'teamId', 'matchPeriod', 'eventSec'])
    
    # Calculate the cumulative possession duration for each team in each match
    events['team_possession'] = events.groupby(['matchId', 'teamId'])['possession_duration'].cumsum()
    
    return events

def add_total_time(events):
    """
    Calculate the total possession time for each team in each match.
    
    Arguments:
    events -- DataFrame of events with 'matchId', 'teamId', 'matchPeriod', 'eventSec' columns.
    
    Returns:
    events -- DataFrame with an additional column 'total_time' containing the total possession times.
    """
    
    # Calculate the previous event time and possession duration
    events['previous_event_time'] = events.groupby(['matchId', 'teamId', 'matchPeriod'])['eventSec'].shift(1).fillna(0)
    events['possession_duration'] = events['eventSec'] - events['previous_event_time']
    events.drop(columns=['previous_event_time'], inplace=True)
    
    # Sort values to ensure proper cumulative summation
    events = events.sort_values(by=['matchId', 'teamId', 'matchPeriod', 'eventSec'])
    
    # Calculate the cumulative possession duration for each team in each match
    events['team_possession'] = events.groupby(['matchId', 'teamId'])['possession_duration'].cumsum()
    
    # Calculate the total time for each team in each match
    events['total_time'] = events.groupby(['matchId', 'teamId'])['possession_duration'].transform('sum')
    
    return events



