| Frontend Page    | API Endpoint (Backend)               | Method | Purpose                    |
| ---------------- | ------------------------------------ | ------ | -------------------------- |
| LoginPage        | `/auth/login`                        | POST   | Auth & get token           |
| Dashboard        | `/users/me`, `/users/loyalty-status` | GET    | Load profile & VIP data    |
| BookingCalendar  | `/bookings/check-availability`       | POST   | Check available time slots |
| BookingForm      | `/bookings`                          | POST   | Create new booking         |
| BookingList      | `/bookings`                          | GET    | Load current bookings      |
| ProfilePage      | `/users/me`                          | GET    | Show user data             |
| Notification.tsx | `/notifications/send`                | POST   | Notify stylist (optional)  |
