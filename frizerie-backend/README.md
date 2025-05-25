# Frizerie API Backend

FastAPI backend for the Frizerie barbershop booking system.

## Features

- User authentication with JWT
- User profiles and loyalty system
- Booking management
- Notifications system
- RESTful API design

## Project Structure

```
frizerie-backend/
├── auth/                    # JWT-based Authentication
│   ├── routes.py            # /login, /logout, /refresh
│   └── services.py
│
├── users/                   # User profiles and loyalty system
│   ├── routes.py            # /me, /loyalty-status
│   ├── models.py            # User model, VIP tiers
│   └── services.py
│
├── bookings/                # Booking logic & availability
│   ├── routes.py            # /bookings, /check-availability
│   ├── models.py            # Booking model, time slots
│   └── services.py
│
├── notifications/           # SMS or local messaging
│   ├── routes.py            # /notifications/send
│   └── services.py
│
├── config/                  # Global config
│   ├── database.py          # SQLAlchemy session
│   ├── settings.py          # Environment variables, secrets
│   └── dependencies.py      # Reusable auth/session dependencies
│
├── main.py                  # FastAPI app init, router includes
└── requirements.txt         # Dependencies
```

## Setup

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the development server:
   ```
   uvicorn main:app --reload
   ```

5. Access the API documentation at:
   ```
   http://localhost:8000/api/v1/docs
   ```

## Environment Variables

For development, you can create a `.env` file with the following variables:

```
DATABASE_URL=sqlite:///./frizerie.db
SECRET_KEY=your_secret_key_here
DEBUG=True
```

## API Endpoints

- **Authentication**
  - POST `/api/v1/auth/login` - Login and get JWT token
  - POST `/api/v1/auth/logout` - Logout
  - POST `/api/v1/auth/refresh` - Refresh token

- **Users**
  - GET `/api/v1/users/me` - Get current user profile
  - GET `/api/v1/users/loyalty-status` - Get loyalty status and VIP perks

- **Bookings**
  - GET `/api/v1/bookings` - Get user's bookings
  - POST `/api/v1/bookings` - Create a new booking
  - POST `/api/v1/bookings/check-availability` - Check available time slots

- **Notifications**
  - POST `/api/v1/notifications/send` - Send a notification 