import sqlite3

def add_columns():
    # Connect to the database
    conn = sqlite3.connect('sql_app.db')
    cursor = conn.cursor()
    
    try:
        # Add stylist_id column
        cursor.execute("ALTER TABLE analytics_events ADD COLUMN stylist_id INTEGER REFERENCES users(id);")
        
        # Add service_id column
        cursor.execute("ALTER TABLE analytics_events ADD COLUMN service_id INTEGER REFERENCES services(id);")
        
        # Add booking_id column
        cursor.execute("ALTER TABLE analytics_events ADD COLUMN booking_id VARCHAR;")
        
        # Commit the changes
        conn.commit()
        print("Successfully added new columns to analytics_events table")
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Some columns already exist, skipping...")
        else:
            print(f"Error: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_columns() 