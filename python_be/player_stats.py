from typing import Dict, Any, List, Optional

def calculate_player_stats(player_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate detailed player statistics."""
    stats = {
        'info': {
            'name': player_data.get('name'),
            'position': player_data.get('position'),
            'proTeam': player_data.get('proTeam'),
            'injuryStatus': player_data.get('injuryStatus')
        },
        'stats': {
            'total': {},
            'average': {},
            'last_5_games': [],
            'best_game': None,
            'worst_game': None
        },
        'fantasy': {
            'total_points': 0,
            'avg_points': 0,
            'projected_points': 0,
            'ownership': {
                'owned_percent': player_data.get('owned_percent', 0),
                'starter_percent': player_data.get('starter_percent', 0)
            }
        }
    }

    # Get stats from player data
    raw_stats = player_data.get('stats', {})
    
    # Calculate totals
    if 'averageStats' in raw_stats:
        stats['stats']['average'] = raw_stats['averageStats']
    if 'totalStats' in raw_stats:
        stats['stats']['total'] = raw_stats['totalStats']
    
    # Calculate game stats if available
    if 'gameStats' in raw_stats:
        game_stats = raw_stats['gameStats']
        
        # Get last 5 games
        stats['stats']['last_5_games'] = game_stats[-5:] if len(game_stats) > 5 else game_stats
        
        # Find best and worst games based on fantasy points
        if game_stats:
            sorted_games = sorted(game_stats, key=lambda x: x.get('points', 0), reverse=True)
            stats['stats']['best_game'] = sorted_games[0] if sorted_games else None
            stats['stats']['worst_game'] = sorted_games[-1] if sorted_games else None
    
    return stats

def get_player_comparison(player1_stats: Dict[str, Any], player2_stats: Dict[str, Any]) -> Dict[str, Any]:
    """Compare two players' statistics."""
    comparison = {
        'players': {
            'player1': player1_stats['info'],
            'player2': player2_stats['info']
        },
        'stats_comparison': {},
        'fantasy_comparison': {
            'total_points': {
                'player1': player1_stats['fantasy']['total_points'],
                'player2': player2_stats['fantasy']['total_points'],
                'difference': player1_stats['fantasy']['total_points'] - player2_stats['fantasy']['total_points']
            },
            'avg_points': {
                'player1': player1_stats['fantasy']['avg_points'],
                'player2': player2_stats['fantasy']['avg_points'],
                'difference': player1_stats['fantasy']['avg_points'] - player2_stats['fantasy']['avg_points']
            }
        },
        'trends': {
            'last_5_games': {
                'player1': player1_stats['stats']['last_5_games'],
                'player2': player2_stats['stats']['last_5_games']
            }
        }
    }
    
    # Compare average stats
    for stat, value in player1_stats['stats']['average'].items():
        comparison['stats_comparison'][stat] = {
            'player1': value,
            'player2': player2_stats['stats']['average'].get(stat, 0),
            'difference': value - player2_stats['stats']['average'].get(stat, 0)
        }
    
    return comparison

def calculate_position_rankings(players: List[Dict[str, Any]], position: Optional[str] = None) -> List[Dict[str, Any]]:
    """Calculate rankings for players in a specific position."""
    # Filter players by position if specified
    if position:
        position_players = [p for p in players if p.get('position') == position]
    else:
        position_players = players
    
    # Sort players by fantasy points
    sorted_players = sorted(
        position_players,
        key=lambda x: x.get('stats', {}).get('totalStats', {}).get('points', 0),
        reverse=True
    )
    
    # Create rankings
    rankings = []
    for idx, player in enumerate(sorted_players, 1):
        rankings.append({
            'rank': idx,
            'name': player.get('name'),
            'position': player.get('position'),
            'total_points': player.get('stats', {}).get('totalStats', {}).get('points', 0),
            'avg_points': player.get('stats', {}).get('averageStats', {}).get('points', 0),
            'team': player.get('proTeam'),
            'injury_status': player.get('injuryStatus')
        })
    
    return rankings

def get_player_trends(player_stats: Dict[str, Any], weeks: int = 4) -> Dict[str, Any]:
    """Analyze player trends over specified number of weeks."""
    trends = {
        'scoring': {
            'trend': 'stable',
            'avg_last_n_weeks': 0,
            'avg_previous_n_weeks': 0,
            'change_percentage': 0
        },
        'usage': {
            'minutes_trend': 'stable',
            'shots_trend': 'stable'
        },
        'performance': {
            'hot_zones': [],
            'cold_zones': []
        }
    }
    
    game_stats = player_stats['stats'].get('gameStats', [])
    if len(game_stats) >= weeks * 2:
        # Calculate recent vs previous averages
        recent_games = game_stats[-weeks:]
        previous_games = game_stats[-(weeks*2):-weeks]
        
        recent_avg = sum(g.get('points', 0) for g in recent_games) / weeks
        previous_avg = sum(g.get('points', 0) for g in previous_games) / weeks
        
        trends['scoring']['avg_last_n_weeks'] = round(recent_avg, 2)
        trends['scoring']['avg_previous_n_weeks'] = round(previous_avg, 2)
        
        # Calculate trend
        if recent_avg > previous_avg * 1.1:
            trends['scoring']['trend'] = 'up'
        elif recent_avg < previous_avg * 0.9:
            trends['scoring']['trend'] = 'down'
        
        # Calculate change percentage
        if previous_avg > 0:
            trends['scoring']['change_percentage'] = round(
                ((recent_avg - previous_avg) / previous_avg) * 100, 
                1
            )
    
    return trends

def get_matchup_analysis(player_stats: Dict[str, Any], opponent_team: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze player performance against specific opponent."""
    analysis = {
        'historical_performance': {
            'avg_points': 0,
            'games_played': 0,
            'best_performance': None,
            'worst_performance': None
        },
        'matchup_rating': 'neutral',  # favorable, neutral, or unfavorable
        'key_stats': {},
        'projected_performance': {
            'points': 0,
            'confidence': 'medium'  # low, medium, or high
        }
    }
    
    # Get games against opponent
    opponent_games = [
        game for game in player_stats['stats'].get('gameStats', [])
        if game.get('opponent') == opponent_team.get('proTeam')
    ]
    
    if opponent_games:
        analysis['historical_performance']['games_played'] = len(opponent_games)
        analysis['historical_performance']['avg_points'] = round(
            sum(g.get('points', 0) for g in opponent_games) / len(opponent_games),
            2
        )
        
        # Get best and worst performances
        sorted_games = sorted(opponent_games, key=lambda x: x.get('points', 0), reverse=True)
        analysis['historical_performance']['best_performance'] = sorted_games[0]
        analysis['historical_performance']['worst_performance'] = sorted_games[-1]
        
        # Determine matchup rating
        avg_vs_opponent = analysis['historical_performance']['avg_points']
        overall_avg = player_stats['fantasy']['avg_points']
        
        if avg_vs_opponent > overall_avg * 1.1:
            analysis['matchup_rating'] = 'favorable'
        elif avg_vs_opponent < overall_avg * 0.9:
            analysis['matchup_rating'] = 'unfavorable'
    
    return analysis
