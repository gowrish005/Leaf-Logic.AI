#!/bin/bash

echo "Tea Processing AI Monitor - Startup Script"
echo "========================================"

echo "Checking local MongoDB availability..."
python3 local_db_setup.py
if [ $? -ne 0 ]; then
    echo
    echo "WARNING: Local MongoDB setup failed. The application will try to use the primary"
    echo "MongoDB only. If that fails, certain features may not work correctly."
    echo
    read -p "Do you want to continue anyway? (y/n): " confirm
    if [[ $confirm != [yY] ]]; then
        echo "Exiting application startup."
        exit 1
    fi
fi

echo "Starting Tea Processing AI Monitor application..."
python3 app.py
