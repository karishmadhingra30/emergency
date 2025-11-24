#!/bin/bash

# Emergency Shelter Chatbot Stop Script
# This script stops all running services

echo "======================================"
echo "Stopping Emergency Shelter Chatbot"
echo "======================================"
echo ""

# Check if PID file exists
if [ -f ".chatbot_pids" ]; then
    PIDS=$(cat .chatbot_pids)
    echo "Stopping processes: $PIDS"

    for PID in $PIDS; do
        if ps -p $PID > /dev/null; then
            echo "Killing process $PID"
            kill $PID
        else
            echo "Process $PID not running"
        fi
    done

    rm .chatbot_pids
    echo ""
    echo "All services stopped!"
else
    echo "No PID file found. Searching for processes..."

    # Try to find and kill processes by port
    RASA_PID=$(lsof -ti:5005)
    ACTIONS_PID=$(lsof -ti:5055)
    FLASK_PID=$(lsof -ti:5000)

    [ ! -z "$RASA_PID" ] && kill $RASA_PID && echo "Stopped Rasa server"
    [ ! -z "$ACTIONS_PID" ] && kill $ACTIONS_PID && echo "Stopped Rasa actions"
    [ ! -z "$FLASK_PID" ] && kill $FLASK_PID && echo "Stopped Flask backend"

    echo ""
    echo "Done!"
fi
