"""Add necessary database constraints for data integrity."""

from sqlalchemy import create_engine, text
from config.database import SQLALCHEMY_DATABASE_URL
from config.settings import get_settings

settings = get_settings()

def add_constraints():
    """Add necessary database constraints for data integrity."""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    # List of constraint statements
    constraint_statements = [
        # User constraints
        """ALTER TABLE users
           ADD CONSTRAINT chk_users_vip_level 
           CHECK (vip_level IN ('BRONZE', 'SILVER', 'GOLD', 'DIAMOND'))""",
        
        """ALTER TABLE users
           ADD CONSTRAINT chk_users_loyalty_points 
           CHECK (loyalty_points >= 0)""",
        
        # Booking constraints
        """ALTER TABLE bookings
           ADD CONSTRAINT chk_bookings_dates 
           CHECK (start_time < end_time)""",
        
        """ALTER TABLE bookings
           ADD CONSTRAINT chk_bookings_status 
           CHECK (status IN ('pending', 'confirmed', 'cancelled', 'completed', 'no_show', 'waitlisted'))""",
        
        # Payment constraints
        """ALTER TABLE payments
           ADD CONSTRAINT chk_payments_amount 
           CHECK (amount > 0)""",
        
        """ALTER TABLE payments
           ADD CONSTRAINT chk_payments_status 
           CHECK (status IN ('pending', 'completed', 'failed', 'refunded', 'cancelled'))""",
        
        # Stylist review constraints
        """ALTER TABLE stylist_reviews
           ADD CONSTRAINT chk_stylist_reviews_rating 
           CHECK (rating >= 1.0 AND rating <= 5.0)""",
        
        # Notification constraints
        """ALTER TABLE notifications
           ADD CONSTRAINT chk_notifications_priority 
           CHECK (priority IN ('low', 'medium', 'high', 'urgent'))""",
        
        """ALTER TABLE notifications
           ADD CONSTRAINT chk_notifications_status 
           CHECK (status IN ('pending', 'sent', 'delivered', 'read', 'failed', 'cancelled'))""",
        
        # Notification preferences constraints
        """ALTER TABLE notification_preferences
           ADD CONSTRAINT chk_notification_prefs_quiet_hours 
           CHECK (
               (quiet_hours_start IS NULL AND quiet_hours_end IS NULL) OR
               (quiet_hours_start IS NOT NULL AND quiet_hours_end IS NOT NULL)
           )""",
        
        # Loyalty points history constraints
        """ALTER TABLE loyalty_points_history
           ADD CONSTRAINT chk_loyalty_points_reason 
           CHECK (reason IN ('BOOKING', 'REDEMPTION', 'REFERRAL', 'ADMIN_ADJUSTMENT', 'EXPIRATION'))""",
        
        # Service constraints
        """ALTER TABLE services
           ADD CONSTRAINT chk_services_duration 
           CHECK (duration > 0)""",
        
        """ALTER TABLE services
           ADD CONSTRAINT chk_services_price 
           CHECK (price >= 0)""",
        
        # Stylist availability constraints
        """ALTER TABLE stylist_availability
           ADD CONSTRAINT chk_stylist_availability_times 
           CHECK (start_time < end_time)""",
        
        # Unique constraints
        """ALTER TABLE users
           ADD CONSTRAINT uq_users_email UNIQUE (email)""",
        
        """ALTER TABLE users
           ADD CONSTRAINT uq_users_phone UNIQUE (phone_number)""",
        
        """ALTER TABLE service_categories
           ADD CONSTRAINT uq_service_categories_name UNIQUE (name)""",
        
        """ALTER TABLE notification_templates
           ADD CONSTRAINT uq_notification_templates_type_channel_lang 
           UNIQUE (type, channel, language)""",
        
        # Foreign key constraints with proper ON DELETE actions
        """ALTER TABLE bookings
           DROP CONSTRAINT IF EXISTS fk_bookings_user_id""",
        
        """ALTER TABLE bookings
           ADD CONSTRAINT fk_bookings_user_id 
           FOREIGN KEY (user_id) 
           REFERENCES users(id) 
           ON DELETE CASCADE""",
        
        """ALTER TABLE payments
           DROP CONSTRAINT IF EXISTS fk_payments_booking_id""",
        
        """ALTER TABLE payments
           ADD CONSTRAINT fk_payments_booking_id 
           FOREIGN KEY (booking_id) 
           REFERENCES bookings(id) 
           ON DELETE CASCADE""",
        
        """ALTER TABLE notifications
           DROP CONSTRAINT IF EXISTS fk_notifications_user_id""",
        
        """ALTER TABLE notifications
           ADD CONSTRAINT fk_notifications_user_id 
           FOREIGN KEY (user_id) 
           REFERENCES users(id) 
           ON DELETE CASCADE""",
        
        """ALTER TABLE stylist_reviews
           DROP CONSTRAINT IF EXISTS fk_stylist_reviews_user_id""",
        
        """ALTER TABLE stylist_reviews
           ADD CONSTRAINT fk_stylist_reviews_user_id 
           FOREIGN KEY (user_id) 
           REFERENCES users(id) 
           ON DELETE CASCADE""",
        
        """ALTER TABLE user_settings
           DROP CONSTRAINT IF EXISTS fk_user_settings_user_id""",
        
        """ALTER TABLE user_settings
           ADD CONSTRAINT fk_user_settings_user_id 
           FOREIGN KEY (user_id) 
           REFERENCES users(id) 
           ON DELETE CASCADE""",
        
        """ALTER TABLE notification_preferences
           DROP CONSTRAINT IF EXISTS fk_notification_preferences_user_id""",
        
        """ALTER TABLE notification_preferences
           ADD CONSTRAINT fk_notification_preferences_user_id 
           FOREIGN KEY (user_id) 
           REFERENCES users(id) 
           ON DELETE CASCADE"""
    ]
    
    with engine.connect() as connection:
        for statement in constraint_statements:
            try:
                connection.execute(text(statement))
                connection.commit()
            except Exception as e:
                print(f"Error executing statement: {statement}")
                print(f"Error: {str(e)}")
                raise

if __name__ == "__main__":
    add_constraints()
    print("Constraints added successfully!") 