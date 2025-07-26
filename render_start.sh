#!/bin/bash
# Render.com startup script

echo "===== Tea Processing AI Monitor - Render Startup ====="

# Set environment variable to indicate we're running on Render
export RENDER=true

# Test MongoDB connection
echo "Testing MongoDB connection..."
python test_mongodb_connection.py
if [ $? -ne 0 ]; then
    echo "MongoDB connection test failed, but continuing anyway with app start"
fi

# Start the application with gunicorn
echo "Starting application with Gunicorn..."
exec gunicorn app:app --timeout 120 --keep-alive 5 --workers 4 --worker-class gthread --threads 2 --log-level info --preload
