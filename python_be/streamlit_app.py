import streamlit as st
import requests
from player_stats import calculate_player_stats
from espn_client import ESPNClient

st.title('FantasyBot Frontend')

# Initialize ESPNClient
client = ESPNClient()

# Input for player ID
def get_player_stats(player_id):
    player_data = client.get_player_info(player_ids=player_id)
    if player_data:
        return calculate_player_stats(player_data[0])
    else:
        st.error('Player not found or error fetching data')
        return None

player_id = st.text_input('Enter Player ID to search for stats:')
if player_id:
    player_stats = get_player_stats(int(player_id))
    if player_stats:
        st.write('Player Stats:', player_stats)

# Input for comparing two players
def compare_players(player1_id, player2_id):
    player1_data = client.get_player_info(player_ids=player1_id)
    player2_data = client.get_player_info(player_ids=player2_id)
    if player1_data and player2_data:
        return player1_data[0], player2_data[0]
    else:
        st.error('Error comparing players')
        return None, None

player1_id = st.text_input('Enter Player 1 ID for comparison:')
player2_id = st.text_input('Enter Player 2 ID for comparison:')
if player1_id and player2_id:
    player1, player2 = compare_players(int(player1_id), int(player2_id))
    if player1 and player2:
        st.write('Player 1:', player1)
        st.write('Player 2:', player2)

# Add search by player name
def search_player_by_name(name):
    players = client.get_player_info(name=name)
    if players:
        return players
    else:
        st.error('No players found with that name')
        return []

player_name = st.text_input('Enter Player Name to search:')
if player_name:
    players = search_player_by_name(player_name)
    if players:
        for player in players:
            st.write('Player:', player)

# Display scoreboards
def display_scoreboard(week=None):
    scoreboard = client.get_scoreboard(matchup_period=week)
    if scoreboard:
        for match in scoreboard:
            st.write(f"Matchup ID: {match['matchup_id']}")
            st.write(f"Home Team: {match['home_team']['team_name']} - Score: {match['home_team']['score']}")
            st.write(f"Away Team: {match['away_team']['team_name']} - Score: {match['away_team']['score']}")
            st.write('---')
    else:
        st.error('No scoreboard data available')

week = st.number_input('Enter Week for Scoreboard:', min_value=1, step=1)
if st.button('Show Scoreboard'):
    display_scoreboard(week)

# List teams for player comparison
def list_teams():
    teams = client.get_all_teams()
    if teams:
        for team in teams:
            st.write(f"Team ID: {team['team_id']} - Name: {team['team_name']}")
    else:
        st.error('No teams data available')

if st.button('List Teams'):
    list_teams()

# Display player news (using hot and cold players as news)
def display_player_news():
    news = client.get_hot_cold_players()
    if news:
        st.write('Hot Players:')
        for player in news['hot_players']:
            st.write(player['name'])
        st.write('Cold Players:')
        for player in news['cold_players']:
            st.write(player['name'])
    else:
        st.error('No player news available')

if st.button('Show Player News'):
    display_player_news()
