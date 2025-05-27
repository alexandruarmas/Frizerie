"""
Run all database migrations in the correct order.
"""
import sys
import os

# Add the parent directory to sys.path to ensure imports work correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from migrations.add_users import add_users
from migrations.add_services import add_services
from migrations.add_stylists import add_stylists
from migrations.add_bookings import add_bookings
from migrations.add_waitlist import add_waitlist
from migrations.add_analytics import add_analytics
from migrations.add_security import add_security
from migrations.add_error_logging import add_error_logging

def run_migrations():
    """
    Run all migrations in the correct order.
    """
    print("Starting database migrations...")
    
    # Run migrations in order
    print("\n1. Setting up users...")
    add_users()
    
    print("\n2. Setting up services...")
    add_services()
    
    print("\n3. Setting up stylists...")
    add_stylists()
    
    print("\n4. Setting up bookings...")
    add_bookings()
    
    print("\n5. Setting up waitlist system...")
    add_waitlist()
    
    print("\n6. Setting up analytics system...")
    add_analytics()
    
    print("\n7. Setting up security features...")
    add_security()
    
    print("\n8. Setting up error logging and monitoring...")
    add_error_logging()
    
    print("\nAll migrations completed successfully!")

if __name__ == "__main__":
    run_migrations() 