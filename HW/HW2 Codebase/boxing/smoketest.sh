#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5002/api"

# Flag to control whether to echo JSON output
ECHO_JSON=true

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################


# /health
# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# /db-check
# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}


###############################################
#
# Boxer Management
#
###############################################


# /add-boxer
add_boxer() {
    name=$1
    weight=$2
    height=$3
    reach=$4
    age=$5

    echo "Adding boxer $name to the gym..."
    curl -s -X POST "$BASE_URL/add-boxer" -H "Content-Type: application/json" \
        -d "{\"name\":\"$name\", \"weight\":$weight, \"height\":$height, \"reach\":$reach, \"age\":$age}" | grep -q '"status": "success"'

    if [ $? -eq 0 ]; then
        echo "Boxer added successfully."
    else
        echo "Failed to add boxer."
        exit 1
    fi
}

# /get-boxer-by-name/<string:boxer_name>
get_boxer_by_name() {
    boxer_name=$1

    echo "Getting boxer by name ($boxer_name)..."
    response=$(curl -s -X GET "$BASE_URL/get-boxer-by-name/$boxer_name")

    if echo "$response" | grep -q '"status": "success"'; then
        echo "Boxer retrieved successfully by name ($boxer_name)."
        if [ "$ECHO_JSON" = true ]; then
        echo "Boxer JSON (name $boxer_name):"
        echo "$response" | jq .
        fi
    else
        echo "Failed to get boxer by name ($boxer_name)."
        exit 1
    fi
}

# /leaderboard
# ordered by wins, descending
get_leaderboard_ordered_by_wins() {
    echo "Getting the leaderboard (ordered by wins)..."
    response=$(curl -s -X GET "$BASE_URL/leaderboard") # 'wins' is the default option

    if echo "$response" | grep -q '"status": "success"'; then
        echo "Leaderboard retrieved successfully."
        if [ "$ECHO_JSON" = true ]; then
        echo "Leaderboard JSON:"
        echo "$response" | jq .
        fi
    else
        echo "Failed to get leaderboard."
        exit 1
    fi
}

# /leaderboard
# ordered by win_pct, descending
get_leaderboard_ordered_by_win_pct() {
    echo "Getting the leaderboard (ordered by win_pct)..."
    response=$(curl -s -X GET "$BASE_URL/leaderboard?sort=win_pct")

    if echo "$response" | grep -q '"status": "success"'; then
        echo "Leaderboard retrieved successfully."
        if [ "$ECHO_JSON" = true ]; then
        echo "Leaderboard JSON:"
        echo "$response" | jq .
        fi
    else
        echo "Failed to get leaderboard."
        exit 1
    fi
}


###############################################
#
# Ring Management
#
###############################################


# /clear-boxers
clear_boxers() {
  echo "Clearing boxers from the ring..."
  response=$(curl -s -X POST "$BASE_URL/clear-boxers")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxers cleared successfully. Ring is now empty."
  else
    echo "Failed to clear boxers."
    exit 1
  fi
}

# /get-boxers
get_boxers() {
  echo "Retrieving boxers from the ring..."
  response=$(curl -s -X GET "$BASE_URL/get-boxers")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxers retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxers JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve boxers from the ring."
    exit 1
  fi
}


###############################################
#
# Running smoketests
#
###############################################


# Health checks
check_health
check_db

# Boxer Management
#add_boxer "wiwiwi" 200 100 5 20 # commented out because it causes an error from adding duplicates
get_boxer_by_name "wiwiwi"
get_leaderboard_ordered_by_wins # may return an empty list, because a boxer needs to fight first to get on the leaderboard
get_leaderboard_ordered_by_win_pct

# Ring Management
clear_boxers
get_boxers