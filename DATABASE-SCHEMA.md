# Frizerie Database Schema

This document describes the database schema for the Frizerie application.

## Entity Relationship Diagram

```
┌────────────┐       ┌────────────┐       ┌────────────────────┐
│   User     │       │   Booking  │       │ StylistAvailability│
├────────────┤       ├────────────┤       ├────────────────────┤
│ id         │       │ id         │       │ id                 │
│ name       │       │ user_id    │◄──────┤ stylist_id         │
│ email      │       │ stylist_id │       │ start_time         │
│ password   │       │ service_type│       │ end_time           │
│ vip_level  │       │ start_time │       │ vip_restricted     │
│ loyalty_pts│       │ end_time   │       └────────────────────┘
└────────────┘       │ status     │                 ▲
      ▲ ▲            │ created_at │                 │
      │ │            │ updated_at │                 │
      │ │            └────────────┘                 │
      │ │                   ▲                       │
      │ │                   │                       │
      │ │                   │                       │
      │ │            ┌────────────┐                 │
      │ └────────────┤  Stylist   ├─────────────────┘
      │              ├────────────┤
      │              │ id         │
      │              │ name       │
      │              │ special... │
      │              │ bio        │
      │              │ avatar_url │
      │              │ is_active  │
      │              └────────────┘
      │
      │
┌─────┴──────┐
│Notification│
├────────────┤
│ id         │
│ user_id    │
│ message    │
│ method     │
│ sent_at    │
│ status     │
└────────────┘
```

## Models

### User

Represents a user of the application.

| Column         | Type      | Description                       |
|----------------|-----------|-----------------------------------|
| id             | Integer   | Primary key                       |
| name           | String    | User's full name                  |
| email          | String    | User's email address (unique)     |
| password       | String    | Hashed password                   |
| vip_level      | Integer   | VIP tier level (0-3)              |
| loyalty_points | Integer   | Earned loyalty points             |
| created_at     | DateTime  | Account creation timestamp        |
| updated_at     | DateTime  | Last update timestamp             |

Relationships:
- One-to-many with Booking
- One-to-many with Notification

### VIPTier

Represents the different VIP tiers available.

| Column      | Type      | Description                 |
|-------------|-----------|-----------------------------|
| id          | Integer   | Primary key                 |
| name        | String    | Tier name (BRONZE, SILVER..)|
| min_points  | Integer   | Minimum points required     |
| description | String    | Tier description            |
| perks       | String    | JSON list of perks          |

### Stylist

Represents a barber or hairdresser.

| Column         | Type      | Description                       |
|----------------|-----------|-----------------------------------|
| id             | Integer   | Primary key                       |
| name           | String    | Stylist's name                    |
| specialization | String    | Area of expertise                 |
| bio            | Text      | Stylist biography                 |
| avatar_url     | String    | Profile image URL                 |
| is_active      | Boolean   | Whether stylist is active         |
| created_at     | DateTime  | Account creation timestamp        |
| updated_at     | DateTime  | Last update timestamp             |

Relationships:
- One-to-many with Booking
- One-to-many with StylistAvailability

### StylistAvailability

Represents a stylist's available time slots.

| Column         | Type      | Description                       |
|----------------|-----------|-----------------------------------|
| id             | Integer   | Primary key                       |
| stylist_id     | Integer   | Foreign key to Stylist            |
| start_time     | DateTime  | Start of availability period      |
| end_time       | DateTime  | End of availability period        |
| vip_restricted | Boolean   | Whether slot is VIP-only          |

Relationships:
- Many-to-one with Stylist

### Booking

Represents an appointment booking.

| Column         | Type      | Description                       |
|----------------|-----------|-----------------------------------|
| id             | Integer   | Primary key                       |
| user_id        | Integer   | Foreign key to User               |
| stylist_id     | Integer   | Foreign key to Stylist            |
| service_type   | String    | Type of service booked            |
| start_time     | DateTime  | Start time of appointment         |
| end_time       | DateTime  | End time of appointment           |
| status         | String    | SCHEDULED, COMPLETED, CANCELLED   |
| created_at     | DateTime  | Booking creation timestamp        |
| updated_at     | DateTime  | Last update timestamp             |

Relationships:
- Many-to-one with User
- Many-to-one with Stylist

### Notification

Represents a notification sent to a user.

| Column         | Type      | Description                       |
|----------------|-----------|-----------------------------------|
| id             | Integer   | Primary key                       |
| user_id        | Integer   | Foreign key to User               |
| message        | String    | Notification message              |
| method         | String    | SMS, EMAIL, etc.                  |
| sent_at        | DateTime  | When notification was sent        |
| status         | String    | PENDING, SENT, FAILED             |

Relationships:
- Many-to-one with User

## Indexes

- User.email: Unique index for fast user lookup
- Booking.user_id: Index for fetching user bookings
- Booking.stylist_id: Index for fetching stylist bookings
- Booking.start_time: Index for date-based queries
- StylistAvailability.stylist_id: Index for fetching stylist availability
- Notification.user_id: Index for fetching user notifications 