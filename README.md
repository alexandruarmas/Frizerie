# Frizerie - Barbershop Appointment System

Frizerie is a modern appointment booking system for barbershops and hair salons, featuring VIP loyalty tiers, real-time booking, and SMS notifications.

## Features

- **User Authentication**: Secure login and registration with JWT tokens
- **Appointment Booking**: Real-time availability checking and booking
- **VIP Loyalty System**: Tiered loyalty program with exclusive perks
- **Notifications**: SMS and in-app notifications for appointments
- **Responsive UI**: Works on desktop and mobile devices

## Project Structure

The project consists of two main parts:

- **Frontend**: React application with Vite, Tailwind CSS, and React Router
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

- Node.js (v16+)
- Python (v3.9+)
- npm or yarn

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/frizerie.git
   cd frizerie
   ```

2. Install backend dependencies:
   ```
   cd frizerie-backend
   pip install -r requirements.txt
   cd ..
   ```

3. Install frontend dependencies:
   ```
   cd frizerie-frontend
   npm install
   cd ..
   ```

### Running the Application

#### Windows:
Simply run the `start.bat` file by double-clicking it or running it from the command line:
```
start.bat
```

#### Manual Start:
1. Start the backend:
   ```
   cd frizerie-backend
   python main.py
   ```

2. In a new terminal, start the frontend:
   ```
   cd frizerie-frontend
   npm run dev
   ```

3. Access the application at `http://localhost:5173` (or the port shown in the terminal)

## Using the Application

1. **Register a new account** - Create a new user account to access the system
2. **Book an appointment** - Browse available stylists and time slots
3. **Check your VIP status** - View your loyalty points and current tier
4. **Manage bookings** - View, cancel, or reschedule your appointments
5. **View notifications** - See your booking confirmations and reminders

## VIP Loyalty System

The application features a tiered loyalty system:

- **Bronze**: Default tier (0-99 points)
- **Silver**: 100-199 points, priority booking
- **Gold**: 200-299 points, priority booking + 10% discount
- **Diamond**: 300+ points, priority booking + 10% discount + free styling products

You earn loyalty points for each booking, and certain time slots are reserved for VIP members.

## Development

### Backend API Documentation

When the backend is running, you can access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Environment Variables

Create a `.env` file in both the frontend and backend directories to configure the application:

#### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

#### Backend (.env)
```
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

## License

MIT License 