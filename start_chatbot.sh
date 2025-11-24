#!/bin/bash

# Emergency Shelter Chatbot Startup Script
# This script starts all required services for the chatbot system

echo "======================================"
echo "Emergency Shelter Chatbot System"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Rasa model exists
if [ ! -d "chatbot/models" ] || [ -z "$(ls -A chatbot/models)" ]; then
    echo -e "${YELLOW}No Rasa model found. Training model first...${NC}"
    echo ""
    cd chatbot
    rasa train
    cd ..
    echo ""
fi

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${RED}Port $1 is already in use!${NC}"
        echo "Please stop the service using this port or change the configuration."
        return 1
    fi
    return 0
}

# Check required ports
echo "Checking ports..."
check_port 5005 || exit 1  # Rasa server
check_port 5055 || exit 1  # Rasa actions
check_port 5000 || exit 1  # Flask backend

echo -e "${GREEN}All ports available!${NC}"
echo ""

# Create log directory
mkdir -p logs

echo "Starting services..."
echo ""

# Start Rasa Actions Server
echo -e "${GREEN}[1/3] Starting Rasa Actions Server...${NC}"
cd chatbot
rasa run actions --port 5055 > ../logs/rasa_actions.log 2>&1 &
ACTIONS_PID=$!
cd ..
echo "Rasa Actions Server PID: $ACTIONS_PID"
sleep 3

# Start Rasa Server
echo -e "${GREEN}[2/3] Starting Rasa Server...${NC}"
cd chatbot
rasa run --enable-api --cors "*" --port 5005 > ../logs/rasa_server.log 2>&1 &
RASA_PID=$!
cd ..
echo "Rasa Server PID: $RASA_PID"
echo "Waiting for Rasa to initialize..."
sleep 10

# Start Flask Backend
echo -e "${GREEN}[3/3] Starting Flask Backend...${NC}"
python3 app.py > logs/flask.log 2>&1 &
FLASK_PID=$!
echo "Flask Backend PID: $FLASK_PID"
sleep 3

echo ""
echo "======================================"
echo -e "${GREEN}All services started successfully!${NC}"
echo "======================================"
echo ""
echo "Service URLs:"
echo "  • Web Interface:  http://localhost:5000"
echo "  • Rasa Server:    http://localhost:5005"
echo "  • Rasa Actions:   http://localhost:5055"
echo ""
echo "Process IDs:"
echo "  • Rasa Actions: $ACTIONS_PID"
echo "  • Rasa Server:  $RASA_PID"
echo "  • Flask:        $FLASK_PID"
echo ""
echo "Log files:"
echo "  • logs/rasa_actions.log"
echo "  • logs/rasa_server.log"
echo "  • logs/flask.log"
echo ""
echo "To stop all services, run:"
echo "  kill $ACTIONS_PID $RASA_PID $FLASK_PID"
echo ""
echo -e "${YELLOW}Opening browser in 3 seconds...${NC}"
sleep 3

# Try to open browser (works on most systems)
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:5000
elif command -v open > /dev/null; then
    open http://localhost:5000
else
    echo "Please open http://localhost:5000 in your browser"
fi

# Save PIDs to file for easy stopping
echo "$ACTIONS_PID $RASA_PID $FLASK_PID" > .chatbot_pids

echo ""
echo "Press Ctrl+C to stop monitoring logs..."
echo ""

# Monitor logs (optional)
tail -f logs/flask.log
