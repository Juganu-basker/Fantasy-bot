#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BLUE='\033[0;34m'

# Base URL
BASE_URL="http://localhost:3000/api"

# Function to make a curl request and format the response
make_request() {
    local endpoint=$1
    local description=$2
    
    echo -e "\n${BLUE}Testing: ${description}${NC}"
    echo -e "${BLUE}Endpoint: ${endpoint}${NC}\n"
    
    response=$(curl -s -w "\n%{http_code}" "${BASE_URL}${endpoint}" \
        -H "Accept: application/json")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -eq 200 ]; then
        echo -e "${GREEN}Status: ${http_code}${NC}"
        echo "$body" | python3 -m json.tool
    else
        echo -e "${RED}Status: ${http_code}${NC}"
        echo "$body" | python3 -m json.tool
    fi
}

echo -e "${BLUE}Starting API Tests...${NC}"

# Test 1: Basic API Connection
make_request "/espn/test" "Basic API Connection Test"

# Test 2: League Data
make_request "/espn/league" "League Data"

# Test 3: League Data with View Parameter
make_request "/espn/league?view=mRoster" "League Data with Roster View"

echo -e "\n${BLUE}API Tests Completed${NC}"
