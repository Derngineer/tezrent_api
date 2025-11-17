#!/bin/bash

# TezRent Production API Test Script

API_URL="https://tezrentapibackend-bsatbme3eqfkfnc3.canadacentral-01.azurewebsites.net"

echo "🔐 Step 1: Login to get token"
echo "Enter your username:"
read USERNAME
echo "Enter your password:"
read -s PASSWORD

echo -e "\n📡 Getting token..."

# Get token
TOKEN_RESPONSE=$(curl -s -X POST "$API_URL/api/accounts/token/" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}")

echo "$TOKEN_RESPONSE" | jq '.' 2>/dev/null || echo "$TOKEN_RESPONSE"

# Extract token
TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"access":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to get token. Check credentials."
    exit 1
fi

echo -e "\n✅ Token received!"
echo "Token: ${TOKEN:0:20}..."

echo -e "\n📊 Step 2: Test revenue_summary endpoint"
curl -s "$API_URL/api/rentals/rentals/revenue_summary/" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

echo -e "\n�� Step 3: Test revenue_trends endpoint"
curl -s "$API_URL/api/rentals/rentals/revenue_trends/?period=daily" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

echo -e "\n✅ Done! If you see data above, the API is working correctly."
