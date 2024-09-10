import pandas as pd
import numpy as np

def coords_to_bins(events, x_col, y_col, bins=(16, 12)):
    # Calculate bin edges
    x_edges = np.linspace(0, 100, bins[0] + 1)
    y_edges = np.linspace(0, 100, bins[1] + 1)
    
    # Convert coordinates to bins using pd.cut
    bin_x = pd.cut(events[x_col], x_edges, right=False, labels=np.arange(0, bins[0]))
    bin_y = pd.cut(events[y_col], y_edges, right=False, labels=np.arange(0, bins[1]))
    
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


def calculate_team_scores(events):
    # Initialiser la colonne team_scores à 0
    events['team_scores'] = 0
    
    # Parcourir chaque match
    for match_id in events['matchId'].unique():
        match_mask = events['matchId'] == match_id
        match_df = events.loc[match_mask]
        
        # Identifier les équipes en compétition dans ce match
        team_ids = match_df['teamId'].unique()
        if len(team_ids) != 2:
            # Passer ce match s'il n'y a pas exactement deux équipes détectées
            continue
        
        # Initialiser les scores pour les équipes
        team_scores = {team_ids[0]: 0, team_ids[1]: 0}
        
        # Parcourir chaque événement du match
        for idx in match_df.index:
            row = events.loc[idx]
            
            # Vérifier si l'événement est un tir et s'il y a un but
            if row['subEventName'] == 'Shot' and any(tag['id'] == 101 for tag in row['tags']):
                # Identifier l'équipe adverse
                opponent_team = team_ids[1] if row['teamId'] == team_ids[0] else team_ids[0]
                
                # Mettre à jour le score pour l'équipe qui a marqué
                team_scores[row['teamId']] = 1
                
                # Mettre à jour le score pour l'équipe adverse
                team_scores[opponent_team] = -1
            
            # Mettre à jour la colonne 'team_scores' avec la valeur de l'équipe en cours
            events.at[idx, 'team_scores'] = team_scores[row['teamId']]
    
    return events
