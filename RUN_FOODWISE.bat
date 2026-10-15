@echo off
cd /d "%~dp0"
echo Starting FoodWise Desktop App...
python --version
if errorlevel 1 (
  echo Python was not found. Install Python from https://www.python.org/downloads/
  echo Make sure "Add Python to PATH" is selected during installation.
  pause
  exit /b 1
)
python app.py
if errorlevel 1 (
  echo.
  echo FoodWise stopped because of an error shown above.
  pause
)
