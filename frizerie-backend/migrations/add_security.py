"""
Migration to set up security features including rate limiting, API keys, and request tracking.
"""
from sqlalchemy import create_engine, text
from config.database import SQLALCHEMY_DATABASE_URL

def add_security():
    """
    Add tables and constraints for security features.
    """
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    # List of SQL statements to create tables and constraints
    statements = [
        # Create api_keys table for managing API access
        """
        CREATE TABLE IF NOT EXISTS api_keys (
            id VARCHAR(36) PRIMARY KEY,
            key_hash VARCHAR(255) NOT NULL UNIQUE,
            name VARCHAR(100) NOT NULL,
            user_id INTEGER NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            rate_limit INTEGER NOT NULL DEFAULT 1000,
            expires_at TIMESTAMP,
            last_used_at TIMESTAMP,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """,
        
        # Create rate_limits table for tracking request rates
        """
        CREATE TABLE IF NOT EXISTS rate_limits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key_hash VARCHAR(255) NOT NULL,
            endpoint VARCHAR(255) NOT NULL,
            request_count INTEGER NOT NULL DEFAULT 1,
            window_start TIMESTAMP NOT NULL,
            window_end TIMESTAMP NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (key_hash) REFERENCES api_keys(key_hash) ON DELETE CASCADE
        )
        """,
        
        # Create request_logs table for tracking API requests
        """
        CREATE TABLE IF NOT EXISTS request_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key_hash VARCHAR(255),
            endpoint VARCHAR(255) NOT NULL,
            method VARCHAR(10) NOT NULL,
            status_code INTEGER NOT NULL,
            ip_address VARCHAR(45),
            user_agent TEXT,
            request_data JSON,
            response_time INTEGER,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (key_hash) REFERENCES api_keys(key_hash) ON DELETE SET NULL
        )
        """,
        
        # Create security_events table for tracking security-related events
        """
        CREATE TABLE IF NOT EXISTS security_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type VARCHAR(50) NOT NULL,
            severity VARCHAR(20) NOT NULL,
            description TEXT NOT NULL,
            ip_address VARCHAR(45),
            user_id INTEGER,
            key_hash VARCHAR(255),
            metadata JSON,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
            FOREIGN KEY (key_hash) REFERENCES api_keys(key_hash) ON DELETE SET NULL
        )
        """,
        
        # Create indexes for better query performance
        """
        CREATE INDEX IF NOT EXISTS idx_api_keys_key_hash 
        ON api_keys(key_hash)
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_api_keys_user_id 
        ON api_keys(user_id)
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_rate_limits_key_endpoint 
        ON rate_limits(key_hash, endpoint, window_start)
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_request_logs_key_created 
        ON request_logs(key_hash, created_at)
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_security_events_type_created 
        ON security_events(event_type, created_at)
        """,
        
        # Add triggers for updating timestamps
        """
        CREATE TRIGGER IF NOT EXISTS trg_api_keys_update_timestamp
        AFTER UPDATE ON api_keys
        BEGIN
            UPDATE api_keys SET updated_at = CURRENT_TIMESTAMP
            WHERE id = NEW.id;
        END
        """,
        
        # Add trigger for cleaning up old rate limit records
        """
        CREATE TRIGGER IF NOT EXISTS trg_cleanup_rate_limits
        AFTER INSERT ON rate_limits
        BEGIN
            DELETE FROM rate_limits 
            WHERE window_end < datetime('now', '-1 day');
        END
        """,
        
        # Add trigger for cleaning up old request logs
        """
        CREATE TRIGGER IF NOT EXISTS trg_cleanup_request_logs
        AFTER INSERT ON request_logs
        BEGIN
            DELETE FROM request_logs 
            WHERE created_at < datetime('now', '-30 days');
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
    print("Starting security migration...")
    add_security()
    print("Security migration completed.") 