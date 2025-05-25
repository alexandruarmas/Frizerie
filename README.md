# Frizerie - Barbershop Appointment System

A modern barbershop booking application with React frontend and FastAPI backend.

## Features

- User authentication with JWT
- Appointment booking system
- Stylist management
- VIP loyalty program
- Real-time notifications
- Responsive UI with Tailwind CSS

## Project Structure

### Frontend (React, TypeScript, Vite, Tailwind CSS)
- Authentication
- Dashboard with loyalty status
- Booking calendar and management
- User profile management
- Responsive design

### Backend (FastAPI, SQLAlchemy, PostgreSQL)
- JWT authentication
- User management
- Booking system
- Notification service
- VIP loyalty tier system

## Deployment

### Frontend Deployment (Vercel)
This project is configured for one-click deployment to Vercel:

1. Connect your GitHub repository to Vercel
2. Set the root directory to `frizerie-frontend`
3. Add environment variable `VITE_API_URL` with your backend URL

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/alexandruarmas/Frizerie)

### Backend Deployment
The backend can be deployed to platforms like Render, Railway, or Heroku.

## Local Development

### Frontend
```bash
cd frizerie-frontend
npm install
npm run dev
```

### Backend
```bash
cd frizerie-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Documentation

- [API Documentation](./API-DOCUMENTATION.md)
- [Database Schema](./DATABASE-SCHEMA.md)
- [Deployment Guide](./DEPLOYMENT-GUIDE.md)
- [VIP Loyalty System](./VIP%20LOGIC%20MODULE.md)

## License

MIT 