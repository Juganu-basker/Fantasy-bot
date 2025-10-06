from espn_api.basketball import League
from typing import Optional, List, Dict, Any, Set, Union
import os
from dotenv import load_dotenv
from logger_config import setup_logger
from fastapi import HTTPException

# Set up logger
logger = setup_logger('espn_client', 'espn_client.log')

load_dotenv()

class ESPNClient:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ESPNClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            logger.info("Initializing ESPNClient")
            self.league_id = int(os.getenv("LEAGUE_ID", 9490871))
            self.season = int(os.getenv("SEASON", 2026))
            self.swid = os.getenv("SWID", "{7AF162F7-20D2-4158-A314-9967A442227B}")
            self.espn_s2 = os.getenv("ESPN_S2", "AEAB07jbWUzo7x%2BY7FfULVtdVyimJomXDl6Zs65DYUBwVbPVg7BqvY7yUrZncqJrl3Ssx%2BQsDor6sRx1Wr2mS%2FrkhBHfXAQy2bWMEe9R76i3HcXenpGUN%2FxdTl2KGvSM%2B%2B7F0C008d0JTFXd2VwqVErrX15jO4UOagLO3DDEsNmRgEdY1AlkxYELWELWELPyPZHonrF2aP5H4KHt%2BfBQe%2BzKAcoHf%2FE5CYZJSIrKWLJpZeF7bqqOvIsSBFl0%2FuEPavC7EVmoB1HbZjztR7Fld%2B8%2BMZw")

            try:
                logger.info(f"Connecting to ESPN Fantasy League {self.league_id} for season {self.season}")
                self.league = League(league_id=self.league_id,
                                    year=self.season,
                                    espn_s2=self.espn_s2,
                                    swid=self.swid)
                self._initialized = True
                logger.info("Successfully initialized ESPNClient")
            except Exception as e:
                logger.error(f"Error initializing league: {str(e)}")
                raise

    def get_standings(self) -> List[Dict[str, Any]]:
        """Get current league standings."""
        try:
            logger.info("Fetching league standings")
            standings = self.league.standings()
            if not standings:
                logger.warning("No standings data found")
                return None
            
            standings_data = []
            for team in standings:
                logger.debug(f"Processing standings data for team {team.team_name}")
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
                    'streak_length': int(team.streak_length) if hasattr(team, 'streak_length') else 0,
                    'streak_type': team.streak_type if hasattr(team, 'streak_type') else None,
                    'standing': int(team.standing) if team.standing else 0,
                    'games_back': float(team.games_back) if hasattr(team, 'games_back') else 0,
                    'final_standing': int(team.final_standing) if team.final_standing else 0,
                    'waiver_position': int(team.waiver_position) if hasattr(team, 'waiver_position') else 0,
                    'number_of_moves': int(team.number_of_moves) if hasattr(team, 'number_of_moves') else 0,
                    'number_of_trades': int(team.number_of_trades) if hasattr(team, 'number_of_trades') else 0,
                    'roster_moves': int(team.roster_moves) if hasattr(team, 'roster_moves') else 0,
                    'clinched_playoffs': bool(team.clinched_playoffs) if hasattr(team, 'clinched_playoffs') else False,
                    'logo_url': team.logo_url if hasattr(team, 'logo_url') else None,
                }
                standings_data.append(team_data)
            
            logger.info(f"Successfully retrieved standings for {len(standings_data)} teams")
            return standings_data
        except Exception as e:
            logger.error(f"Error getting standings: {str(e)}")
            return None

    def get_free_agents(self, position: Optional[str] = None, size: int = 50) -> List[Dict[str, Any]]:
        """Get list of free agents, optionally filtered by position."""
        try:
            free_agents = self.league.free_agents(position=position, size=size)
            return [{
                'name': getattr(player, 'name', None),
                'position': getattr(player, 'position', None),
                'proTeam': getattr(player, 'proTeam', None),
                'injuryStatus': getattr(player, 'injuryStatus', None),
                'stats': getattr(player, 'stats', {}),
                'total_points': getattr(player, 'total_points', 0),
                'avg_points': getattr(player, 'avg_points', 0),
                'percent_owned': getattr(player, 'percent_owned', 0),
                'percent_started': getattr(player, 'percent_started', 0),
                'projected_points': getattr(player, 'projected_points', 0)
            } for player in free_agents]
        except Exception as e:
            print(f"Error getting free agents: {str(e)}")
            return None

    def get_transactions(self, 
                        scoring_period: Optional[int] = None, 
                        types: Set[str] = {"FREEAGENT", "WAIVER", "TRADE"}) -> List[Dict[str, Any]]:
        """Get list of transactions."""
        try:
            transactions = self.league.transactions(scoring_period=scoring_period, types=types)
            return [{
                'type': getattr(trans, 'type', None),
                'team': getattr(trans.team, 'team_name', None) if trans.team else None,
                'player': getattr(trans.player, 'name', None) if trans.player else None,
                'bid_amount': getattr(trans, 'bid_amount', None),
                'status': getattr(trans, 'status', None),
                'date': getattr(trans, 'date', None)
            } for trans in transactions]
        except Exception as e:
            print(f"Error getting transactions: {str(e)}")
            return None

    def get_scoreboard(self, matchup_period: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get scoreboard for specific week or current week."""
        try:
            matchups = self.league.scoreboard(matchupPeriod=matchup_period)
            if not matchups:
                return None
                
            return [{
                'matchup_id': getattr(m, 'matchup_id', None),
                'home_team': {
                    'team_id': getattr(m.home_team, 'team_id', None),
                    'team_name': getattr(m.home_team, 'team_name', None),
                    'score': getattr(m, 'home_score', 0),
                    'projected': getattr(m, 'home_projected', 0)
                },
                'away_team': {
                    'team_id': getattr(m.away_team, 'team_id', None) if m.away_team else None,
                    'team_name': getattr(m.away_team, 'team_name', None) if m.away_team else None,
                    'score': getattr(m, 'away_score', 0),
                    'projected': getattr(m, 'away_projected', 0)
                }
            } for m in matchups]
        except Exception as e:
            print(f"Error getting scoreboard: {str(e)}")
            return None

    def get_box_scores(self, 
                      matchup_period: Optional[int] = None, 
                      scoring_period: Optional[int] = None, 
                      matchup_total: bool = True) -> List[Dict[str, Any]]:
        """Get detailed box scores with player stats."""
        try:
            box_scores = self.league.box_scores(
                matchup_period=matchup_period,
                scoring_period=scoring_period,
                matchup_total=matchup_total
            )
            if not box_scores:
                return None
                
            return [{
                'home_team': {
                    'team_id': getattr(bs.home_team, 'team_id', None),
                    'team_name': getattr(bs.home_team, 'team_name', None),
                    'score': getattr(bs, 'home_score', 0),
                    'projected': getattr(bs, 'home_projected', 0),
                    'lineup': [{
                        'name': getattr(p, 'name', None),
                        'position': getattr(p, 'position', None),
                        'points': getattr(p, 'points', 0),
                        'projected': getattr(p, 'projected_points', 0),
                        'stats': getattr(p, 'stats', {}),
                        'injuryStatus': getattr(p, 'injuryStatus', None),
                        'starting': getattr(p, 'starting', False),
                        'proTeam': getattr(p, 'proTeam', None)
                    } for p in getattr(bs, 'home_lineup', [])]
                },
                'away_team': {
                    'team_id': getattr(bs.away_team, 'team_id', None),
                    'team_name': getattr(bs.away_team, 'team_name', None),
                    'score': getattr(bs, 'away_score', 0),
                    'projected': getattr(bs, 'away_projected', 0),
                    'lineup': [{
                        'name': getattr(p, 'name', None),
                        'position': getattr(p, 'position', None),
                        'points': getattr(p, 'points', 0),
                        'projected': getattr(p, 'projected_points', 0),
                        'stats': getattr(p, 'stats', {}),
                        'injuryStatus': getattr(p, 'injuryStatus', None),
                        'starting': getattr(p, 'starting', False),
                        'proTeam': getattr(p, 'proTeam', None)
                    } for p in getattr(bs, 'away_lineup', [])]
                }
            } for bs in box_scores]
        except Exception as e:
            print(f"Error getting box scores: {str(e)}")
            return None

    def get_player_info(self, 
                       name: Optional[str] = None, 
                       player_ids: Optional[Union[int, List[int]]] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Get detailed player information. Can fetch multiple players at once."""
        try:
            logger.info(f"Fetching player information for player IDs: {player_ids}")
            players = self.league.player_info(
                name=name,
                playerId=player_ids
            )
            
            if not players:
                logger.warning("No player data found")
                raise HTTPException(status_code=404, detail="Player not found")
                
            if not isinstance(players, list):
                players = [players]
                
            player_data = [{
                'name': getattr(p, 'name', None),
                'position': getattr(p, 'position', None),
                'proTeam': getattr(p, 'proTeam', None),
                'injuryStatus': getattr(p, 'injuryStatus', None),
                'stats': getattr(p, 'stats', {}),
                'total_points': getattr(p, 'total_points', 0),
                'avg_points': getattr(p, 'avg_points', 0),
                'percent_owned': getattr(p, 'percent_owned', 0),
                'percent_started': getattr(p, 'percent_started', 0),
                'projected_points': getattr(p, 'projected_points', 0)
            } for p in players]
            
            logger.info(f"Successfully retrieved player information for {len(player_data)} players")
            return player_data
        except Exception as e:
            logger.error(f"Error getting player info: {str(e)}")
            return None

    def get_team(self, team_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed team information."""
        try:
            logger.info(f"Fetching team information for team ID {team_id}")
            team = self.league.get_team_data(team_id)
            if not team:
                logger.warning(f"Team ID {team_id} not found")
                return None
            
            team_data = {
                'team_id': getattr(team, 'team_id', None),
                'team_name': getattr(team, 'team_name', None),
                'division_id': getattr(team, 'division_id', None),
                'division_name': getattr(team, 'division_name', None),
                'wins': getattr(team, 'wins', 0),
                'losses': getattr(team, 'losses', 0),
                'ties': getattr(team, 'ties', 0),
                'points_for': float(getattr(team, 'points_for', 0)),
                'points_against': float(getattr(team, 'points_against', 0)),
                'standing': getattr(team, 'standing', 0),
                'logo_url': getattr(team, 'logo_url', None)
            }
            logger.info(f"Successfully retrieved team information for {team_data['team_name']}")
            return team_data
        except Exception as e:
            logger.error(f"Error getting team info: {str(e)}")
            return None