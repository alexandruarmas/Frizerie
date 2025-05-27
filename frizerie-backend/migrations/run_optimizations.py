"""
Main script to run all database optimizations in the correct order.
The order is important because of foreign key dependencies.
"""
import sys
import os
from pathlib import Path

# Add the parent directory to sys.path to allow imports
sys.path.append(str(Path(__file__).parent.parent))

from optimize_users_table import optimize_users_table
from optimize_bookings_table import optimize_bookings_table
from optimize_payments_table import optimize_payments_table

def run_all_optimizations():
    print("Starting database optimizations...")
    
    # 1. Optimize users table first (as it's referenced by others)
    print("\n=== Optimizing Users Table ===")
    optimize_users_table()
    
    # 2. Optimize bookings table (depends on users)
    print("\n=== Optimizing Bookings Table ===")
    optimize_bookings_table()
    
    # 3. Optimize payments table (depends on users and bookings)
    print("\n=== Optimizing Payments Table ===")
    optimize_payments_table()
    
    print("\nAll database optimizations completed successfully!")

if __name__ == "__main__":
    try:
        run_all_optimizations()
    except Exception as e:
        print(f"\nError during optimization: {str(e)}")
        sys.exit(1) 