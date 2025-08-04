#!/usr/bin/env python3
"""
Production API Testing Suite for Chicago Taxi Fare API
Tests health, single prediction, batch prediction, and error handling
"""

import requests
import json
import time
import sys
from datetime import datetime

class ProductionAPITester:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Chicago-Taxi-API-Tester/1.0'
        })
    
    def test_health_check(self):
        """Test health check endpoint"""
        print("🔍 Testing health check endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed")
                print(f"   Status: {data.get('status')}")
                print(f"   Model: {data.get('model')}")
                print(f"   Version: {data.get('version')}")
                print(f"   Production Ready: {data.get('production_ready')}")
                
                if data.get('performance'):
                    print(f"   RMSE: {data['performance'].get('rmse_percentage')}%")
                    print(f"   R²: {data['performance'].get('r2_score')}")
                
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_single_prediction(self):
        """Test single fare prediction"""
        print("\n🎯 Testing single prediction...")
        
        # Test data for a typical Chicago trip
        trip_data = {
            "trip_miles": 5.2,
            "trip_seconds": 1800,  # 30 minutes
            "pickup_community_area": 73,  # High demand area
            "dropoff_community_area": 53,
            "trip_start_timestamp": "2021-06-15T14:30:00",
            "payment_type": "Credit Card"
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/predict", 
                json=trip_data, 
                timeout=30
            )
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                predicted_fare = data.get('predicted_fare')
                
                print(f"✅ Single prediction successful")
                print(f"   Predicted Fare: ${predicted_fare}")
                print(f"   Confidence: ${data['confidence_interval']['lower']:.2f} - ${data['confidence_interval']['upper']:.2f}")
                print(f"   Category: {data.get('business_category')}")
                print(f"   Response Time: {response_time:.0f}ms")
                
                # Validate prediction is reasonable
                if 5 <= predicted_fare <= 100:
                    print(f"   ✅ Fare prediction within reasonable range")
                    return True
                else:
                    print(f"   ⚠️  Fare prediction seems unusual: ${predicted_fare}")
                    return False
                    
            else:
                print(f"❌ Single prediction failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Single prediction error: {e}")
            return False
    
    def test_batch_prediction(self):
        """Test batch fare prediction"""
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
            },
            {
                "trip_miles": 12.3,
                "trip_seconds": 3600,
                "pickup_community_area": 32,
                "dropoff_community_area": 77,
                "trip_start_timestamp": "2021-06-15T22:00:00"
            }
        ]
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/batch_predict", 
                json={"trips": trips}, 
                timeout=60
            )
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                predictions = data.get('predictions', [])
                
                print(f"✅ Batch prediction successful")
                print(f"   Total Trips: {data.get('count')}")
                print(f"   Successful: {data.get('successful')}")
                print(f"   Failed: {data.get('failed')}")
                print(f"   Response Time: {response_time:.0f}ms")
                
                for i, pred in enumerate(predictions[:3]):  # Show first 3
                    if 'error' not in pred:
                        print(f"   Trip {i+1}: ${pred['predicted_fare']} ({pred['business_category']})")
                    else:
                        print(f"   Trip {i+1}: Error - {pred['error']}")
                
                return data.get('successful', 0) > 0
                
            else:
                print(f"❌ Batch prediction failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Batch prediction error: {e}")
            return False
    
    def test_error_handling(self):
        """Test API error handling"""
        print("\n🚨 Testing error handling...")
        
        # Test missing required field
        invalid_data = {
            "trip_miles": 5.2
            # Missing required fields
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/predict", 
                json=invalid_data, 
                timeout=10
            )
            
            if response.status_code == 400:
                data = response.json()
                print(f"✅ Error handling working correctly")
                print(f"   Status: {response.status_code}")
                print(f"   Error: {data.get('error')}")
                return True
            else:
                print(f"⚠️  Unexpected response for invalid data: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error handling test failed: {e}")
            return False
    
    def test_performance(self):
        """Test API performance"""
        print("\n⚡ Testing performance...")
        
        trip_data = {
            "trip_miles": 5.0,
            "trip_seconds": 1500,
            "pickup_community_area": 32,
            "dropoff_community_area": 73,
            "trip_start_timestamp": "2021-06-15T12:00:00"
        }
        
        response_times = []
        successful_requests = 0
        
        for i in range(10):
            try:
                start_time = time.time()
                response = self.session.post(
                    f"{self.base_url}/predict", 
                    json=trip_data, 
                    timeout=10
                )
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    response_times.append(response_time)
                    successful_requests += 1
                
            except Exception:
                pass
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            
            print(f"✅ Performance test completed")
            print(f"   Successful Requests: {successful_requests}/10")
            print(f"   Average Response Time: {avg_time:.0f}ms")
            print(f"   Min Response Time: {min_time:.0f}ms")
            print(f"   Max Response Time: {max_time:.0f}ms")
            
            # Performance benchmarks
            if avg_time < 1000:  # Under 1 second
                print(f"   ✅ Performance: Excellent")
                return True
            elif avg_time < 2000:  # Under 2 seconds
                print(f"   ✅ Performance: Good")
                return True
            else:
                print(f"   ⚠️  Performance: Needs improvement")
                return False
        else:
            print(f"❌ Performance test failed - no successful requests")
            return False
    
    def run_all_tests(self):
        """Run all tests and provide summary"""
        print("🧪 CHICAGO TAXI FARE API - PRODUCTION TESTING SUITE")
        print("=" * 60)
        print(f"Testing API at: {self.base_url}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print()
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Single Prediction", self.test_single_prediction),
            ("Batch Prediction", self.test_batch_prediction),
            ("Error Handling", self.test_error_handling),
            ("Performance", self.test_performance)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            results[test_name] = test_func()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(results.values())
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name:<20}: {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! API is production ready!")
            return True
        else:
            print("⚠️  Some tests failed. Please check the issues above.")
            return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_production_api.py <API_URL>")
        print("Example: python test_production_api.py https://your-api.herokuapp.com")
        sys.exit(1)
    
    api_url = sys.argv[1]
    tester = ProductionAPITester(api_url)
    
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()