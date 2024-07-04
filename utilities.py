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
    This function adds a column for the previous event time for each event.
    
    Arguments:
    events -- DataFrame of events with 'matchId', 'matchPeriod' and 'eventSec' columns.
    
    Returns:
    events -- DataFrame with an additional column 'previous_event_time' containing the time of the previous event.
    """
    
    # Sort events by 'matchId', 'matchPeriod', and 'eventSec'
    events = events.sort_values(by=['matchId', 'matchPeriod', 'eventSec'])

    # Create 'previous_event_time' by shifting 'eventSec' by one row, fill the first row with 0
    events['previous_event_time'] = events['eventSec'].shift(1, fill_value=0)

    # Reset 'previous_event_time' to 0 if the current event time is less than the previous event time
    events.loc[events['eventSec'] < events['previous_event_time'], 'previous_event_time'] = 0
    
    return events


def add_possession_duration(events):
    """
    This function calculates the possession duration between events and adds cumulative possession time for each team in each match.
    
    Arguments:
    events -- DataFrame of events with 'matchId', 'teamId', 'matchPeriod', 'eventSec', and 'previous_event_time' columns.
    
    Returns:
    events -- DataFrame with additional columns 'possession_duration' and 'team_possession' containing the possession durations and cumulative possession times respectively.
    """
    
    # Calculate the possession duration between events
    events['possession_duration'] = events['eventSec'] - events['previous_event_time']

    # Calculate the cumulative possession duration for each team in each match
    events['team_possession'] = (
        events.sort_values(by=['matchId', 'teamId', 'matchPeriod', 'eventSec'])
              .groupby(['matchId', 'teamId'])['possession_duration']
              .cumsum()
    )
    
    return events


def add_total_time(events):
    """
    This function calculates the cumulative total time for possession duration within each match and adds it as a new column 'total_time'.
    
    Arguments:
    events -- DataFrame of events with 'matchId', 'matchPeriod', 'eventSec', and 'possession_duration' columns.
    
    Returns:
    events -- DataFrame with an additional column 'total_time' containing the cumulative total time for each match.
    """
    
    # Sort events by 'matchId', 'matchPeriod', and 'eventSec'
    events = events.sort_values(by=['matchId', 'matchPeriod', 'eventSec'])

    # Calculate the cumulative total time for possession duration within each match
    events['total_time'] = (
        events.groupby(['matchId'])['possession_duration']
              .cumsum()
    )
    
    return events

