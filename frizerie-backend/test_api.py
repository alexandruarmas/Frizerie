import requests
import json

# Base URL for the API
base_url = "http://localhost:8000"

def test_api_root():
    """Test the root endpoint."""
    response = requests.get(base_url)
    print(f"Root endpoint response: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_health_check():
    """Test the health check endpoint."""
    response = requests.get(f"{base_url}/health")
    print(f"Health check response: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
if __name__ == "__main__":
    print("Testing Frizerie API...")
    try:
        test_api_root()
        test_health_check()
        print("\nAPI tests completed successfully!")
    except Exception as e:
        print(f"\nError testing API: {str(e)}")
        print("Make sure the backend server is running.") 