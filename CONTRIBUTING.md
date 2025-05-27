# Contributing to Frizerie

Thank you for your interest in contributing to Frizerie! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How Can I Contribute?

### Reporting Bugs

Bug reports help make Frizerie better. When you create a bug report, please include as many details as possible:

1. **Use a clear and descriptive title** for the issue
2. **Describe the exact steps to reproduce the problem**
3. **Provide specific examples** to demonstrate the steps
4. **Describe the behavior you observed** after following the steps
5. **Explain the behavior you expected to see**
6. **Include screenshots or animated GIFs** if possible
7. **Include details about your environment** (OS, browser, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

1. **Use a clear and descriptive title** for the issue
2. **Provide a detailed description of the suggested enhancement**
3. **Explain why this enhancement would be useful**
4. **Include mockups or examples** if applicable

### Pull Requests

1. **Fork the repository** and create your branch from `main`.
2. **Make your changes** in your fork.
3. **Ensure your code follows the existing style and passes linting checks.**
4. **Add tests for new or changed functionality.**
5. **Ensure all tests pass.**
6. **Submit a pull request** with a clear description of your changes.

## Development Setup

To set up the development environment, please refer to the detailed instructions in the [backend README](../frizerie-backend/README.md) and [frontend README](../frizerie-frontend/README.md).

In summary:

### Backend Setup

1. Clone the repository.
2. Navigate to the `frizerie-backend` directory.
3. Create and activate a Python virtual environment.
4. Install dependencies using `pip install -r requirements.txt`.
5. Create and configure a `.env` file.
6. Run database setup/migrations (if applicable).
7. Run the server using `uvicorn main:app --reload`.

### Frontend Setup

1. Navigate to the `frizerie-frontend` directory.
2. Install dependencies using `npm install` or `yarn install`.
3. Create and configure a `.env` file.
4. Run the development server using `npm run dev` or `yarn dev`.

For running both simultaneously, use the `start.bat` (Windows) or `start.sh` (Linux/macOS) scripts in the project root.

## Project Structure

### Backend Structure

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

### Frontend Structure

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

## Coding Guidelines

### Backend (Python)

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide.
- Use type hints when defining functions.
- Document functions and classes using docstrings.
- Keep functions small and focused on a single task.
- Write unit tests for new functionality.
- Ensure error handling is implemented using the centralized error handling module.
- Utilize the structured logging module for application logging.

### Frontend (TypeScript/React)

- Follow the [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript).
- Use functional components and hooks rather than class components.
- Use TypeScript interfaces for props and state.
- Keep components small and reusable.
- Use Tailwind CSS for styling following the project's existing patterns.
- Ensure API calls are handled through the centralized API service functions.

## Git Workflow

1. Create a new branch for each feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

2. Make your changes and commit with a descriptive message (conventional commits are preferred):
   ```bash
   git commit -m "feat: Add new feature"
   # or
   git commit -m "fix: Resolve issue #123"
   ```

3. Push your branch to GitHub:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a Pull Request from your branch to the `main` branch of the main repository.

## Testing

Tests are located in the `tests/` directory for the backend and typically in `src/` or a dedicated `__tests__` directory for the frontend (depending on framework conventions). Please refer to the respective READMEs for specific instructions.

### Backend Testing

```bash
cd frizerie-backend
pytest
```

### Frontend Testing

```bash
cd frizerie-frontend
npm test
# or yarn test
```

## Documentation

- Update documentation (READMEs, contributing guidelines, API docs) when changing functionality.
- Document all new features, components, or API endpoints.
- Keep README.md and other documentation files up to date.

## Questions?

If you have any questions, feel free to open an issue or contact the maintainers. 