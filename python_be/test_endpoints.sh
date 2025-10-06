#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color
YELLOW='\033[1;33m'

# Base URL
BASE_URL="http://localhost:8000/api/v1"

# Function to make requests and check response
make_request() {
    local endpoint=$1
    local description=$2
    local method=${3:-GET}
    
    echo -e "\n${YELLOW}Testing: ${description}${NC}"
    echo "Endpoint: ${endpoint}"
    
    response=$(curl -s -w "\n%{http_code}" -X ${method} "${BASE_URL}${endpoint}")
    status_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | sed '$d')
    
    if [ "$status_code" -ge 200 ] && [ "$status_code" -lt 300 ]; then
        echo -e "${GREEN}✓ Success (HTTP ${status_code})${NC}"
    else
        echo -e "${RED}✗ Failed (HTTP ${status_code})${NC}"
        echo "Response: $response_body"
    fi
}

# Function to test pagination
test_pagination() {
    local endpoint=$1
    local description=$2
    
    echo -e "\n${YELLOW}Testing Pagination: ${description}${NC}"
    
    # Test different page sizes
    make_request "${endpoint}?page=1&page_size=5" "Page 1, Size 5"
    make_request "${endpoint}?page=2&page_size=5" "Page 2, Size 5"
    make_request "${endpoint}?page=1&page_size=10" "Page 1, Size 10"
}

echo "Starting API Tests..."

# League Info
# make_request "/league/info" "Get League Information"

# Standings
make_request "/league/standings" "Get League Standings"
test_pagination "/league/standings" "Standings Pagination"

# Teams
make_request "/teams" "Get All Teams"
test_pagination "/teams" "Teams Pagination"
make_request "/team/1" "Get Single Team"
make_request "/team/1?include_schedule=true" "Get Team with Schedule"
make_request "/team/1?include_roster=true" "Get Team with Roster"

# Scoreboard
make_request "/league/scoreboard" "Get Current Scoreboard"
make_request "/league/scoreboard?week=1" "Get Week 1 Scoreboard"

# Fantasycast
make_request "/league/fantasycast" "Get Fantasycast"
test_pagination "/league/fantasycast" "Fantasycast Pagination"

# Player Stats
make_request "/players/stats/3112335" "Get Player Stats"
make_request "/players/compare?player1_id=3112335&player2_id=3945274" "Compare Players"
make_request "/players/rankings?position=PG" "Get Player Rankings"
# make_request "/players/news" "Get Player News"
make_request "/players/hot-cold" "Get Hot/Cold Players"

# Activity
# make_request "/league/activity" "Get Recent Activity"
test_pagination "/league/activity" "Activity Pagination"

echo -e "\n${GREEN}All tests completed!${NC}"
