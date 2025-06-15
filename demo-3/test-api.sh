#!/bin/bash

# Color codes for better readability
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Set default message if none provided
MESSAGE_CONTENT="${*:-Hello World!}"
API_BASE_URL="http://localhost:8001"
HEALTH_ENDPOINT="${API_BASE_URL}/health"
CHAT_ENDPOINT="${API_BASE_URL}/chat"

echo -e "${CYAN}Testing AWS Workshop API server (Demo 1)...${NC}"
echo ""

# Function to check if server is responding
check_server_status() {
    # Test health endpoint with timeout
    if curl -s --connect-timeout 5 --max-time 10 "${HEALTH_ENDPOINT}" > /dev/null 2>&1; then
        return 0
    else
        echo -e "${RED}✗ Server is not responding or not started${NC}"
        echo -e "${YELLOW}Make sure to run ./start.sh first${NC}"
        return 1
    fi
}

# Function to test chat endpoint
test_chat_endpoint() {
    echo -e "${BLUE}Testing chat endpoint...${NC}"
    echo -e "${CYAN}POST ${CHAT_ENDPOINT}${NC}"
    
    response=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "${CHAT_ENDPOINT}" \
        -H "Content-Type: application/json" \
        -d "{\"content\":\"${MESSAGE_CONTENT}\"}")
    
    http_code=$(echo "$response" | grep "HTTP_CODE:" | cut -d: -f2)
    body=$(echo "$response" | sed '/HTTP_CODE:/d')
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ Chat endpoint successful (HTTP $http_code)${NC}"
        echo " "
        echo " $body" | jq
    else
        echo -e "${RED}✗ Chat endpoint failed (HTTP $http_code)${NC}"
        echo -e "${RED} $body${NC}"
    fi
    echo ""
}

# Main test execution
main() {
    if check_server_status; then
        echo ""
        test_chat_endpoint
        echo -e "${GREEN}✓ All tests completed${NC}"
    else
        echo -e "${RED}✗ Cannot proceed with tests - server not running${NC}"
        exit 1
    fi
}

# Run main function
main 