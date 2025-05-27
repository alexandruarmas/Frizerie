"""
Migration to optimize existing queries with better SQL and proper joins.
This includes adding query optimizations and updating the service layer functions.
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import joinedload, selectinload
from config.database import SQLALCHEMY_DATABASE_URL

def optimize_queries():
    """
    Add query optimizations by creating views and updating service layer functions.
    """
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    # List of SQL statements to create optimized views
    statements = [
        # Create a view for service statistics (used in analytics)
        """
        CREATE VIEW IF NOT EXISTS service_statistics AS
        SELECT 
            s.id,
            s.name,
            s.category_id,
            sc.name as category_name,
            COUNT(b.id) as booking_count,
            AVG(p.amount) as avg_revenue,
            SUM(p.amount) as total_revenue
        FROM services s
        LEFT JOIN bookings b ON s.id = b.service_id
        LEFT JOIN payments p ON b.id = p.booking_id AND p.status = 'completed'
        LEFT JOIN service_categories sc ON s.category_id = sc.id
        GROUP BY s.id, s.name, s.category_id, sc.name
        """,
        
        # Create a view for booking statistics (used in analytics)
        """
        CREATE VIEW IF NOT EXISTS booking_statistics AS
        SELECT 
            DATE(b.start_time) as booking_date,
            COUNT(*) as total_bookings,
            SUM(CASE WHEN b.status = 'completed' THEN 1 ELSE 0 END) as completed_bookings,
            SUM(CASE WHEN b.status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_bookings,
            AVG(p.amount) as avg_booking_value
        FROM bookings b
        LEFT JOIN payments p ON b.id = p.booking_id AND p.status = 'completed'
        GROUP BY DATE(b.start_time)
        """,
        
        # Create a view for user statistics (used in analytics)
        """
        CREATE VIEW IF NOT EXISTS user_statistics AS
        SELECT 
            u.id,
            u.name,
            u.vip_level,
            COUNT(DISTINCT b.id) as total_bookings,
            SUM(p.amount) as total_spent,
            MAX(b.created_at) as last_booking_date
        FROM users u
        LEFT JOIN bookings b ON u.id = b.user_id
        LEFT JOIN payments p ON b.id = p.booking_id AND p.status = 'completed'
        GROUP BY u.id, u.name, u.vip_level
        """,
        
        # Create a view for stylist performance (used in analytics)
        """
        CREATE VIEW IF NOT EXISTS stylist_performance AS
        SELECT 
            s.id,
            s.name,
            COUNT(DISTINCT b.id) as total_bookings,
            AVG(sr.rating) as avg_rating,
            SUM(p.amount) as total_revenue
        FROM stylists s
        LEFT JOIN bookings b ON s.id = b.stylist_id
        LEFT JOIN stylist_reviews sr ON s.id = sr.stylist_id
        LEFT JOIN payments p ON b.id = p.booking_id AND p.status = 'completed'
        GROUP BY s.id, s.name
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

    # Now let's update the service layer functions to use these optimized views
    # and add proper joins where needed.
    # We'll create a new file with the optimized service functions.
    with open("frizerie-backend/migrations/optimized_services.py", "w") as f:
        f.write("""
# Optimized service layer functions using the new views and proper joins.
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy import func, desc
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timedelta

# Example optimized get_summary (analytics) function:
def get_summary(db, time_range):
    # Use the booking_statistics view for faster aggregation
    booking_stats = db.query(func.sum(booking_statistics.total_bookings),
                            func.sum(booking_statistics.completed_bookings),
                            func.avg(booking_statistics.avg_booking_value)).\
        filter(booking_statistics.booking_date.between(time_range.start_date, time_range.end_date)).\
        first()
    
    # Use the service_statistics view for popular services
    popular_services = db.query(service_statistics).\
        order_by(desc(service_statistics.booking_count)).\
        limit(5).all()
    
    # Use the user_statistics view for user metrics
    user_metrics = db.query(func.count(user_statistics.id),
                           func.avg(user_statistics.total_spent)).\
        first()
    
    # Use the stylist_performance view for stylist metrics
    stylist_metrics = db.query(func.avg(stylist_performance.avg_rating),
                              func.sum(stylist_performance.total_revenue)).\
        first()
    
    return {
        "total_bookings": booking_stats[0] or 0,
        "completed_bookings": booking_stats[1] or 0,
        "avg_booking_value": booking_stats[2] or 0.0,
        "popular_services": [{"name": s.name, "booking_count": s.booking_count} for s in popular_services],
        "total_users": user_metrics[0] or 0,
        "avg_user_spend": user_metrics[1] or 0.0,
        "avg_stylist_rating": stylist_metrics[0] or 0.0,
        "total_revenue": stylist_metrics[1] or 0.0
    }

# Example optimized search_notifications function:
def search_notifications(db, params):
    # Use selectinload for notifications to avoid N+1 queries
    query = db.query(Notification).options(selectinload(Notification.user)).\
        filter(Notification.user_id == params.user_id)
    
    if params.type:
        query = query.filter(Notification.type == params.type)
    if params.channel:
        query = query.filter(Notification.channel == params.channel)
    if params.status:
        query = query.filter(Notification.status == params.status)
    if params.priority:
        query = query.filter(Notification.priority == params.priority)
    if params.start_date:
        query = query.filter(Notification.created_at >= params.start_date)
    if params.end_date:
        query = query.filter(Notification.created_at <= params.end_date)
    if not params.include_read:
        query = query.filter(Notification.status != NotificationStatus.READ)
    if not params.include_expired:
        query = query.filter(or_(Notification.expires_at.is_(None), Notification.expires_at > datetime.utcnow()))
    
    # Get total count (using a subquery for better performance)
    subquery = query.subquery()
    total = db.query(func.count()).select_from(subquery).scalar()
    
    # Apply pagination and ordering
    query = query.order_by(Notification.created_at.desc()).\
        offset(params.offset).\
        limit(params.limit)
    
    return query.all(), total

# Example optimized search_bookings function:
def search_bookings(db, params, skip, limit):
    # Use joinedload to avoid N+1 queries for user, stylist, and service
    query = db.query(Booking).\
        options(joinedload(Booking.user), joinedload(Booking.stylist), joinedload(Booking.service))
    
    if params.user_id:
        query = query.filter(Booking.user_id == params.user_id)
    if params.stylist_id:
        query = query.filter(Booking.stylist_id == params.stylist_id)
    if params.status:
        query = query.filter(Booking.status == params.status)
    if params.start_date:
        query = query.filter(Booking.start_time >= params.start_date)
    if params.end_date:
        query = query.filter(Booking.end_time <= params.end_date)
    
    # Get total count (using a subquery for better performance)
    subquery = query.subquery()
    total = db.query(func.count()).select_from(subquery).scalar()
    
    # Apply pagination and ordering
    query = query.order_by(Booking.start_time.desc()).\
        offset(skip).\
        limit(limit)
    
    return query.all(), total

# Example optimized search_payments function:
def search_payments(db, params, user_id):
    # Use joinedload to avoid N+1 queries for user and booking
    query = db.query(Payment).\
        options(joinedload(Payment.user), joinedload(Payment.booking))
    
    if params.user_id:
        query = query.filter(Payment.user_id == params.user_id)
    if params.status:
        query = query.filter(Payment.status == params.status)
    if params.start_date:
        query = query.filter(Payment.created_at >= params.start_date)
    if params.end_date:
        query = query.filter(Payment.created_at <= params.end_date)
    if params.min_amount:
        query = query.filter(Payment.amount >= params.min_amount)
    if params.max_amount:
        query = query.filter(Payment.amount <= params.max_amount)
    
    # Get total count (using a subquery for better performance)
    subquery = query.subquery()
    total = db.query(func.count()).select_from(subquery).scalar()
    
    # Apply pagination and ordering
    query = query.order_by(Payment.created_at.desc()).\
        offset(params.offset).\
        limit(params.limit)
    
    return query.all(), total
        """)

if __name__ == "__main__":
    print("Starting query optimizations...")
    optimize_queries()
    print("Query optimizations completed.") 