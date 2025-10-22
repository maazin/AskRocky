#!/bin/bash

cd ~/Desktop/Mac/Programs/AskRocky/bullbot

echo "🚀 Starting Bull Bot..."
echo ""

# Start Flask API
echo "Starting Flask API..."
python api/index.py &
FLASK_PID=$!

echo "Flask started with PID: $FLASK_PID"
echo "Waiting for Flask to initialize..."
sleep 5

# Start Vite
echo ""
echo "Starting Vite client..."
cd client
npm run dev &
VITE_PID=$!

echo "Vite started with PID: $VITE_PID"
echo ""
echo "✅ Servers started!"
echo ""
echo "📍 URLs:"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000"
echo ""
echo "⚠️  Keep this terminal open. Press Ctrl+C to stop all servers."
echo ""

# Wait for user to stop
wait
