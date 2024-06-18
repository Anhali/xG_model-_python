import pandas as pd

def calculate_previous_possession(events):
    # Trier les événements par match et par temps
    events = events.sort_values(by=['matchId', 'eventSec'])

    # Initialiser les colonnes pour stocker la durée de possession précédant chaque événement
    events['previous_possession_percentage_team'] = 0.0
    events['previous_possession_percentage_opponent'] = 0.0

    # Dictionnaire pour garder la trace de la dernière possession par match
    possession_data = {}
    match_total_times = {}

    for idx, row in events.iterrows():
        match_id = row['matchId']
        event_time = row['eventSec']
        team_id = row['teamId']

        if match_id not in possession_data:
            possession_data[match_id] = {
                'last_team': team_id,
                'last_time': event_time,
                'team_possession': {}
            }
            match_total_times[match_id] = event_time  # Initialiser le temps total du match

        if team_id not in possession_data[match_id]['team_possession']:
            possession_data[match_id]['team_possession'][team_id] = 0.0

        # Calculer l'identifiant de l'équipe adverse
        opponent_team_id = 'other'  # Utiliser une clé spéciale pour l'équipe adverse
        if opponent_team_id not in possession_data[match_id]['team_possession']:
            possession_data[match_id]['team_possession'][opponent_team_id] = 0.0

        # Calculer la durée de possession depuis le dernier événement
        last_team = possession_data[match_id]['last_team']
        last_time = possession_data[match_id]['last_time']
        duration_since_last = event_time - last_time

        # Mettre à jour la possession pour l'équipe précédente
        if last_team == team_id:
            possession_data[match_id]['team_possession'][team_id] += duration_since_last
        else:
            possession_data[match_id]['team_possession'][opponent_team_id] += duration_since_last

        # Mettre à jour le temps total du match jusqu'à présent
        match_total_times[match_id] = event_time

        # Mettre à jour les valeurs précédentes de possession pour l'événement courant
        total_time = match_total_times[match_id]
        if total_time > 0:
            events.at[idx, 'previous_possession_percentage_team'] = (possession_data[match_id]['team_possession'][team_id] / total_time) * 100
            events.at[idx, 'previous_possession_percentage_opponent'] = (possession_data[match_id]['team_possession'][opponent_team_id] / total_time) * 100

        # Mettre à jour la dernière équipe et le dernier temps
        possession_data[match_id]['last_team'] = team_id
        possession_data[match_id]['last_time'] = event_time

        # Réinitialiser la possession de l'adversaire si l'équipe change
        if last_team != team_id:
            possession_data[match_id]['team_possession'][opponent_team_id] = 0.0

    return events
