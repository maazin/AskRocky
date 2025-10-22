#!/bin/bash

echo "🚀 Starting Bull Bot Servers..."
echo ""

# Change to project directory
cd ~/Desktop/Mac/Programs/AskRocky/bullbot

# Kill any existing processes
echo "Stopping any existing servers..."
pkill -f "python api/index.py" 2>/dev/null
pkill -f "vite" 2>/dev/null
sleep 2

# Start Flask API
echo "Starting Flask API on port 8000..."
python api/index.py > flask.log 2>&1 &
FLASK_PID=$!
echo "Flask PID: $FLASK_PID"

# Wait for Flask to start
sleep 5

# Test Flask
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ Flask API is running on http://localhost:8000"
else
    echo "❌ Flask API failed to start. Check flask.log for errors:"
    tail -20 flask.log
    exit 1
fi

# Start Vite
echo ""
echo "Starting Vite client on port 5173..."
cd client
npm run dev > ../vite.log 2>&1 &
VITE_PID=$!
echo "Vite PID: $VITE_PID"

# Wait for Vite to start
sleep 5

echo ""
echo "✅ Both servers should be running!"
echo ""
echo "Flask API: http://localhost:8000"
echo "Vite Client: http://localhost:5173"
echo ""
echo "Open http://localhost:5173 in your browser"
echo ""
echo "To stop servers:"
echo "  kill $FLASK_PID $VITE_PID"
echo ""
echo "To view logs:"
echo "  tail -f ~/Desktop/Mac/Programs/AskRocky/bullbot/flask.log"
echo "  tail -f ~/Desktop/Mac/Programs/AskRocky/bullbot/vite.log"
