"""
Migration to set up error logging and monitoring system.
"""
from sqlalchemy import text
from database import engine

def add_error_logging():
    """Add error logging and monitoring tables."""
    with engine.connect() as conn:
        # Create error_logs table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS error_logs (
                id SERIAL PRIMARY KEY,
                error_type VARCHAR(50) NOT NULL,
                error_code VARCHAR(50),
                message TEXT NOT NULL,
                stack_trace TEXT,
                severity VARCHAR(20) NOT NULL CHECK (severity IN ('info', 'warning', 'error', 'critical')),
                source VARCHAR(255) NOT NULL,
                user_id INTEGER REFERENCES users(id),
                request_id VARCHAR(50),
                endpoint VARCHAR(255),
                method VARCHAR(10),
                status_code INTEGER,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP WITH TIME ZONE,
                resolution_notes TEXT
            );
        """))
        
        # Create system_logs table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS system_logs (
                id SERIAL PRIMARY KEY,
                log_level VARCHAR(20) NOT NULL CHECK (log_level IN ('debug', 'info', 'warning', 'error', 'critical')),
                message TEXT NOT NULL,
                source VARCHAR(255) NOT NULL,
                context JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create monitoring_metrics table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS monitoring_metrics (
                id SERIAL PRIMARY KEY,
                metric_name VARCHAR(100) NOT NULL,
                metric_value FLOAT NOT NULL,
                metric_type VARCHAR(50) NOT NULL,
                labels JSONB,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create alert_rules table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS alert_rules (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                metric_name VARCHAR(100) NOT NULL,
                condition VARCHAR(50) NOT NULL,
                threshold FLOAT NOT NULL,
                severity VARCHAR(20) NOT NULL CHECK (severity IN ('info', 'warning', 'error', 'critical')),
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create alerts table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS alerts (
                id SERIAL PRIMARY KEY,
                rule_id INTEGER REFERENCES alert_rules(id),
                metric_name VARCHAR(100) NOT NULL,
                metric_value FLOAT NOT NULL,
                threshold FLOAT NOT NULL,
                severity VARCHAR(20) NOT NULL,
                message TEXT NOT NULL,
                status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'acknowledged', 'resolved')),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP WITH TIME ZONE,
                resolved_by INTEGER REFERENCES users(id),
                resolution_notes TEXT
            );
        """))
        
        # Create indexes
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_error_logs_created_at ON error_logs(created_at);
            CREATE INDEX IF NOT EXISTS idx_error_logs_severity ON error_logs(severity);
            CREATE INDEX IF NOT EXISTS idx_error_logs_error_type ON error_logs(error_type);
            CREATE INDEX IF NOT EXISTS idx_error_logs_user_id ON error_logs(user_id);
            
            CREATE INDEX IF NOT EXISTS idx_system_logs_created_at ON system_logs(created_at);
            CREATE INDEX IF NOT EXISTS idx_system_logs_log_level ON system_logs(log_level);
            CREATE INDEX IF NOT EXISTS idx_system_logs_source ON system_logs(source);
            
            CREATE INDEX IF NOT EXISTS idx_monitoring_metrics_timestamp ON monitoring_metrics(timestamp);
            CREATE INDEX IF NOT EXISTS idx_monitoring_metrics_name ON monitoring_metrics(metric_name);
            
            CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at);
            CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
            CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
        """))
        
        # Create cleanup functions
        conn.execute(text("""
            CREATE OR REPLACE FUNCTION cleanup_old_logs()
            RETURNS void AS $$
            BEGIN
                -- Delete error logs older than 30 days
                DELETE FROM error_logs 
                WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '30 days';
                
                -- Delete system logs older than 30 days
                DELETE FROM system_logs 
                WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '30 days';
                
                -- Delete monitoring metrics older than 7 days
                DELETE FROM monitoring_metrics 
                WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '7 days';
                
                -- Delete resolved alerts older than 90 days
                DELETE FROM alerts 
                WHERE status = 'resolved' 
                AND created_at < CURRENT_TIMESTAMP - INTERVAL '90 days';
            END;
            $$ LANGUAGE plpgsql;
        """))
        
        # Create cleanup trigger
        conn.execute(text("""
            CREATE OR REPLACE FUNCTION trigger_cleanup_old_logs()
            RETURNS trigger AS $$
            BEGIN
                PERFORM cleanup_old_logs();
                RETURN NULL;
            END;
            $$ LANGUAGE plpgsql;
            
            DROP TRIGGER IF EXISTS cleanup_logs_trigger ON error_logs;
            CREATE TRIGGER cleanup_logs_trigger
            AFTER INSERT ON error_logs
            FOR EACH STATEMENT
            EXECUTE FUNCTION trigger_cleanup_old_logs();
        """))
        
        print("Error logging and monitoring tables created successfully!") 