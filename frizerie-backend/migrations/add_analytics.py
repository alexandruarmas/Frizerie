"""
Migration to set up the analytics and reporting system with proper tables and views.
This includes creating tables for storing analytics data and views for common reports.
"""
from sqlalchemy import create_engine, text
from config.database import SQLALCHEMY_DATABASE_URL

def add_analytics():
    """
    Add tables, views, and triggers for analytics and reporting.
    """
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    # List of SQL statements to create tables and views
    statements = [
        # Create analytics_events table for tracking various events
        """
        CREATE TABLE IF NOT EXISTS analytics_events (
            id VARCHAR(36) PRIMARY KEY,
            event_type VARCHAR(50) NOT NULL,
            event_data JSON NOT NULL,
            user_id INTEGER,
            stylist_id INTEGER,
            service_id INTEGER,
            booking_id VARCHAR(36),
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
            FOREIGN KEY (stylist_id) REFERENCES stylists(id) ON DELETE SET NULL,
            FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE SET NULL,
            FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE SET NULL
        )
        """,
        
        # Create daily_analytics table for storing aggregated daily metrics
        """
        CREATE TABLE IF NOT EXISTS daily_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL UNIQUE,
            total_bookings INTEGER NOT NULL DEFAULT 0,
            completed_bookings INTEGER NOT NULL DEFAULT 0,
            cancelled_bookings INTEGER NOT NULL DEFAULT 0,
            total_revenue DECIMAL(10,2) NOT NULL DEFAULT 0,
            total_waitlist_entries INTEGER NOT NULL DEFAULT 0,
            total_recurring_bookings INTEGER NOT NULL DEFAULT 0,
            average_booking_duration INTEGER NOT NULL DEFAULT 0,
            peak_hours JSON,
            stylist_performance JSON,
            service_popularity JSON,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        # Create monthly_analytics table for storing aggregated monthly metrics
        """
        CREATE TABLE IF NOT EXISTS monthly_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            total_bookings INTEGER NOT NULL DEFAULT 0,
            completed_bookings INTEGER NOT NULL DEFAULT 0,
            cancelled_bookings INTEGER NOT NULL DEFAULT 0,
            total_revenue DECIMAL(10,2) NOT NULL DEFAULT 0,
            total_waitlist_entries INTEGER NOT NULL DEFAULT 0,
            total_recurring_bookings INTEGER NOT NULL DEFAULT 0,
            average_booking_duration INTEGER NOT NULL DEFAULT 0,
            peak_days JSON,
            stylist_performance JSON,
            service_popularity JSON,
            customer_retention_rate DECIMAL(5,2),
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(year, month)
        )
        """,
        
        # Create view for booking statistics
        """
        CREATE VIEW IF NOT EXISTS vw_booking_statistics AS
        SELECT 
            DATE(b.start_time) as booking_date,
            COUNT(*) as total_bookings,
            SUM(CASE WHEN b.status = 'COMPLETED' THEN 1 ELSE 0 END) as completed_bookings,
            SUM(CASE WHEN b.status = 'CANCELLED' THEN 1 ELSE 0 END) as cancelled_bookings,
            SUM(s.price) as total_revenue,
            AVG(s.duration_minutes) as average_duration,
            COUNT(DISTINCT b.user_id) as unique_customers,
            COUNT(DISTINCT b.stylist_id) as active_stylists
        FROM bookings b
        JOIN services s ON b.service_id = s.id
        GROUP BY DATE(b.start_time)
        """,
        
        # Create view for stylist performance
        """
        CREATE VIEW IF NOT EXISTS vw_stylist_performance AS
        SELECT 
            u.id as stylist_id,
            u.first_name || ' ' || u.last_name as stylist_name,
            COUNT(b.id) as total_bookings,
            SUM(CASE WHEN b.status = 'COMPLETED' THEN 1 ELSE 0 END) as completed_bookings,
            SUM(CASE WHEN b.status = 'CANCELLED' THEN 1 ELSE 0 END) as cancelled_bookings,
            SUM(s.price) as total_revenue,
            AVG(s.duration_minutes) as average_duration,
            COUNT(DISTINCT b.user_id) as unique_customers
        FROM users u
        LEFT JOIN bookings b ON u.id = b.stylist_id
        LEFT JOIN services s ON b.service_id = s.id
        WHERE u.is_stylist = 1
        GROUP BY u.id, u.first_name, u.last_name
        """,
        
        # Create view for service popularity
        """
        CREATE VIEW IF NOT EXISTS vw_service_popularity AS
        SELECT 
            s.id as service_id,
            s.name as service_name,
            COUNT(b.id) as total_bookings,
            SUM(CASE WHEN b.status = 'COMPLETED' THEN 1 ELSE 0 END) as completed_bookings,
            SUM(s.price) as total_revenue,
            AVG(s.duration_minutes) as average_duration,
            COUNT(DISTINCT b.user_id) as unique_customers
        FROM services s
        LEFT JOIN bookings b ON s.id = b.service_id
        GROUP BY s.id, s.name
        """,
        
        # Create view for customer analytics
        """
        CREATE VIEW IF NOT EXISTS vw_customer_analytics AS
        SELECT 
            u.id as user_id,
            u.first_name || ' ' || u.last_name as customer_name,
            COUNT(b.id) as total_bookings,
            SUM(CASE WHEN b.status = 'COMPLETED' THEN 1 ELSE 0 END) as completed_bookings,
            SUM(CASE WHEN b.status = 'CANCELLED' THEN 1 ELSE 0 END) as cancelled_bookings,
            SUM(s.price) as total_spent,
            AVG(s.duration_minutes) as average_booking_duration,
            COUNT(DISTINCT b.stylist_id) as stylists_visited,
            COUNT(DISTINCT b.service_id) as services_used,
            MAX(b.start_time) as last_booking_date,
            MIN(b.start_time) as first_booking_date
        FROM users u
        LEFT JOIN bookings b ON u.id = b.user_id
        LEFT JOIN services s ON b.service_id = s.id
        GROUP BY u.id, u.first_name, u.last_name
        """,
        
        # Create indexes for better query performance
        """
        CREATE INDEX IF NOT EXISTS idx_analytics_events_type 
        ON analytics_events(event_type, created_at)
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_analytics_events_user 
        ON analytics_events(user_id, created_at)
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_analytics_events_stylist 
        ON analytics_events(stylist_id, created_at)
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_daily_analytics_date 
        ON daily_analytics(date)
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_monthly_analytics_year_month 
        ON monthly_analytics(year, month)
        """,
        
        # Add triggers to update analytics
        """
        CREATE TRIGGER IF NOT EXISTS trg_update_daily_analytics
        AFTER INSERT ON bookings
        BEGIN
            INSERT OR REPLACE INTO daily_analytics (
                date,
                total_bookings,
                completed_bookings,
                cancelled_bookings,
                total_revenue,
                updated_at
            )
            SELECT 
                DATE(NEW.start_time),
                COUNT(*),
                SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END),
                SUM(CASE WHEN status = 'CANCELLED' THEN 1 ELSE 0 END),
                SUM(s.price),
                CURRENT_TIMESTAMP
            FROM bookings b
            JOIN services s ON b.service_id = s.id
            WHERE DATE(b.start_time) = DATE(NEW.start_time)
            GROUP BY DATE(b.start_time);
        END
        """,
        
        """
        CREATE TRIGGER IF NOT EXISTS trg_update_monthly_analytics
        AFTER INSERT ON bookings
        BEGIN
            INSERT OR REPLACE INTO monthly_analytics (
                year,
                month,
                total_bookings,
                completed_bookings,
                cancelled_bookings,
                total_revenue,
                updated_at
            )
            SELECT 
                strftime('%Y', NEW.start_time),
                strftime('%m', NEW.start_time),
                COUNT(*),
                SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END),
                SUM(CASE WHEN status = 'CANCELLED' THEN 1 ELSE 0 END),
                SUM(s.price),
                CURRENT_TIMESTAMP
            FROM bookings b
            JOIN services s ON b.service_id = s.id
            WHERE strftime('%Y', b.start_time) = strftime('%Y', NEW.start_time)
            AND strftime('%m', b.start_time) = strftime('%m', NEW.start_time)
            GROUP BY strftime('%Y', b.start_time), strftime('%m', b.start_time);
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
    print("Starting analytics migration...")
    add_analytics()
    print("Analytics migration completed.") 