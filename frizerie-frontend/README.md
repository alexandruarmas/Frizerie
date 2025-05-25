# Frizerie - Barbershop Appointment System

This is a modern appointment booking system for barbershops and hair salons, featuring VIP loyalty tiers, real-time booking, and notification system.

## Features

- **User Authentication**: Secure login/register with JWT tokens
- **Appointment Booking**: View and book appointments with real-time availability
- **VIP Loyalty System**: Tiered membership with exclusive perks and time slots
- **Notifications**: Booking confirmations and appointment reminders
- **Profile Management**: Update personal information and view loyalty status
- **Progressive Web App (PWA)**: Support for mobile and offline usage

## Project Structure

The project consists of two main parts:

- **Frontend**: React application with Vite, TypeScript, and Tailwind CSS
- **Backend**: FastAPI application with SQLAlchemy ORM and SQLite database

### Frontend Structure
```
frizerie-frontend/
├── src/
│   ├── auth/         - Authentication context and hooks
│   ├── components/   - UI components
│   ├── pages/        - Page components
│   ├── services/     - API service functions
│   ├── App.tsx       - Main application component
│   └── main.tsx      - Application entry point
└── ...
```

### Backend Structure
```
frizerie-backend/
├── auth/             - Authentication logic and routes
├── bookings/         - Booking management logic and routes
├── config/           - Application configuration
├── notifications/    - Notification system
├── users/            - User management and VIP loyalty
└── main.py           - Application entry point
```

## Getting Started

### Prerequisites

- Node.js 14.18+ or 16+
- Python 3.9+
- npm or yarn

### Installation

1. Clone the repository
2. Install backend dependencies:
   ```bash
   cd frizerie-backend
   pip install fastapi uvicorn sqlalchemy pydantic[email] python-jose[cryptography] passlib[bcrypt] python-multipart
   cd ..
   ```
3. Install frontend dependencies:
   ```bash
   cd frizerie-frontend
   npm install
   cd ..
   ```

### Running the Application

#### Using the start script:
Simply run the `start.bat` file in the root directory, which will start both the backend and frontend servers.

#### Manual startup:
1. Start the backend:
   ```bash
   cd frizerie-backend
   python main.py
   ```
2. Start the frontend:
   ```bash
   cd frizerie-frontend
   npm run dev
   ```

The frontend will be available at `http://localhost:5173` (or the port shown in the console) and the backend API at `http://localhost:8000`.

## VIP Loyalty System

The application features a tiered loyalty system:

- **Bronze**: Default tier (0-99 points)
- **Silver**: 100-199 points, priority booking
- **Gold**: 200-299 points, priority booking + 10% discount
- **Diamond**: 300+ points, priority booking + 10% discount + free products

Users earn loyalty points for each booking, and certain time slots are reserved for VIP members.

## API Documentation

When the backend is running, you can access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Building for Production

To build the frontend for production:

```bash
cd frizerie-frontend
npm run build
```

To preview the production build:

```bash
cd frizerie-frontend
npm run preview
``` 