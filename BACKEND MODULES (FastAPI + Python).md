backend/
├── 1_auth/                    # JWT-based Authentication
│   ├── routes.py              # /login, /logout, /refresh
│   └── services.py
│
├── 2_users/                  # User profiles and loyalty system
│   ├── routes.py             # /me, /loyalty-status
│   ├── models.py             # User model, VIP tiers
│   └── services.py
│
├── 3_bookings/               # Booking logic & availability
│   ├── routes.py             # /bookings, /check-availability
│   ├── models.py             # Booking model, time slots
│   └── services.py
│
├── 4_notifications/          # SMS or local messaging
│   ├── routes.py             # /notifications/send
│   └── services.py
│
├── 5_config/                 # Global config
│   ├── database.py           # SQLAlchemy session
│   ├── settings.py           # Environment variables, secrets
│   └── dependencies.py       # Reusable auth/session dependencies
│
├── main.py                   # FastAPI app init, router includes
└── requirements.txt          # Dependencies
