"""
Migration to optimize the payments table with indexes and constraints.
"""
from sqlalchemy import create_engine, text
from config.database import SQLALCHEMY_DATABASE_URL

def optimize_payments_table():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    # List of SQL statements to execute
    statements = [
        # Add indexes for frequently queried fields
        "CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status)",
        "CREATE INDEX IF NOT EXISTS idx_payments_created_at ON payments(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_payments_booking_id ON payments(booking_id)",
        
        # Add composite indexes for common query patterns
        "CREATE INDEX IF NOT EXISTS idx_payments_user_status ON payments(user_id, status)",
        "CREATE INDEX IF NOT EXISTS idx_payments_date_status ON payments(created_at, status)",
        "CREATE INDEX IF NOT EXISTS idx_payments_amount_status ON payments(amount, status)",
        
        # Create new table with constraints
        """
        CREATE TABLE payments_new (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            booking_id INTEGER NOT NULL,
            amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
            currency VARCHAR(3) NOT NULL DEFAULT 'RON',
            status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'completed', 'failed', 'refunded', 'cancelled', 'partially_refunded', 'disputed', 'dispute_resolved')),
            payment_method VARCHAR(50) NOT NULL,
            transaction_id VARCHAR(100) UNIQUE,
            payment_details JSON,
            refund_amount DECIMAL(10,2) CHECK (refund_amount >= 0),
            refund_reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
            CHECK (refund_amount <= amount)
        )
        """,
        
        # Copy data to new table
        """
        INSERT INTO payments_new 
        SELECT id, user_id, booking_id, amount, currency, status,
               payment_method, transaction_id, payment_details, refund_amount,
               refund_reason, created_at, updated_at 
        FROM payments
        """,
        
        # Drop old table and rename new one
        "DROP TABLE payments",
        "ALTER TABLE payments_new RENAME TO payments",
        
        # Recreate indexes on the new table
        "CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status)",
        "CREATE INDEX IF NOT EXISTS idx_payments_created_at ON payments(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_payments_booking_id ON payments(booking_id)",
        "CREATE INDEX IF NOT EXISTS idx_payments_user_status ON payments(user_id, status)",
        "CREATE INDEX IF NOT EXISTS idx_payments_date_status ON payments(created_at, status)",
        "CREATE INDEX IF NOT EXISTS idx_payments_amount_status ON payments(amount, status)"
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
    print("Starting payments table optimization...")
    optimize_payments_table()
    print("Payments table optimization completed.") 