# Frizerie API Backend

FastAPI backend for the Frizerie barbershop booking system. It provides a comprehensive set of endpoints for user management, booking scheduling, payments, notifications, and analytics.

## Features

- User authentication (Registration, Login, JWT)
- User profiles and loyalty system (VIP tiers, points)
- Booking management (Creation, Retrieval, Cancellation)
- Stylist availability management
- Payment processing (Stripe integration)
- Notifications system
- Centralized Error Handling
- Structured Logging
- Search and File Handling capabilities
- Analytics tracking and reporting
- RESTful API design
- Database migration support (Implied by SQLAlchemy Base)

## GDPR Compliance
- Privacy Policy available in `PRIVACY_POLICY.md`
- Export user data in Excel format via `GET /users/me/export-xlsx`
- View audit logs and third-party data processors via `GET /users/me/audit-logs` and `GET /users/me/third-party-processors`

## Project Structure

```
frizerie-backend/
├── analytics/             # Analytics tracking and reporting
│   ├── models.py
│   ├── schemas.py
│   ├── services.py
│   ├── routes.py
│   └── middleware.py
│
├── app_logging/           # Structured Logging module
│   ├── __init__.py
│   ├── config.py
│   ├── formatters.py
│   ├── handlers.py
│   └── middleware.py
│
├── auth/                    # JWT-based Authentication
│   ├── dependencies.py
│   ├── routes.py
│   └── services.py
│
├── bookings/                # Booking logic, availability, and models
│   ├── models.py
│   ├── routes.py
│   └── services.py
│
├── config/                  # Global configuration
│   ├── database.py          # SQLAlchemy session
│   ├── settings.py          # Environment variables, secrets
│   └── dependencies.py      # Reusable auth/session dependencies
│
├── errors/                # Centralized Error Handling
│   ├── __init__.py
│   ├── exceptions.py
│   ├── handlers.py
│   └── messages.py
│
├── files/                 # File handling capabilities
│   ├── routes.py
│   └── services.py
│
├── logs/                  # Directory for log files
│
├── notifications/           # Notifications system
│   ├── models.py
│   ├── routes.py
│   └── services.py
│
├── payments/              # Payment processing (Stripe)
│   ├── models.py
│   ├── schemas.py
│   ├── services.py
│   ├── routes.py
│   └── stripe_client.py
│
├── search/                # Search capabilities
│   ├── routes.py
│   └── services.py
│
├── services/              # General service management (e.g., barber services)
│   ├── models.py
│   ├── schemas.py
│   ├── routes.py
│   └── services.py
│
├── static/                # Static files (like favicon.ico)
│   └── favicon.ico
│
├── tests/                 # Application tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_bookings.py
│   ├── test_notifications.py
│   └── utils.py
│
├── users/                   # User profiles, loyalty, and models
│   ├── models.py
│   ├── routes.py
│   └── services.py
│
├── main.py                  # FastAPI app entry point, middleware, router includes
├── requirements.txt         # Project dependencies
└── .env.example             # Example environment file
```

## Setup

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd frizerie-backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `.\venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create a `.env` file in the `frizerie-backend` directory based on `.env.example` and configure your settings (e.g., Database URL, Secret Key, Stripe Keys).

6. Run database migrations (if using a database like PostgreSQL or MySQL and Alembic). *Note: This project currently uses SQLite with direct table creation.* For production, consider adding Alembic for migrations.
   ```bash
   # Example commands with Alembic (if implemented)
   # alembic revision -autogenerate -m "create initial tables"
   # alembic upgrade head
   ```

7. Run the development server:
   ```bash
   uvicorn main:app --reload
   ```

8. Access the API documentation (Swagger UI) at:
   ```
   http://localhost:8000/api/v1/docs
   ```
   Or ReDoc at:
   ```
   http://localhost:8000/api/v1/redoc
   ```

## Environment Variables

Create a `.env` file in the `frizerie-backend` directory. Copy the contents of `.env.example` and fill in the required values.

```env
# Example .env file
APP_NAME="Frizerie API"
APP_VERSION="1.0.0"
API_V1_PREFIX="/api/v1"

# Database
DATABASE_URL="sqlite:///./frizerie.db"

# Authentication
SECRET_KEY="your_super_secret_key_CHANGE_THIS"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Stripe Payments
STRIPE_SECRET_KEY="sk_test_..."
STRIPE_PUBLIC_KEY="pk_test_..."

# Logging
LOG_LEVEL="INFO"
LOG_FILE="app.log"

# Other settings...
```

## API Endpoints

The API documentation (Swagger UI/ReDoc) provides the most up-to-date list and details of all available endpoints.

- **Authentication (`/api/v1/auth`)**
  - `POST /login` - Authenticate user and return JWT tokens.
  - `POST /logout` - Invalidate refresh token.
  - `POST /refresh` - Refresh access token using a valid refresh token.

- **Users (`/api/v1/users`)**
  - `POST /` - Register a new user.
  - `GET /me` - Get information about the current authenticated user.
  - `PUT /me` - Update current user's information.
  - `GET /loyalty-status` - Get current user's loyalty status and perks.

- **Bookings (`/api/v1/bookings`)**
  - `GET /stylists` - Get a list of all stylists.
  - `GET /available-slots/{stylist_id}/{date}` - Get available booking slots for a stylist on a specific date.
  - `POST /` - Create a new booking.
  - `GET /my-bookings` - Get bookings for the current authenticated user.
  - `DELETE /{booking_id}` - Cancel a specific booking.
  - `POST /setup-test-data` - Endpoint to setup test booking data (for development/testing).

- **Notifications (`/api/v1/notifications`)**
  - `GET /me` - Get notifications for the current authenticated user.
  - `POST /` - Create and send a notification.
  - `GET /settings` - Get notification settings for the current user.
  - `PUT /settings` - Update notification settings for the current user.

- **Services (`/api/v1/services`)**
  - `POST /` - Create a new service (Admin only).
  - `GET /` - Get a list of all services.
  - `GET /{service_id}` - Get details of a specific service.
  - `PUT /{service_id}` - Update a service (Admin only).
  - `DELETE /{service_id}` - Delete a service (Admin only).

- **Payments (`/api/v1/payments`)**
  - `POST /` - Create a payment endpoint.
  - `POST /{payment_id}/process` - Process a payment for a booking.
  - `GET /{payment_id}` - Get details of a specific payment.
  - `GET /user/me` - Get payments for the current authenticated user.
  - `POST /{payment_id}/refund` - Refund a payment.
  - `POST /validate/{payment_id}` - Validate a payment endpoint.

- **Analytics (`/api/v1/analytics`)**
  - `POST /events` - Track an analytics event.
  - `GET /events` - Get analytics events (Admin only).
  - `GET /summary` - Get a summary of analytics data (Admin only).
  - `GET /revenue` - Get revenue analytics (Admin only).
  - `GET /bookings` - Get booking analytics (Admin only).
  - `GET /users` - Get user analytics (Admin only).

- **File Handling (`/api/v1/files`)**
  - Endpoints to be defined for file uploads/downloads.

- **Search (`/api/v1/search`)**
  - Endpoints to be defined for search functionality.

## Testing

Tests are located in the `tests/` directory. To run tests:

```bash
pip install -r requirements.txt
cd frizerie-backend # Make sure you are in the backend directory
pytest
```

## Contributing

Feel free to fork the repository and contribute. Please follow the existing code style and submit pull requests for any new features or bug fixes.

## License

This project is licensed under the MIT License. 