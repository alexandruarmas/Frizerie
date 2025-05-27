import sqlite3

def check_table():
    # Connect to the database
    conn = sqlite3.connect('sql_app.db')
    cursor = conn.cursor()
    
    try:
        # Get table info
        cursor.execute("PRAGMA table_info(analytics_events);")
        columns = cursor.fetchall()
        
        print("\nCurrent analytics_events table structure:")
        print("----------------------------------------")
        for col in columns:
            print(f"Column: {col[1]}, Type: {col[2]}, NotNull: {col[3]}, Default: {col[4]}")
            
    except sqlite3.OperationalError as e:
        print(f"Error: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_table() 