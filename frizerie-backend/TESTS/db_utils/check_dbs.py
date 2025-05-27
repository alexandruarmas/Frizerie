import sqlite3

def check_database(db_path):
    print(f"\nChecking database: {db_path}")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables found: {tables}")
        
        # Check analytics_events table if it exists
        if 'analytics_events' in tables:
            cursor.execute("PRAGMA table_info(analytics_events)")
            columns = cursor.fetchall()
            print("\nanalytics_events table structure:")
            for col in columns:
                print(f"Column: {col[1]}, Type: {col[2]}, NotNull: {col[3]}, Default: {col[4]}")
        
        conn.close()
    except Exception as e:
        print(f"Error checking {db_path}: {str(e)}")

# Check both databases
check_database('frizerie.db')
check_database('sql_app.db') 