# Frizerie API Documentation

This document provides detailed information about the Frizerie API endpoints.

## Base URL

```
http://localhost:8000
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication.

### Login

```
POST /auth/login
```

**Request Body:**
```json
{
  "username": "email@example.com",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Refresh Token

```
POST /auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Users

### Register User

```
POST /users/register
```

**Request Body:**
```json
{
  "email": "email@example.com",
  "password": "your_password",
  "name": "Your Name"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Your Name",
  "email": "email@example.com",
  "vip_level": 0,
  "loyalty_points": 0
}
```

### Get Current User

```
GET /users/me
```

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```json
{
  "id": 1,
  "name": "Your Name",
  "email": "email@example.com",
  "vip_level": 0,
  "loyalty_points": 0
}
```

### Update User Profile

```
PUT /users/me
```

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Request Body:**
```json
{
  "name": "Updated Name",
  "email": "updated@example.com"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Updated Name",
  "email": "updated@example.com",
  "vip_level": 0,
  "loyalty_points": 0
}
```

### Get User Loyalty Status

```
GET /users/loyalty-status
```

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```json
{
  "tier": "BRONZE",
  "points": 50,
  "next_tier": "SILVER",
  "points_to_next_tier": 50,
  "perks": ["Access to regular slots"]
}
```

## Bookings

### Get Stylists

```
GET /bookings/stylists
```

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Ana Maria",
    "specialization": "Color Specialist"
  },
  {
    "id": 2,
    "name": "Ion",
    "specialization": "Haircuts"
  }
]
```

### Get Available Slots

```
GET /bookings/available-slots/{stylist_id}/{date}
```

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Path Parameters:**
- `stylist_id`: ID of the stylist
- `date`: Date in ISO format (YYYY-MM-DDTHH:MM:SS)

**Response:**
```json
[
  {
    "start_time": "2023-10-20T09:00:00",
    "end_time": "2023-10-20T09:30:00",
    "is_vip_only": false
  },
  {
    "start_time": "2023-10-20T10:00:00",
    "end_time": "2023-10-20T10:30:00",
    "is_vip_only": true
  }
]
```

### Create Booking

```
POST /bookings/
```

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Request Body:**
```json
{
  "stylist_id": 1,
  "service_type": "Haircut",
  "start_time": "2023-10-20T09:00:00"
}
```

**Response:**
```json
{
  "id": 1,
  "stylist": {
    "id": 1,
    "name": "Ana Maria"
  },
  "service_type": "Haircut",
  "start_time": "2023-10-20T09:00:00",
  "end_time": "2023-10-20T09:30:00",
  "status": "SCHEDULED"
}
```

### Get User Bookings

```
GET /bookings/my-bookings
```

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```json
[
  {
    "id": 1,
    "stylist": {
      "id": 1,
      "name": "Ana Maria"
    },
    "service_type": "Haircut",
    "start_time": "2023-10-20T09:00:00",
    "end_time": "2023-10-20T09:30:00",
    "status": "SCHEDULED"
  }
]
```

### Cancel Booking

```
DELETE /bookings/{booking_id}
```

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Path Parameters:**
- `booking_id`: ID of the booking to cancel

**Response:**
```json
{
  "id": 1,
  "stylist": {
    "id": 1,
    "name": "Ana Maria"
  },
  "service_type": "Haircut",
  "start_time": "2023-10-20T09:00:00",
  "end_time": "2023-10-20T09:30:00",
  "status": "CANCELLED"
}
```

## Notifications

### Get User Notifications

```
GET /notifications/
```

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```json
[
  {
    "id": 1,
    "message": "Booking confirmed with Ana Maria for a Haircut on Friday, October 20, 2023 at 09:00 AM.",
    "method": "SMS",
    "sent_at": "2023-10-15T14:30:00",
    "status": "SENT"
  }
]
```

### Create Notification

```
POST /notifications/
```

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Request Body:**
```json
{
  "message": "Custom notification message",
  "method": "SMS"
}
```

**Response:**
```json
{
  "id": 2,
  "message": "Custom notification message",
  "method": "SMS",
  "sent_at": "2023-10-15T15:45:00",
  "status": "SENT"
}
```

### Get Notification Settings

```
GET /notifications/settings
```

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```json
{
  "sms_enabled": true,
  "email_enabled": true,
  "booking_reminders": true,
  "promotional_messages": false,
  "vip_updates": true
}
```

### Update Notification Settings

```
PUT /notifications/settings
```

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Request Body:**
```json
{
  "sms_enabled": true,
  "email_enabled": true,
  "booking_reminders": false,
  "promotional_messages": true,
  "vip_updates": true
}
```

**Response:**
```json
{
  "sms_enabled": true,
  "email_enabled": true,
  "booking_reminders": false,
  "promotional_messages": true,
  "vip_updates": true
}
``` 