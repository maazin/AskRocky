#!/bin/zsh
#
# Same as run_local.sh, but starts both servers detached and writes their
# output to flask.log / vite.log instead of holding the terminal.
#
#   ./start.sh            # default ports: API 8000, client 5173
#   PORT=8010 ./start.sh  # override the API port if 8000 is taken
#
echo "🚀 Starting AskRocky Servers..."
echo ""

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

# Load environment variables if .env exists (do not commit secrets)
if [ -f .env ]; then
    echo "Loading environment from .env"
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
fi

API_PORT="${PORT:-8000}"
CLIENT_PORT="${CLIENT_PORT:-5173}"

# Stop only the servers this script starts -- a bare `pkill -f vite` would
# also kill unrelated Vite projects running on this machine.
echo "Stopping any previous AskRocky servers..."
pkill -f "$ROOT_DIR/.venv311/bin/python api/index.py" 2>/dev/null
pkill -f "$ROOT_DIR/api/index.py" 2>/dev/null
sleep 1

PYTHON="./.venv311/bin/python"
if [ ! -x "$PYTHON" ]; then
    echo "❌ ./.venv311/bin/python is missing. Create the virtualenv first:"
    echo "     python3.11 -m venv .venv311 && ./.venv311/bin/pip install -r requirements.txt"
    exit 1
fi

if lsof -nP -iTCP:"$API_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "❌ Port $API_PORT is already in use by:"
    lsof -nP -iTCP:"$API_PORT" -sTCP:LISTEN | tail -n +2 | awk '{print "     " $1 " (pid " $2 ")"}'
    echo "   Free it, or pick another port, e.g.:  PORT=8011 ./start.sh"
    exit 1
fi

export VITE_SERVER="${VITE_SERVER:-http://localhost:$API_PORT/api/chat}"

echo "Starting Flask API on port $API_PORT..."
PORT="$API_PORT" $PYTHON api/index.py > flask.log 2>&1 &
FLASK_PID=$!
echo "Flask PID: $FLASK_PID"

# Poll /health rather than sleeping a fixed number of seconds.
for i in $(seq 1 60); do
    curl -sf --max-time 2 "http://localhost:$API_PORT/health" >/dev/null 2>&1 && break
    if ! kill -0 $FLASK_PID 2>/dev/null; then
        echo "❌ Flask API exited during startup. Last lines of flask.log:"
        tail -20 flask.log
        exit 1
    fi
    sleep 1
done

if curl -sf --max-time 2 "http://localhost:$API_PORT/health" >/dev/null 2>&1; then
    echo "✅ Flask API is running on http://localhost:$API_PORT"
else
    echo "❌ Flask API did not respond within 60s. Check flask.log for errors:"
    tail -20 flask.log
    kill $FLASK_PID 2>/dev/null
    exit 1
fi

echo ""
echo "Starting Vite client on port $CLIENT_PORT..."
cd client
npm run dev -- --port "$CLIENT_PORT" > ../vite.log 2>&1 &
VITE_PID=$!
cd "$ROOT_DIR"
echo "Vite PID: $VITE_PID"
sleep 3

echo ""
echo "✅ Both servers are running!"
echo ""
echo "Flask API:   http://localhost:$API_PORT   (health: /health)"
echo "Vite Client: http://localhost:$CLIENT_PORT"
echo ""
echo "Open http://localhost:$CLIENT_PORT in your browser"
echo ""
echo "To stop servers:"
echo "  kill $FLASK_PID $VITE_PID"
echo ""
echo "To view logs:"
echo "  tail -f $ROOT_DIR/flask.log"
echo "  tail -f $ROOT_DIR/vite.log"
