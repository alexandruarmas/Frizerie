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

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** in your fork
3. **Ensure your code follows the existing style**
4. **Add tests if applicable**
5. **Ensure all tests pass**
6. **Submit a pull request**

## Development Setup

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/frizerie.git
   cd frizerie
   ```

2. Set up Python virtual environment:
   ```bash
   cd frizerie-backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Run the backend:
   ```bash
   python main.py
   ```

### Frontend Setup

1. Install dependencies:
   ```bash
   cd frizerie-frontend
   npm install
   ```

2. Run the development server:
   ```bash
   npm run dev
   ```

## Project Structure

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

## Coding Guidelines

### Backend (Python)

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use type hints when defining functions
- Document functions and classes using docstrings
- Keep functions small and focused on a single task
- Write unit tests for new functionality

### Frontend (TypeScript/React)

- Follow the [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use functional components and hooks rather than class components
- Use TypeScript interfaces for props and state
- Keep components small and reusable
- Use Tailwind CSS for styling following the project's existing patterns

## Git Workflow

1. Create a new branch for each feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

2. Make your changes and commit with a descriptive message:
   ```bash
   git commit -m "Add feature: description of your changes"
   ```

3. Push your branch to GitHub:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a Pull Request from your branch to the main repository

## Testing

### Backend Testing

```bash
cd frizerie-backend
pytest
```

### Frontend Testing

```bash
cd frizerie-frontend
npm test
```

## Documentation

- Update documentation when changing functionality
- Document all new features, components, or API endpoints
- Keep README.md and other documentation files up to date

## Questions?

If you have any questions, feel free to open an issue or contact the maintainers. 