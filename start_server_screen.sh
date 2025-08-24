#!/bin/bash

# Alternative approach using screen/tmux for persistence

SERVER_SCRIPT="run_tornado_server.py"
PID_FILE="tornado_server.pid"
LOG_FILE="tornado_server.log"
SESSION_NAME="tornado_server"

# Default arguments
HOST="0.0.0.0"
PORT="8767"
MAX_CONNECTIONS="200"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --max-connections)
            MAX_CONNECTIONS="$2"
            shift 2
            ;;
        --pid-file)
            PID_FILE="$2"
            shift 2
            ;;
        --log-file)
            LOG_FILE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

echo "Starting tornado server in persistent session..."
echo "Host: $HOST, Port: $PORT, Max connections: $MAX_CONNECTIONS"

# Kill any existing session
screen -S "$SESSION_NAME" -X quit 2>/dev/null || true
tmux kill-session -t "$SESSION_NAME" 2>/dev/null || true

if command -v screen >/dev/null 2>&1; then
    echo "Using screen for persistent session..."
    
    # Start server in detached screen session
    screen -dmS "$SESSION_NAME" bash -c "
        python3 '$SERVER_SCRIPT' \
            --host '$HOST' \
            --port '$PORT' \
            --max-connections '$MAX_CONNECTIONS' \
            > '$LOG_FILE' 2>&1 &
        PID=\$!
        echo \$PID > '$PID_FILE'
        echo 'Server started in screen with PID: '\$PID
        wait \$PID
    "
    
    sleep 2
    
    # Check if screen session exists
    if screen -list | grep -q "$SESSION_NAME"; then
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            echo "✅ Server started in screen session '$SESSION_NAME' with PID: $PID"
            echo "You can attach with: screen -r $SESSION_NAME"
        fi
    else
        echo "❌ Failed to create screen session"
        exit 1
    fi

elif command -v tmux >/dev/null 2>&1; then
    echo "Using tmux for persistent session..."
    
    # Start server in detached tmux session
    tmux new-session -d -s "$SESSION_NAME" bash -c "
        python3 '$SERVER_SCRIPT' \
            --host '$HOST' \
            --port '$PORT' \
            --max-connections '$MAX_CONNECTIONS' \
            > '$LOG_FILE' 2>&1 &
        PID=\$!
        echo \$PID > '$PID_FILE'
        echo 'Server started in tmux with PID: '\$PID
        wait \$PID
    "
    
    sleep 2
    
    # Check if tmux session exists
    if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            echo "✅ Server started in tmux session '$SESSION_NAME' with PID: $PID"
            echo "You can attach with: tmux attach-session -t $SESSION_NAME"
        fi
    else
        echo "❌ Failed to create tmux session"
        exit 1
    fi

else
    echo "❌ Neither screen nor tmux available"
    echo "Falling back to daemon script..."
    exec ./start_server_daemon.sh "$@"
fi