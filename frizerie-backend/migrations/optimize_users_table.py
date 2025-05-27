"""
Migration to optimize the users table with indexes and constraints.
"""
from sqlalchemy import create_engine, text
from config.database import SQLALCHEMY_DATABASE_URL

def optimize_users_table():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    # List of SQL statements to execute
    statements = [
        # Add index on vip_level for faster tier-based queries
        "CREATE INDEX IF NOT EXISTS idx_users_vip_level ON users(vip_level)",
        
        # Add index on created_at for faster date-based queries
        "CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at)",
        
        # Add index on loyalty_points for faster points-based queries
        "CREATE INDEX IF NOT EXISTS idx_users_loyalty_points ON users(loyalty_points)",
        
        # Add composite index for admin queries
        "CREATE INDEX IF NOT EXISTS idx_users_admin_created ON users(is_admin, created_at)",
        
        # Add check constraint for vip_level
        """
        CREATE TABLE users_new (
            id INTEGER PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            phone_number VARCHAR(20) UNIQUE,
            vip_level VARCHAR(20) DEFAULT 'BRONZE' CHECK (vip_level IN ('BRONZE', 'SILVER', 'GOLD', 'DIAMOND')),
            loyalty_points INTEGER DEFAULT 0 CHECK (loyalty_points >= 0),
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        # Copy data to new table
        """
        INSERT INTO users_new 
        SELECT id, name, email, password_hash, phone_number, 
               vip_level, loyalty_points, is_admin, created_at, updated_at 
        FROM users
        """,
        
        # Drop old table and rename new one
        "DROP TABLE users",
        "ALTER TABLE users_new RENAME TO users",
        
        # Recreate indexes on the new table
        "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
        "CREATE INDEX IF NOT EXISTS idx_users_vip_level ON users(vip_level)",
        "CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_users_loyalty_points ON users(loyalty_points)",
        "CREATE INDEX IF NOT EXISTS idx_users_admin_created ON users(is_admin, created_at)"
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
    print("Starting users table optimization...")
    optimize_users_table()
    print("Users table optimization completed.") 