from typing import List, Dict, Any, Optional
from datetime import datetime

def calculate_team_stats(team_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate advanced team statistics."""
    stats = {
        'record': {
            'wins': team_data.get('wins', 0),
            'losses': team_data.get('losses', 0),
            'win_percentage': 0.0,
            'games_played': 0
        },
        'scoring': {
            'points_for': team_data.get('points_for', 0),
            'points_against': team_data.get('points_against', 0),
            'point_differential': 0,
            'avg_points_for': 0,
            'avg_points_against': 0
        },
        'streaks': {
            'current_streak': team_data.get('streak_type', 'N/A') + str(team_data.get('streak_length', 0)),
            'longest_win_streak': 0,
            'longest_loss_streak': 0
        }
    }
    
    # Calculate win percentage
    games_played = stats['record']['wins'] + stats['record']['losses']
    stats['record']['games_played'] = games_played
    stats['record']['win_percentage'] = round(stats['record']['wins'] / games_played, 3) if games_played > 0 else 0.0
    
    # Calculate scoring averages
    stats['scoring']['point_differential'] = stats['scoring']['points_for'] - stats['scoring']['points_against']
    stats['scoring']['avg_points_for'] = round(stats['scoring']['points_for'] / games_played, 2) if games_played > 0 else 0
    stats['scoring']['avg_points_against'] = round(stats['scoring']['points_against'] / games_played, 2) if games_played > 0 else 0
    
    return stats

def calculate_roster_stats(roster: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate roster statistics."""
    stats = {
        'positions': {},
        'total_players': len(roster),
        'injured_players': 0,
        'starters': 0,
        'bench': 0,
        'scoring': {
            'total_points': 0,
            'avg_points_per_player': 0,
            'highest_scorer': None,
            'lowest_scorer': None
        }
    }
    
    for player in roster:
        # Count positions
        pos = player.get('position', 'Unknown')
        stats['positions'][pos] = stats['positions'].get(pos, 0) + 1
        
        # Count injury statuses
        if player.get('injuryStatus') in ['OUT', 'INJURED']:
            stats['injured_players'] += 1
            
        # Calculate scoring
        player_points = sum(player.get('stats', {}).get('points', [0]))
        stats['scoring']['total_points'] += player_points
        
        # Track highest/lowest scorers
        if stats['scoring']['highest_scorer'] is None or player_points > stats['scoring']['highest_scorer']['points']:
            stats['scoring']['highest_scorer'] = {
                'name': player.get('name'),
                'points': player_points
            }
        if stats['scoring']['lowest_scorer'] is None or player_points < stats['scoring']['lowest_scorer']['points']:
            stats['scoring']['lowest_scorer'] = {
                'name': player.get('name'),
                'points': player_points
            }
    
    # Calculate averages
    if stats['total_players'] > 0:
        stats['scoring']['avg_points_per_player'] = round(stats['scoring']['total_points'] / stats['total_players'], 2)
    
    return stats

def calculate_matchup_stats(matchups: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate matchup statistics."""
    stats = {
        'total_matchups': len(matchups),
        'avg_combined_score': 0,
        'highest_scoring_game': None,
        'closest_game': None,
        'biggest_blowout': None,
        'home_wins': 0,
        'away_wins': 0
    }
    
    total_points = 0
    for matchup in matchups:
        home_score = matchup.get('home_team', {}).get('score', 0)
        away_score = matchup.get('away_team', {}).get('score', 0)
        combined_score = home_score + away_score
        point_differential = abs(home_score - away_score)
        
        # Track total points
        total_points += combined_score
        
        # Track highest scoring game
        if stats['highest_scoring_game'] is None or combined_score > stats['highest_scoring_game']['combined_score']:
            stats['highest_scoring_game'] = {
                'home_team': matchup.get('home_team', {}).get('team_name'),
                'away_team': matchup.get('away_team', {}).get('team_name'),
                'home_score': home_score,
                'away_score': away_score,
                'combined_score': combined_score
            }
        
        # Track closest game
        if stats['closest_game'] is None or point_differential < stats['closest_game']['point_differential']:
            stats['closest_game'] = {
                'home_team': matchup.get('home_team', {}).get('team_name'),
                'away_team': matchup.get('away_team', {}).get('team_name'),
                'home_score': home_score,
                'away_score': away_score,
                'point_differential': point_differential
            }
        
        # Track biggest blowout
        if stats['biggest_blowout'] is None or point_differential > stats['biggest_blowout']['point_differential']:
            stats['biggest_blowout'] = {
                'home_team': matchup.get('home_team', {}).get('team_name'),
                'away_team': matchup.get('away_team', {}).get('team_name'),
                'home_score': home_score,
                'away_score': away_score,
                'point_differential': point_differential
            }
        
        # Track home/away wins
        if home_score > away_score:
            stats['home_wins'] += 1
        else:
            stats['away_wins'] += 1
    
    # Calculate averages
    if stats['total_matchups'] > 0:
        stats['avg_combined_score'] = round(total_points / stats['total_matchups'], 2)
    
    return stats

def calculate_league_stats(teams: List[Dict[str, Any]], matchups: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate overall league statistics."""
    stats = {
        'teams': len(teams),
        'total_games': 0,
        'scoring': {
            'highest_scoring_team': None,
            'lowest_scoring_team': None,
            'avg_points_per_game': 0,
            'total_points': 0
        },
        'standings': {
            'avg_wins': 0,
            'avg_losses': 0,
            'most_wins': None,
            'most_losses': None
        },
        'matchups': calculate_matchup_stats(matchups)
    }
    
    total_wins = 0
    total_losses = 0
    for team in teams:
        wins = team.get('wins', 0)
        losses = team.get('losses', 0)
        points = team.get('points_for', 0)
        
        # Track total games
        stats['total_games'] += wins + losses
        
        # Track wins/losses
        total_wins += wins
        total_losses += losses
        
        # Track highest/lowest scoring teams
        if stats['scoring']['highest_scoring_team'] is None or points > stats['scoring']['highest_scoring_team']['points']:
            stats['scoring']['highest_scoring_team'] = {
                'team_name': team.get('team_name'),
                'points': points
            }
        if stats['scoring']['lowest_scoring_team'] is None or points < stats['scoring']['lowest_scoring_team']['points']:
            stats['scoring']['lowest_scoring_team'] = {
                'team_name': team.get('team_name'),
                'points': points
            }
        
        # Track most wins/losses
        if stats['standings']['most_wins'] is None or wins > stats['standings']['most_wins']['wins']:
            stats['standings']['most_wins'] = {
                'team_name': team.get('team_name'),
                'wins': wins
            }
        if stats['standings']['most_losses'] is None or losses > stats['standings']['most_losses']['losses']:
            stats['standings']['most_losses'] = {
                'team_name': team.get('team_name'),
                'losses': losses
            }
        
        stats['scoring']['total_points'] += points
    
    # Calculate averages
    if stats['teams'] > 0:
        stats['standings']['avg_wins'] = round(total_wins / stats['teams'], 2)
        stats['standings']['avg_losses'] = round(total_losses / stats['teams'], 2)
        stats['scoring']['avg_points_per_game'] = round(stats['scoring']['total_points'] / stats['total_games'], 2) if stats['total_games'] > 0 else 0
    
    return stats
