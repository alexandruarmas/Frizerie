from fastapi import FastAPI, Request
from analytics.services import track_event
from datetime import datetime
import asyncio
from config.database import SessionLocal

async def test_analytics():
    # Create a mock request
    class MockRequest:
        def __init__(self):
            self.client = type('Client', (), {'host': '127.0.0.1'})()
            self.headers = {'user-agent': 'test-agent'}

    # Test different event types
    test_cases = [
        {
            "event_type": "page_view",
            "properties": {
                "page": "/home",
                "method": "GET",
                "query_params": {}
            },
            "user_id": 1,
            "stylist_id": None,
            "service_id": None,
            "booking_id": None
        },
        {
            "event_type": "booking_created",
            "properties": {
                "booking_details": "Test booking",
                "method": "POST"
            },
            "user_id": 1,
            "stylist_id": 2,
            "service_id": 3,
            "booking_id": "TEST-123"
        },
        {
            "event_type": "service_viewed",
            "properties": {
                "service_name": "Test Service",
                "method": "GET"
            },
            "user_id": 1,
            "stylist_id": None,
            "service_id": 3,
            "booking_id": None
        }
    ]

    print("\nTesting analytics tracking...")
    print("----------------------------")

    db = SessionLocal()
    try:
        for test_case in test_cases:
            try:
                print(f"\nTesting {test_case['event_type']}...")
                track_event(
                    db=db,
                    event_type=test_case['event_type'],
                    properties=test_case['properties'],
                    user_id=test_case['user_id'],
                    stylist_id=test_case['stylist_id'],
                    service_id=test_case['service_id'],
                    booking_id=test_case['booking_id']
                )
                print(f"✓ Successfully tracked {test_case['event_type']}")
            except Exception as e:
                print(f"✗ Error tracking {test_case['event_type']}: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_analytics()) 