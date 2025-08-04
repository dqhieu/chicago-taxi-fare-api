#!/usr/bin/env python3
"""
Test script for Chicago Taxi Fare Prediction API
"""

import requests
import json
from datetime import datetime

# API base URL
API_URL = "http://localhost:5001"

def test_health_check():
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_single_prediction():
    """Test single fare prediction"""
    print("\n🎯 Testing single prediction...")
    
    # Sample trip data
    trip_data = {
        "trip_miles": 5.2,
        "trip_seconds": 1800,  # 30 minutes
        "pickup_community_area": 73,
        "dropoff_community_area": 53,
        "trip_start_timestamp": "2021-06-15T14:30:00",
        "payment_type": "Credit Card",
        "company": "Chicago Taxi"
    }
    
    response = requests.post(f"{API_URL}/predict", json=trip_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Predicted Fare: ${result['predicted_fare']}")
        print(f"Confidence Interval: ${result['confidence_interval']['lower']} - ${result['confidence_interval']['upper']}")
        print(f"Business Category: {result['business_category']}")
        print(f"Model RMSE: {result['model_info']['rmse_percentage']}%")
    else:
        print(f"Error: {response.json()}")
    
    return response.status_code == 200

def test_batch_prediction():
    """Test batch fare predictions"""
    print("\n📊 Testing batch prediction...")
    
    trips = [
        {
            "trip_miles": 2.1,
            "trip_seconds": 900,
            "pickup_community_area": 23,
            "dropoff_community_area": 32,
            "trip_start_timestamp": "2021-06-15T09:00:00"
        },
        {
            "trip_miles": 8.5,
            "trip_seconds": 2400,
            "pickup_community_area": 5,
            "dropoff_community_area": 69,
            "trip_start_timestamp": "2021-06-15T19:30:00"
        }
    ]
    
    response = requests.post(f"{API_URL}/batch_predict", json={"trips": trips})
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Predictions count: {result['count']}")
        for i, pred in enumerate(result['predictions']):
            if 'predicted_fare' in pred:
                print(f"  Trip {i+1}: ${pred['predicted_fare']} ({pred['business_category']})")
            else:
                print(f"  Trip {i+1}: Error - {pred.get('error', 'Unknown')}")
    else:
        print(f"Error: {response.json()}")
    
    return response.status_code == 200

if __name__ == "__main__":
    print("🧪 CHICAGO FARE API TESTING SUITE")
    print("=" * 50)
    
    print("⚠️  Make sure the API is running on port 5001: python api/chicago_fare_api.py")
    print("\nPress Enter to start testing...")
    input()
    
    try:
        # Run tests
        health_ok = test_health_check()
        single_ok = test_single_prediction()
        batch_ok = test_batch_prediction()
        
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS:")
        print(f"   Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
        print(f"   Single Prediction: {'✅ PASS' if single_ok else '❌ FAIL'}")
        print(f"   Batch Prediction: {'✅ PASS' if batch_ok else '❌ FAIL'}")
        
        if all([health_ok, single_ok, batch_ok]):
            print("\n🎉 ALL TESTS PASSED! API is production ready!")
        else:
            print("\n⚠️  Some tests failed. Check API implementation.")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ CONNECTION ERROR: Make sure API is running on localhost:5001")
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
