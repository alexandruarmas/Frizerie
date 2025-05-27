"""
Migration to set up the waitlist system with proper tables and constraints.
This includes creating tables for waitlist entries and their status tracking.
"""
from sqlalchemy import create_engine, text
from config.database import SQLALCHEMY_DATABASE_URL

def add_waitlist():
    """
    Add tables and constraints for waitlist management.
    """
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    # List of SQL statements to create tables and constraints
    statements = [
        # Create waitlist_entries table if it doesn't exist
        """
        CREATE TABLE IF NOT EXISTS waitlist_entries (
            id VARCHAR(36) PRIMARY KEY,
            user_id INTEGER NOT NULL,
            service_id INTEGER NOT NULL,
            stylist_id INTEGER,
            preferred_date_start TIMESTAMP NOT NULL,
            preferred_date_end TIMESTAMP NOT NULL,
            preferred_time_start VARCHAR(5) CHECK (preferred_time_start REGEXP '^([0-1][0-9]|2[0-3]):[0-5][0-9]$'),
            preferred_time_end VARCHAR(5) CHECK (preferred_time_end REGEXP '^([0-1][0-9]|2[0-3]):[0-5][0-9]$'),
            status VARCHAR(20) NOT NULL CHECK (status IN ('PENDING', 'NOTIFIED', 'BOOKED', 'EXPIRED', 'CANCELLED')),
            notes TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            notified_at TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE,
            FOREIGN KEY (stylist_id) REFERENCES stylists(id) ON DELETE SET NULL,
            CHECK (preferred_date_start < preferred_date_end),
            CHECK (preferred_time_start < preferred_time_end),
            CHECK (expires_at > created_at)
        )
        """,
        
        # Create waitlist_notifications table if it doesn't exist
        """
        CREATE TABLE IF NOT EXISTS waitlist_notifications (
            id VARCHAR(36) PRIMARY KEY,
            waitlist_entry_id VARCHAR(36) NOT NULL,
            notification_type VARCHAR(20) NOT NULL CHECK (notification_type IN ('SLOT_AVAILABLE', 'EXPIRING_SOON', 'EXPIRED')),
            sent_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) NOT NULL CHECK (status IN ('SENT', 'READ', 'FAILED')),
            FOREIGN KEY (waitlist_entry_id) REFERENCES waitlist_entries(id) ON DELETE CASCADE
        )
        """,
        
        # Create indexes for better query performance
        """
        CREATE INDEX IF NOT EXISTS idx_waitlist_entries_user 
        ON waitlist_entries(user_id, status)
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_waitlist_entries_service 
        ON waitlist_entries(service_id, status)
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_waitlist_entries_stylist 
        ON waitlist_entries(stylist_id, status)
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_waitlist_entries_dates 
        ON waitlist_entries(preferred_date_start, preferred_date_end, status)
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_waitlist_notifications_entry 
        ON waitlist_notifications(waitlist_entry_id, sent_at)
        """,
        
        # Add trigger to update updated_at timestamp
        """
        CREATE TRIGGER IF NOT EXISTS update_waitlist_entries_timestamp 
        AFTER UPDATE ON waitlist_entries
        BEGIN
            UPDATE waitlist_entries SET updated_at = CURRENT_TIMESTAMP 
            WHERE id = NEW.id;
        END
        """
    ]
    
    with engine.connect() as conn:
        for statement in statements:
            try:
                conn.execute(text(statement))
                conn.commit()
                print(f"Successfully executed: {statement[:100]}...")
            except Exception as e:
                print(f"Error executing statement: {statement[:100]}...")
                print(f"Error: {str(e)}")
                conn.rollback()
                raise

if __name__ == "__main__":
    print("Starting waitlist migration...")
    add_waitlist()
    print("Waitlist migration completed.") 