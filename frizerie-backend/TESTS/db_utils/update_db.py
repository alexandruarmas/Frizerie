from sqlalchemy import create_engine, inspect
from config.database import Base, engine
from analytics.models import AnalyticsEvent
from users.models import User
from services.models import Service

def update_database():
    # Get the inspector
    inspector = inspect(engine)
    
    # Check if the table exists
    if 'analytics_events' not in inspector.get_table_names():
        print("Creating analytics_events table...")
        Base.metadata.create_all(bind=engine)
        return
    
    # Get existing columns
    columns = [col['name'] for col in inspector.get_columns('analytics_events')]
    
    # Check for missing columns
    missing_columns = []
    for column in ['stylist_id', 'service_id', 'booking_id']:
        if column not in columns:
            missing_columns.append(column)
    
    if missing_columns:
        print(f"Missing columns: {missing_columns}")
        print("Please run the following SQL commands to add the missing columns:")
        for column in missing_columns:
            if column == 'stylist_id':
                print("ALTER TABLE analytics_events ADD COLUMN stylist_id INTEGER REFERENCES users(id);")
            elif column == 'service_id':
                print("ALTER TABLE analytics_events ADD COLUMN service_id INTEGER REFERENCES services(id);")
            elif column == 'booking_id':
                print("ALTER TABLE analytics_events ADD COLUMN booking_id VARCHAR;")
    else:
        print("All required columns exist in the analytics_events table.")

if __name__ == "__main__":
    update_database() 