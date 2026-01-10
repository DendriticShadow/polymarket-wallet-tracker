"""
Quick test script to check Polymarket API response structure
"""
import requests
import json

def test_polymarket_api():
    """Test Polymarket API endpoints"""

    print("=" * 60)
    print("Testing Polymarket API")
    print("=" * 60)

    # Test trades endpoint
    print("\n1. Testing trades endpoint...")
    try:
        url = "https://data-api.polymarket.com/trades"
        params = {"limit": 1}
        response = requests.get(url, params=params, timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Response type: {type(data)}")
            if isinstance(data, list) and len(data) > 0:
                print(f"Number of trades: {len(data)}")
                print("\nFirst trade structure:")
                print(json.dumps(data[0], indent=2))
            elif isinstance(data, dict):
                print("\nResponse structure:")
                print(json.dumps(data, indent=2)[:500])
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

    # Test markets endpoint
    print("\n2. Testing markets endpoint...")
    try:
        url = "https://gamma-api.polymarket.com/markets"
        params = {"limit": 1}
        response = requests.get(url, params=params, timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Response type: {type(data)}")
            if isinstance(data, list) and len(data) > 0:
                print(f"Number of markets: {len(data)}")
                print("\nFirst market structure:")
                print(json.dumps(data[0], indent=2)[:500])
            elif isinstance(data, dict):
                print("\nResponse structure:")
                print(json.dumps(data, indent=2)[:500])
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 60)
    print("Test complete")
    print("=" * 60)


if __name__ == "__main__":
    test_polymarket_api()
