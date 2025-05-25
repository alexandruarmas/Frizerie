| # | Table           | Fields                                                       |
| - | --------------- | ------------------------------------------------------------ |
| 1 | `users`         | id, name, email, password\_hash, vip\_level, loyalty\_points |
| 2 | `bookings`      | id, user\_id, stylist\_id, service, date, time, status       |
| 3 | `stylists`      | id, name, available\_hours (JSON or related table)           |
| 4 | `notifications` | id, user\_id, message, sent\_at, method (sms/local)          |
| 5 | `vip_tiers`     | id, name, min\_points, perks (description string or JSON)    |
