# Frizerie - Barbershop Appointment System

This is a modern, full-stack appointment booking system for barbershops and hair salons. It features user authentication, booking management with real-time availability, a VIP loyalty system, notifications, payment processing, and analytics.

It is composed of two main parts:

- **Backend**: A FastAPI application providing the API (see [frizerie-backend/README.md](../frizerie-backend/README.md))
- **Frontend**: A React application built with Vite, TypeScript, and Tailwind CSS

## Frontend Features

- User Authentication (Login, Registration)
- User Profile and Loyalty Status Viewing
- Browse Stylists and Services
- Real-time Appointment Booking Interface
- View and Manage User Bookings
- Payment Integration for Bookings
- Notification Settings Management
- Responsive UI with Tailwind CSS
- Progressive Web App (PWA) readiness

For a detailed list of backend features, please refer to the [backend README](../frizerie-backend/README.md).

## Project Structure

```
frizerie-frontend/
├── public/       # Static assets (like index.html, icons, manifest.json)
│   └── ...
├── src/
│   ├── api/          # Centralized API service functions (using Axios or Fetch)
│   ├── assets/       # Static assets used in components (images, svgs)
│   ├── components/   # Reusable UI components
│   ├── context/      # React Context for global state (e.g., AuthContext)
│   ├── hooks/        # Custom React hooks
│   ├── pages/        # Top-level components for different routes
│   ├── types/        # TypeScript type definitions
│   ├── utils/        # Utility functions
│   ├── App.tsx       # Main application component and routing setup
│   └── main.tsx      # Application entry point (ReactDOM rendering)
├── .env.example  # Example environment variables for frontend
├── index.html    # Main HTML file
├── package.json  # npm dependencies and scripts
├── postcss.config.js # PostCSS configuration (for Tailwind)
├── tailwind.config.js # Tailwind CSS configuration
├── tsconfig.json # TypeScript configuration
└── vite.config.ts # Vite build configuration
```

## Getting Started

### Prerequisites

- Node.js (LTS version recommended)
- npm or yarn

### Installation

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd frizerie-frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   # or yarn install
   ```

3. Create a `.env` file in the `frizerie-frontend` directory based on `.env.example` and configure necessary environment variables (e.g., the backend API URL).

### Running the Application

It is recommended to use the provided start scripts in the project root directory (`start.bat` for Windows, `start.sh` for Linux/macOS) which will start both the backend and frontend servers simultaneously.

Alternatively, you can start the frontend manually:

```bash
cd frizerie-frontend
npm run dev
# or yarn dev
```

The frontend development server will typically be available at `http://localhost:5173`. The console output will show the exact URL.

Ensure the backend server is also running for the application to function correctly.

## API Documentation

The backend API documentation (Swagger UI/ReDoc) can be accessed when the backend server is running:

- Swagger UI: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`

## Building for Production

To build the frontend for production:

```bash
cd frizerie-frontend
npm run build
# or yarn build
```

The production-ready files will be generated in the `dist/` directory.

To preview the production build:

```bash
cd frizerie-frontend
npm run preview
# or yarn preview
```

## Contributing

We welcome contributions! Please see the [CONTRIBUTING.md](../CONTRIBUTING.md) file for details on how to contribute.

## License

This project is licensed under the MIT License. 