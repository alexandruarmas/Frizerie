#!/bin/bash

# Start the backend
echo "Starting Frizerie Backend..."
cd frizerie-backend
python main.py &
BACKEND_PID=$!
cd ..

# Start the frontend
echo "Starting Frizerie Frontend..."
cd frizerie-frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "Frizerie Application is running!"
echo "Backend running with PID: $BACKEND_PID"
echo "Frontend running with PID: $FRONTEND_PID"
echo "Press Ctrl+C to stop both servers"

# Wait for both processes to finish
wait $BACKEND_PID $FRONTEND_PID 