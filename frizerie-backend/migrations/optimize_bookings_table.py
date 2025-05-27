"""
Migration to optimize the bookings table with indexes and constraints.
"""
from sqlalchemy import create_engine, text
from config.database import SQLALCHEMY_DATABASE_URL

def optimize_bookings_table():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    # List of SQL statements to execute
    statements = [
        # Add indexes for frequently queried fields
        "CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status)",
        "CREATE INDEX IF NOT EXISTS idx_bookings_start_time ON bookings(start_time)",
        "CREATE INDEX IF NOT EXISTS idx_bookings_user_id ON bookings(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_bookings_stylist_id ON bookings(stylist_id)",
        
        # Add composite indexes for common query patterns
        "CREATE INDEX IF NOT EXISTS idx_bookings_user_status ON bookings(user_id, status)",
        "CREATE INDEX IF NOT EXISTS idx_bookings_stylist_status ON bookings(stylist_id, status)",
        "CREATE INDEX IF NOT EXISTS idx_bookings_date_status ON bookings(start_time, status)",
        
        # Create new table with constraints
        """
        CREATE TABLE bookings_new (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            stylist_id INTEGER NOT NULL,
            service_id INTEGER NOT NULL,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP NOT NULL,
            status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'confirmed', 'cancelled', 'completed', 'no_show', 'waitlisted')),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (stylist_id) REFERENCES stylists(id) ON DELETE CASCADE,
            FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE,
            CHECK (end_time > start_time)
        )
        """,
        
        # Copy data to new table
        """
        INSERT INTO bookings_new 
        SELECT id, user_id, stylist_id, service_id, start_time, 
               end_time, status, notes, created_at, updated_at 
        FROM bookings
        """,
        
        # Drop old table and rename new one
        "DROP TABLE bookings",
        "ALTER TABLE bookings_new RENAME TO bookings",
        
        # Recreate indexes on the new table
        "CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status)",
        "CREATE INDEX IF NOT EXISTS idx_bookings_start_time ON bookings(start_time)",
        "CREATE INDEX IF NOT EXISTS idx_bookings_user_id ON bookings(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_bookings_stylist_id ON bookings(stylist_id)",
        "CREATE INDEX IF NOT EXISTS idx_bookings_user_status ON bookings(user_id, status)",
        "CREATE INDEX IF NOT EXISTS idx_bookings_stylist_status ON bookings(stylist_id, status)",
        "CREATE INDEX IF NOT EXISTS idx_bookings_date_status ON bookings(start_time, status)"
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
    print("Starting bookings table optimization...")
    optimize_bookings_table()
    print("Bookings table optimization completed.") 