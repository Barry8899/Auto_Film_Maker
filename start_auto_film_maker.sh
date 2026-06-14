#!/bin/bash

# Ensure we are in the correct directory
cd /home/admin/.openclaw/workspace/auto_film_maker

echo "====================================================="
echo "🎬 Starting Auto Film Maker Backend..."
echo "====================================================="

# 1. Kill existing uvicorn and tunnel processes to avoid port conflicts
echo "[1/3] Cleaning up old processes..."
pkill -f "uvicorn app:app"
pkill -f "pinggy.io"
pkill -f "ngrok"

# 2. Start FastAPI backend
echo "[2/3] Starting backend server (FastAPI)..."
source venv/bin/activate
nohup uvicorn app:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &

# Wait a moment for the server to spin up
sleep 3

# 3. Start Public Tunnel
echo "[3/3] Starting public tunnel..."
# Note: Temporarily using Pinggy until Ngrok token is provided
nohup ssh -p 443 -R0:localhost:8000 -o StrictHostKeyChecking=no a.pinggy.io > pinggy.log 2>&1 &

sleep 5
PUBLIC_URL=$(grep -o 'https://[a-zA-Z0-9.-]*\.pinggy-free\.link' pinggy.log | head -n 1)

if [ -n "$PUBLIC_URL" ]; then
    echo ""
    echo "====================================================="
    echo "🎉 Auto Film Maker is Live!"
    echo "🌐 Public Access URL: $PUBLIC_URL"
    echo "====================================================="
    echo "💡 Note: This is a temporary Pinggy link. We will upgrade to Ngrok shortly."
else
    echo "⚠️ Failed to extract public URL. Check pinggy.log for details."
fi
