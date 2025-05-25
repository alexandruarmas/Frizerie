# VIP Loyalty System Module

This document describes the implementation of the VIP loyalty system in the Frizerie application.

## Overview

The VIP loyalty system rewards users for their bookings with loyalty points, which determine their VIP tier. Higher tiers provide access to exclusive benefits and premium booking slots.

## Tier Structure

| Tier    | Points Required | Benefits                                           |
|---------|----------------|-----------------------------------------------------|
| BRONZE  | 0-99           | Basic booking access                                |
| SILVER  | 100-199        | Priority booking for normal slots                   |
| GOLD    | 200-299        | Priority booking + 10% discount on services         |
| DIAMOND | 300+           | Priority booking + 10% discount + free products     |

## Backend Implementation

### Database Models

- **User Model**: Contains `vip_level` (0-3) and `loyalty_points` fields
- **VIPTier Model**: Defines tier thresholds, names, and associated perks
- **StylistAvailability Model**: Includes `vip_restricted` flag for premium slots

### API Endpoints

#### Get User Loyalty Status

```
GET /users/loyalty-status
```

Returns the user's current tier, points, next tier, and available perks:

```json
{
  "tier": "SILVER",
  "points": 150,
  "next_tier": "GOLD",
  "points_to_next_tier": 50,
  "perks": ["Priority booking"]
}
```

### Service Layer

The core VIP logic is implemented in `users/services.py`:

```python
def calculate_vip_tier(points):
    """Calculate VIP tier based on loyalty points."""
    if points >= 300:
        return 3  # DIAMOND
    elif points >= 200:
        return 2  # GOLD
    elif points >= 100:
        return 1  # SILVER
    else:
        return 0  # BRONZE

def update_user_loyalty(db, user_id, points_to_add):
    """Update a user's loyalty points and recalculate their VIP tier."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.loyalty_points += points_to_add
    user.vip_level = calculate_vip_tier(user.loyalty_points)
    
    db.commit()
    db.refresh(user)
    
    # Send notification if tier changed
    if calculate_vip_tier(user.loyalty_points - points_to_add) != user.vip_level:
        tier_names = ["BRONZE", "SILVER", "GOLD", "DIAMOND"]
        create_vip_notification(db, user.id, tier_names[user.vip_level])
    
    return user
```

### Points Accumulation

Users earn loyalty points in the following ways:
- 10 points for each completed booking
- Additional points for specific services or promotions

When a booking is created, points are automatically added to the user's account:

```python
# In bookings/services.py
def create_booking(db, user_id, stylist_id, service_type, start_time):
    # Create booking...
    
    # Add loyalty points
    user.loyalty_points += 10  # Add 10 points per booking
    db.commit()
```

### VIP-Restricted Time Slots

Certain time slots are restricted to VIP members only (Silver and above):
- Weekend morning slots
- Prime-time slots (3-5 PM)

When checking available slots, the user's VIP level is considered:

```python
# In bookings/services.py
def get_available_slots(db, stylist_id, date, user_vip_level=0):
    # ...
    
    for avail in availability:
        # ...
        
        # Check VIP restrictions
        is_vip_restricted = avail.vip_restricted
        is_vip_accessible = not is_vip_restricted or (is_vip_restricted and user_vip_level >= 1)
        
        if not is_booked and is_vip_accessible:
            available_slots.append({
                "start_time": current_time.isoformat(),
                "end_time": slot_end_time.isoformat(),
                "is_vip_only": is_vip_restricted
            })
```

## Frontend Implementation

### Displaying Loyalty Status

The loyalty status is displayed in the user dashboard using the `LoyaltyCard` component:

```tsx
// src/components/LoyaltyCard.tsx
export default function LoyaltyCard({ loyaltyStatus }) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h2 className="text-xl font-bold">{loyaltyStatus.tier} Member</h2>
      <div className="mt-2">
        <div className="w-full bg-gray-200 rounded-full h-2.5">
          <div 
            className="bg-primary h-2.5 rounded-full" 
            style={{ width: `${(loyaltyStatus.points / (loyaltyStatus.next_tier_points || 300)) * 100}%` }}
          ></div>
        </div>
        <p className="text-sm mt-1">
          {loyaltyStatus.points} / {loyaltyStatus.next_tier_points || 'MAX'} points
        </p>
      </div>
      <div className="mt-4">
        <h3 className="font-medium">Your Perks:</h3>
        <ul className="list-disc list-inside text-sm">
          {loyaltyStatus.perks.map((perk, i) => (
            <li key={i}>{perk}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
```

### Handling VIP-Only Slots in the Booking Calendar

The booking calendar displays VIP-only slots with special styling and restricts access based on the user's VIP level:

```tsx
// src/components/BookingCalendar.tsx
function TimeSlot({ slot, onSelect, userVipLevel }) {
  const isVipOnly = slot.is_vip_only;
  const canBook = !isVipOnly || (isVipOnly && userVipLevel >= 1);
  
  return (
    <button
      className={`p-2 rounded ${
        isVipOnly 
          ? 'bg-gold-100 border border-gold-300' 
          : 'bg-gray-100 border border-gray-300'
      } ${canBook ? 'hover:bg-primary hover:text-white' : 'opacity-50 cursor-not-allowed'}`}
      onClick={() => canBook && onSelect(slot)}
      disabled={!canBook}
    >
      {format(parseISO(slot.start_time), 'h:mm a')}
      {isVipOnly && <span className="ml-2 text-xs bg-gold-500 text-white px-1 rounded">VIP</span>}
    </button>
  );
}
```

### Displaying VIP Benefits

The app displays VIP benefits in various locations:
- In the user profile
- During the booking process
- In promotional notifications

## Testing

To verify the VIP logic is working correctly, run these tests:

```bash
# Backend tests
cd frizerie-backend
python -m pytest tests/test_vip_logic.py

# Frontend tests
cd frizerie-frontend
npm test -- --testPathPattern=src/components/LoyaltyCard.test.tsx
```

## Future Enhancements

Planned improvements to the VIP system:
- Seasonal promotions with bonus points
- Referral bonuses for bringing new customers
- Birthday rewards with double points
- Tiered discounts on products based on VIP level