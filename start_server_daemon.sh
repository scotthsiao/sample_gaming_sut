#!/bin/bash

# Simple daemon script for tornado server
# This creates a truly detached process that survives Jenkins

SERVER_SCRIPT="run_tornado_server.py"
PID_FILE="tornado_server.pid"
LOG_FILE="tornado_server.log"

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

echo "Starting tornado server daemon..."
echo "Host: $HOST"
echo "Port: $PORT"
echo "Max connections: $MAX_CONNECTIONS"
echo "PID file: $PID_FILE"
echo "Log file: $LOG_FILE"

# Try different approaches for true process isolation
if command -v systemd-run >/dev/null 2>&1; then
    echo "Using systemd-run for process isolation..."
    systemd-run --user --scope --slice=user.slice \
        python3 "$SERVER_SCRIPT" \
            --host "$HOST" \
            --port "$PORT" \
            --max-connections "$MAX_CONNECTIONS" \
            > "$LOG_FILE" 2>&1 < /dev/null &
    PID=$!
    echo $PID > "$PID_FILE"
    echo "Server started with systemd-run, PID: $PID"
elif command -v at >/dev/null 2>&1; then
    echo "Using 'at' command for process scheduling..."
    # Create a temporary script for at command
    TEMP_SCRIPT="/tmp/start_server_$$"
    cat > "$TEMP_SCRIPT" << EOF
#!/bin/bash
cd "$(pwd)"
python3 "$SERVER_SCRIPT" \\
    --host "$HOST" \\
    --port "$PORT" \\
    --max-connections "$MAX_CONNECTIONS" \\
    > "$LOG_FILE" 2>&1 < /dev/null &
echo \$! > "$PID_FILE"
EOF
    chmod +x "$TEMP_SCRIPT"
    at now + 1 minute < "$TEMP_SCRIPT"
    rm "$TEMP_SCRIPT"
    
    # Wait for the job to start
    sleep 65
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        echo "Server scheduled with at, PID: $PID"
    else
        echo "Failed to start with at command"
        exit 1
    fi
else
    echo "Using advanced double-fork with new session..."
    # Create a completely detached process using double fork and new session
    (
        # First fork - detach from parent terminal
        setsid bash -c '
            # Second fork - detach from session leader
            (
                python3 "'"$SERVER_SCRIPT"'" \
                    --host "'"$HOST"'" \
                    --port "'"$PORT"'" \
                    --max-connections "'"$MAX_CONNECTIONS"'" \
                    > "'"$LOG_FILE"'" 2>&1 < /dev/null &
                echo $! > "'"$PID_FILE"'"
                echo "Double-fork server started with PID: $!"
                
                # Detach completely - ignore all signals
                trap "" HUP INT TERM
                exec > /dev/null 2>&1 < /dev/null
                
                # Wait for parent to exit
                sleep 1
            ) &
        ' &
    ) &
    
    # Wait for PID file to be created
    sleep 3
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        echo "Advanced fork server started with PID: $PID"
    fi
fi

# Wait a moment for startup
sleep 2

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "✅ Server daemon started successfully with PID: $PID"
        echo "Server should be accessible at: ws://$HOST:$PORT"
    else
        echo "❌ Server failed to start"
        if [ -f "$LOG_FILE" ]; then
            echo "--- Log output ---"
            cat "$LOG_FILE"
        fi
        exit 1
    fi
else
    echo "❌ PID file not created"
    exit 1
fi