#!/bin/bash

echo "Stopping Solmakase services..."

# FastAPI 서버 중지
if [ -f /tmp/fastapi.pid ]; then
    PID=$(cat /tmp/fastapi.pid)
    if ps -p $PID > /dev/null; then
        kill $PID
        echo "FastAPI server stopped (PID: $PID)"
    fi
    rm /tmp/fastapi.pid
fi

# Vite 서버 중지
if [ -f /tmp/vite.pid ]; then
    PID=$(cat /tmp/vite.pid)
    if ps -p $PID > /dev/null; then
        kill $PID
        echo "Vite dev server stopped (PID: $PID)"
    fi
    rm /tmp/vite.pid
fi

echo "Services stopped!"

