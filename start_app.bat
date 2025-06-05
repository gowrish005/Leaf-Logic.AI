@echo off
echo Tea Processing AI Monitor - Startup Script
echo ========================================

echo Checking local MongoDB availability...
python local_db_setup.py
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Local MongoDB setup failed. The application will try to use the primary
    echo MongoDB only. If that fails, certain features may not work correctly.
    echo.
    choice /C YN /M "Do you want to continue anyway?"
    if %errorlevel% neq 1 (
        echo Exiting application startup.
        exit /b 1
    )
)

echo Starting Tea Processing AI Monitor application...
python app.py
