from fastapi import APIRouter, HTTPException, Query
from espn_client import ESPNClient
from typing import Any, Optional, List, Dict
# from player_stats import (
#     # calculate_player_stats,
#     # get_player_comparison,
#     # calculate_position_rankings,
#     # get_player_trends,
#     # get_matchup_analysis
# )

# Initialize the router
router = APIRouter(prefix="/api/v1")

# Initialize the ESPNClient (singleton pattern ensures only one instance)
client = ESPNClient()

# Helper function to safely get attributes
def safe_getattr(obj, attr: str, default: Any = None) -> Any:
    try:
        return getattr(obj, attr, default)
    except AttributeError:
        return default

# Helper function for pagination
def paginate_results(items: List[Any], page: int = 1, page_size: int = 10) -> Dict[str, Any]:
    """Paginate a list of items."""
    start = (page - 1) * page_size
    end = start + page_size
    total_items = len(items)
    total_pages = (total_items + page_size - 1) // page_size
    
    return {
        'items': items[start:end],
        'pagination': {
            'total_items': total_items,
            'total_pages': total_pages,
            'current_page': page,
            'page_size': page_size,
            'has_next': end < total_items,
            'has_previous': page > 1
        }
    }

# League Information Endpoints
# @router.get("/league/info")
# def get_league_info():
#     """Get comprehensive league information."""
#     try:
#         info = client.get_league_info()
#         if info is None:
#             raise HTTPException(status_code=404, detail="League info not found")
#         return info
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@router.get("/league/standings")
def get_standings(
    division_id: Optional[int] = None,
    page: int = Query(1, gt=0),
    page_size: int = Query(10, gt=0, le=50)
):
    """Get league standings, optionally filtered by division."""
    try:
        standings = client.get_standings()
        if standings is None:
            raise HTTPException(status_code=404, detail="Standings not found")
        
        # Filter by division if specified
        if division_id is not None:
            standings = [team for team in standings if team.get('division_id') == division_id]
        
        # Sort standings by wins and then points_for
        standings.sort(
            key=lambda team: (team.get('wins', 0), team.get('points_for', 0)),
            reverse=True
        )
        
        return paginate_results(standings, page, page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/league/scoreboard")
def get_scoreboard(week: Optional[int] = None):
    """Get scoreboard for specific week or current week."""
    try:
        scoreboard = client.get_scoreboard(matchup_period=week)
        if scoreboard is None:
            raise HTTPException(status_code=404, detail="Scoreboard not found")
        return scoreboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/league/fantasycast")
def get_fantasycast(
    page: int = Query(1, gt=0),
    page_size: int = Query(10, gt=0, le=50)
):
    """Get live scoring and detailed game information."""
    try:
        box_scores = client.get_box_scores()  # Using box_scores instead of fantasycast
        if box_scores is None:
            raise HTTPException(status_code=404, detail="Fantasycast data not found")
        return paginate_results(box_scores, page, page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Team Endpoints
@router.get("/teams")
def get_all_teams(
    page: int = Query(1, gt=0),
    page_size: int = Query(10, gt=0, le=50),
    division_id: Optional[int] = None
):
    """Get all teams in the league with pagination."""
    try:
        teams = client.league.teams
        if not teams:
            raise HTTPException(status_code=404, detail="No teams found")
        
        # Convert teams to serializable format
        teams_data = []
        for team in teams:
            if division_id is not None and team.division_id != division_id:
                continue
                
            team_data = {
                'team_id': team.team_id,
                'team_name': team.team_name,
                'division_id': team.division_id,
                'division_name': team.division_name,
                'wins': team.wins,
                'losses': team.losses,
                'ties': team.ties,
                'points_for': float(team.points_for) if team.points_for else 0,
                'points_against': float(team.points_against) if team.points_against else 0,
                'standing': team.standing,
                'roster_size': len(team.roster) if team.roster else 0,
                'logo_url': team.logo_url if hasattr(team, 'logo_url') else None
            }
            teams_data.append(team_data)
        
        # Sort teams by standing
        teams_data.sort(key=lambda x: x['standing'])
        
        return paginate_results(teams_data, page, page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/team/{team_id}")
def get_team(team_id: int, include_schedule: bool = False, include_roster: bool = True):
    """Get detailed team information."""
    try:
        team = client.get_team(team_id)
        if team is None:
            raise HTTPException(status_code=404, detail="Team not found")
        
        team_data = {
            'team_id': team['team_id'],
            'team_name': team['team_name'],
            'division_id': team['division_id'],
            'division_name': team['division_name'],
            'wins': team['wins'],
            'losses': team['losses'],
            'ties': team['ties'],
            'points_for': team['points_for'],
            'points_against': team['points_against'],
            'standing': team['standing'],
            'logo_url': team['logo_url']
        }
        
        if include_roster and 'roster' in team:
            team_data['roster'] = [{
                'name': player['name'],
                'position': player['position'],
                'proTeam': player['proTeam'],
                'injuryStatus': player['injuryStatus'],
                'total_points': player.get('total_points', 0),
                'avg_points': player.get('avg_points', 0)
            } for player in team['roster']]
            
        if include_schedule and 'schedule' in team:
            team_data['schedule'] = [{
                'week': idx + 1,
                'opponent': matchup['opponent'],
                'is_home': matchup['is_home'],
                'score': matchup['score'],
                'opponent_score': matchup['opponent_score']
            } for idx, matchup in enumerate(team['schedule'])]
            
        return team_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/players/stats/{player_id}")
def get_player_stats(player_id: int):
    """Get detailed player statistics."""
    try:
        player = client.get_player_info(player_ids=player_id)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        return player[0]  # Assuming get_player_info returns a list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/players/compare")
def compare_players(player1_id: int, player2_id: int):
    """Compare two players' statistics."""
    try:
        players = client.get_player_info(player_ids=[player1_id, player2_id])
        if not players or len(players) < 2:
            raise HTTPException(status_code=404, detail="One or both players not found")
        return {
            'player1': players[0],
            'player2': players[1]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/players/rankings")
def get_player_rankings(position: Optional[str] = None):
    """Get player rankings, optionally filtered by position."""
    try:
        all_players = []
        for team in client.league.teams:
            all_players.extend(team.roster)
        
        players_data = client.get_player_info(player_ids=[p.playerId for p in all_players])
        if not players_data:
            raise HTTPException(status_code=404, detail="No players found")
        
        if position:
            players_data = [p for p in players_data if p['position'] == position]
        
        players_data.sort(key=lambda x: x['total_points'], reverse=True)
        return players_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/players/hot-cold")
def get_hot_cold_players():
    """Get lists of hot and cold players based on recent performance."""
    try:
        all_players = []
        for team in client.league.teams:
            all_players.extend(team.roster)
        
        players_data = client.get_player_info(player_ids=[p.playerId for p in all_players])
        if not players_data:
            raise HTTPException(status_code=404, detail="No players found")
        
        hot_players = sorted(players_data, key=lambda x: x['total_points'], reverse=True)[:10]
        cold_players = sorted(players_data, key=lambda x: x['total_points'])[:10]
        
        return {
            'hot_players': hot_players,
            'cold_players': cold_players
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))