#!/bin/zsh
#
# Start the AskRocky backend (Flask) and frontend (Vite) for local development.
#
#   ./run_local.sh            # default ports: API 8000, client 5173
#   PORT=8010 ./run_local.sh  # override the API port if 8000 is taken
#
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "🚀 Starting AskRocky..."
echo ""

# Load .env if present
if [ -f .env ]; then
	echo "Loading environment from .env"
	set -a
	source .env
	set +a
fi

API_PORT="${PORT:-8000}"
CLIENT_PORT="${CLIENT_PORT:-5173}"

# Choose Python interpreter -- the pinned deps need 3.11, not the system 3.13.
PYTHON="./.venv311/bin/python"
if [ ! -x "$PYTHON" ]; then
	echo "❌ ./.venv311/bin/python is missing. Create the virtualenv first:"
	echo "     python3.11 -m venv .venv311 && ./.venv311/bin/pip install -r requirements.txt"
	exit 1
fi

# Refuse to start on a port something else already owns, rather than
# reporting success while Flask silently fails to bind.
if lsof -nP -iTCP:"$API_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
	echo "❌ Port $API_PORT is already in use by:"
	lsof -nP -iTCP:"$API_PORT" -sTCP:LISTEN | tail -n +2 | awk '{print "     " $1 " (pid " $2 ")"}'
	echo "   Free it, or pick another port, e.g.:  PORT=8011 ./run_local.sh"
	exit 1
fi

if lsof -nP -iTCP:"$CLIENT_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
	echo "❌ Port $CLIENT_PORT is already in use. Try:  CLIENT_PORT=5174 ./run_local.sh"
	exit 1
fi

# Point the client at whichever port the API actually landed on.
export VITE_SERVER="${VITE_SERVER:-http://localhost:$API_PORT/api/chat}"

# Start Flask API
echo "Starting Flask API on port $API_PORT with $PYTHON..."
PORT="$API_PORT" $PYTHON api/index.py &
FLASK_PID=$!

trap 'echo ""; echo "Stopping servers..."; kill $FLASK_PID $VITE_PID 2>/dev/null || true' INT TERM

# Wait for the API to answer, instead of a blind sleep.
echo -n "Waiting for the API to come up"
for i in $(seq 1 60); do
	if curl -sf --max-time 2 "http://localhost:$API_PORT/health" >/dev/null 2>&1; then
		echo " ✅"
		break
	fi
	if ! kill -0 $FLASK_PID 2>/dev/null; then
		echo ""
		echo "❌ The Flask API exited during startup. Scroll up for the traceback."
		exit 1
	fi
	echo -n "."
	sleep 1
done

if ! curl -sf --max-time 2 "http://localhost:$API_PORT/health" >/dev/null 2>&1; then
	echo ""
	echo "❌ The API did not respond on port $API_PORT within 60s."
	kill $FLASK_PID 2>/dev/null || true
	exit 1
fi

# Start Vite
echo ""
echo "Starting Vite client on port $CLIENT_PORT..."
cd client
npm run dev -- --port "$CLIENT_PORT" &
VITE_PID=$!
cd "$ROOT_DIR"

echo ""
echo "✅ Servers started!"
echo ""
echo "📍 URLs:"
echo "   Frontend: http://localhost:$CLIENT_PORT"
echo "   Backend:  http://localhost:$API_PORT   (health: /health)"
echo ""
echo "ℹ️  The embedding model loads in the background; /health reports"
echo "   \"ready\": true once the knowledge base is live. Until then answers"
echo "   come from the LLM alone, without USF sources."
echo ""
echo "⚠️  Keep this terminal open. Press Ctrl+C to stop all servers."
echo ""

wait
