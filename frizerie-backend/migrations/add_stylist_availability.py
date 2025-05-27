"""
Migration to set up the stylist availability system with proper tables and constraints.
This includes creating tables for stylist availability, time off, and breaks.
"""
from sqlalchemy import create_engine, text
from config.database import SQLALCHEMY_DATABASE_URL

def add_stylist_availability():
    """
    Add tables and constraints for stylist availability management.
    """
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    # List of SQL statements to create tables and constraints
    statements = [
        # Create stylist_availability table if it doesn't exist
        """
        CREATE TABLE IF NOT EXISTS stylist_availability (
            id VARCHAR(36) PRIMARY KEY,
            stylist_id INTEGER NOT NULL,
            day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),
            start_time VARCHAR(5) NOT NULL CHECK (start_time REGEXP '^([0-1][0-9]|2[0-3]):[0-5][0-9]$'),
            end_time VARCHAR(5) NOT NULL CHECK (end_time REGEXP '^([0-1][0-9]|2[0-3]):[0-5][0-9]$'),
            is_available BOOLEAN NOT NULL DEFAULT TRUE,
            break_start VARCHAR(5) CHECK (break_start REGEXP '^([0-1][0-9]|2[0-3]):[0-5][0-9]$'),
            break_end VARCHAR(5) CHECK (break_end REGEXP '^([0-1][0-9]|2[0-3]):[0-5][0-9]$'),
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (stylist_id) REFERENCES stylists(id) ON DELETE CASCADE,
            UNIQUE (stylist_id, day_of_week),
            CHECK (start_time < end_time),
            CHECK (break_start IS NULL OR break_end IS NULL OR break_start < break_end),
            CHECK (break_start IS NULL OR (break_start >= start_time AND break_start <= end_time)),
            CHECK (break_end IS NULL OR (break_end >= start_time AND break_end <= end_time))
        )
        """,
        
        # Create stylist_time_off table if it doesn't exist
        """
        CREATE TABLE IF NOT EXISTS stylist_time_off (
            id VARCHAR(36) PRIMARY KEY,
            stylist_id INTEGER NOT NULL,
            start_date TIMESTAMP NOT NULL,
            end_date TIMESTAMP NOT NULL,
            reason TEXT,
            is_approved BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (stylist_id) REFERENCES stylists(id) ON DELETE CASCADE,
            CHECK (start_date < end_date),
            CHECK (start_date >= CURRENT_TIMESTAMP)
        )
        """,
        
        # Create indexes for better query performance
        """
        CREATE INDEX IF NOT EXISTS idx_stylist_availability_stylist_day 
        ON stylist_availability(stylist_id, day_of_week)
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_stylist_time_off_stylist_dates 
        ON stylist_time_off(stylist_id, start_date, end_date)
        """,
        
        # Add trigger to update updated_at timestamp
        """
        CREATE TRIGGER IF NOT EXISTS update_stylist_availability_timestamp 
        AFTER UPDATE ON stylist_availability
        BEGIN
            UPDATE stylist_availability SET updated_at = CURRENT_TIMESTAMP 
            WHERE id = NEW.id;
        END
        """,
        
        """
        CREATE TRIGGER IF NOT EXISTS update_stylist_time_off_timestamp 
        AFTER UPDATE ON stylist_time_off
        BEGIN
            UPDATE stylist_time_off SET updated_at = CURRENT_TIMESTAMP 
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
    print("Starting stylist availability migration...")
    add_stylist_availability()
    print("Stylist availability migration completed.") 