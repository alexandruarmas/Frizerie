frontend/
├── 1_auth/                   # Login/logout views and logic
│   ├── LoginPage.tsx
│   └── useAuth.ts            # Hook for auth + token
│
├── 2_dashboard/              # VIP dashboard (points, welcome)
│   ├── Dashboard.tsx
│   └── LoyaltyCard.tsx
│
├── 3_bookings/               # Booking interface
│   ├── BookingCalendar.tsx   # UI for available slots
│   ├── BookingForm.tsx       # Submit/edit form
│   └── BookingList.tsx       # List upcoming bookings
│
├── 4_profile/                # Account info & edit
│   ├── ProfilePage.tsx
│   └── EditProfile.tsx
│
├── 5_services/               # API services
│   ├── api.ts                # Axios instance with base URL
│   ├── bookings.ts           # /bookings API calls
│   ├── users.ts              # /users API calls
│   └── auth.ts               # /auth API calls
│
├── 6_shared/                 # Reusable components
│   ├── Button.tsx
│   ├── Modal.tsx
│   └── Notification.tsx
│
├── App.tsx                   # Router and main layout
└── main.tsx                  # React entry point
