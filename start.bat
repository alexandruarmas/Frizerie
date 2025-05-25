@echo off
echo Starting Frizerie Application...

:: Start backend in a new window
echo Starting Backend...
start "Frizerie Backend" cmd /k "cd frizerie-backend && python main.py"

:: Start frontend in a new window
echo Starting Frontend...
start "Frizerie Frontend" cmd /k "cd frizerie-frontend && npm run dev"

echo Frizerie Application is running!
echo Backend and Frontend are running in separate windows.
echo Close the windows to stop the servers. 