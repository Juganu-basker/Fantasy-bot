#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BLUE='\033[0;34m'

# Base URL
BASE_URL="http://localhost:3000/api/espn"

echo -e "${BLUE}Testing ESPN API Integration${NC}"

# Test with different views
VIEWS=("mTeam" "mRoster" "mMatchup" "mSettings")

for view in "${VIEWS[@]}"
do
    echo -e "\n${BLUE}Testing with view: ${view}${NC}"
    echo -e "${BLUE}URL: ${BASE_URL}/test?view=${view}${NC}\n"
    
    curl -s -X GET "${BASE_URL}/test?view=${view}" \
        -H "Accept: application/json" \
        | python3 -m json.tool
    
    echo -e "\n${BLUE}Waiting 2 seconds before next request...${NC}"
    sleep 2
done

echo -e "\n${BLUE}Tests completed${NC}"
