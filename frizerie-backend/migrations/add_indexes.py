"""Add necessary indexes to improve query performance."""

from sqlalchemy import create_engine, Index, text
from config.database import SQLALCHEMY_DATABASE_URL
from config.settings import get_settings

settings = get_settings()

def add_indexes():
    """Add necessary indexes to improve query performance."""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    # List of index creation statements
    index_statements = [
        # Users table indexes
        "CREATE INDEX IF NOT EXISTS idx_users_phone_number ON users(phone_number)",
        "CREATE INDEX IF NOT EXISTS idx_users_vip_level ON users(vip_level)",
        "CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at)",
        
        # Bookings table indexes
        "CREATE INDEX IF NOT EXISTS idx_bookings_user_id ON bookings(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_bookings_stylist_id ON bookings(stylist_id)",
        "CREATE INDEX IF NOT EXISTS idx_bookings_service_id ON bookings(service_id)",
        "CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status)",
        "CREATE INDEX IF NOT EXISTS idx_bookings_start_time ON bookings(start_time)",
        "CREATE INDEX IF NOT EXISTS idx_bookings_end_time ON bookings(end_time)",
        "CREATE INDEX IF NOT EXISTS idx_bookings_created_at ON bookings(created_at)",
        
        # Composite index for booking queries
        "CREATE INDEX IF NOT EXISTS idx_bookings_stylist_date ON bookings(stylist_id, start_time)",
        "CREATE INDEX IF NOT EXISTS idx_bookings_user_date ON bookings(user_id, start_time)",
        
        # Payments table indexes
        "CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_payments_booking_id ON payments(booking_id)",
        "CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status)",
        "CREATE INDEX IF NOT EXISTS idx_payments_created_at ON payments(created_at)",
        
        # Notifications table indexes
        "CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type)",
        "CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications(status)",
        "CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at)",
        
        # Stylist reviews indexes
        "CREATE INDEX IF NOT EXISTS idx_stylist_reviews_stylist_id ON stylist_reviews(stylist_id)",
        "CREATE INDEX IF NOT EXISTS idx_stylist_reviews_rating ON stylist_reviews(rating)",
        "CREATE INDEX IF NOT EXISTS idx_stylist_reviews_created_at ON stylist_reviews(created_at)",
        
        # Analytics events indexes
        "CREATE INDEX IF NOT EXISTS idx_analytics_events_user_id ON analytics_events(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_analytics_events_event_type ON analytics_events(event_type)",
        "CREATE INDEX IF NOT EXISTS idx_analytics_events_created_at ON analytics_events(created_at)",
        
        # Loyalty points history indexes
        "CREATE INDEX IF NOT EXISTS idx_loyalty_points_user_id ON loyalty_points_history(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_loyalty_points_created_at ON loyalty_points_history(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_loyalty_points_reason ON loyalty_points_history(reason)",
        
        # User settings indexes
        """CREATE INDEX IF NOT EXISTS idx_user_settings_notification_prefs 
           ON user_settings(enable_notifications, enable_email_notifications, 
           enable_sms_notifications, enable_booking_reminders)""",
        
        # Notification preferences indexes
        """CREATE INDEX IF NOT EXISTS idx_notification_prefs_channels 
           ON notification_preferences(email_enabled, sms_enabled, 
           push_enabled, in_app_enabled)""",
        
        # Service categories indexes
        "CREATE INDEX IF NOT EXISTS idx_service_categories_name ON service_categories(name)",
        
        # Audit logs indexes
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action)",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at)"
    ]
    
    with engine.connect() as connection:
        for statement in index_statements:
            try:
                connection.execute(text(statement))
                connection.commit()
            except Exception as e:
                print(f"Error executing statement: {statement}")
                print(f"Error: {str(e)}")
                raise

if __name__ == "__main__":
    add_indexes()
    print("Indexes added successfully!") 