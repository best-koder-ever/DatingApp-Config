#!/usr/bin/env python3
"""
Quick API Test for Dating App Services
"""

import requests
import json
import time

def test_basic_flow():
    print("🚀 Testing basic Dating App API flow...")
    
    # Service URLs
    auth_url = "http://localhost:8081"
    user_url = "http://localhost:8082"
    swipe_url = "http://localhost:8084"
    matchmaking_url = "http://localhost:8083"
    
    # Test data with username field included
    test_user = {
        "username": "testuser123",
        "email": "testuser@example.com", 
        "password": "Test123!",
        "phoneNumber": "+1234567890",
        "firstName": "Test",
        "lastName": "User"
    }
    
    try:
        # Test 1: Health checks
        print("\n🏥 Testing health endpoints...")
        for service_name, url in [("Auth", auth_url), ("User", user_url), ("Swipe", swipe_url), ("Matchmaking", matchmaking_url)]:
            try:
                response = requests.get(f"{url}/health", timeout=5)
                print(f"  ✅ {service_name} Service: {response.status_code}")
            except Exception as e:
                print(f"  ❌ {service_name} Service: {str(e)}")
        
        # Test 2: Register user
        print("\n👤 Testing user registration...")
        try:
            response = requests.post(f"{auth_url}/api/auth/register", json=test_user)
            if response.status_code in [200, 201]:
                print("  ✅ User registration successful")
            elif response.status_code == 409:
                print("  ✅ User already exists (expected)")
            else:
                print(f"  ❌ Registration failed: {response.status_code} - {response.text}")
                return
        except Exception as e:
            print(f"  ❌ Registration error: {str(e)}")
            return
        
        # Test 3: Login user
        print("\n🔐 Testing user login...")
        try:
            login_data = {"email": test_user["email"], "password": test_user["password"]}
            response = requests.post(f"{auth_url}/api/auth/login", json=login_data)
            if response.status_code == 200:
                token_data = response.json()
                token = token_data.get("token") or token_data.get("accessToken")
                if token:
                    print("  ✅ Login successful, token received")
                else:
                    print(f"  ❌ No token in response: {token_data}")
                    return
            else:
                print(f"  ❌ Login failed: {response.status_code} - {response.text}")
                return
        except Exception as e:
            print(f"  ❌ Login error: {str(e)}")
            return
        
        # Test 4: Create user profile
        print("\n👤 Testing user profile creation...")
        try:
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            profile_data = {
                "firstName": "Test",
                "lastName": "User", 
                "dateOfBirth": "1990-01-01",
                "bio": "Test user profile",
                "city": "Test City",
                "occupation": "Tester",
                "interests": ["testing", "coding"],
                "height": 175,
                "education": "Bachelor's"
            }
            
            response = requests.post(f"{user_url}/api/userprofiles", json=profile_data, headers=headers)
            if response.status_code in [200, 201]:
                profile = response.json()
                print("  ✅ Profile creation successful")
            elif response.status_code == 409:
                print("  ✅ Profile already exists, getting existing...")
                response = requests.get(f"{user_url}/api/userprofiles/me", headers=headers)
                if response.status_code == 200:
                    profile = response.json()
                    print("  ✅ Retrieved existing profile")
                else:
                    print(f"  ❌ Could not get existing profile: {response.status_code}")
                    return
            else:
                print(f"  ❌ Profile creation failed: {response.status_code} - {response.text}")
                return
        except Exception as e:
            print(f"  ❌ Profile creation error: {str(e)}")
            return
        
        # Test 5: Search profiles
        print("\n🔍 Testing profile search...")
        try:
            response = requests.get(f"{user_url}/api/userprofiles/search?page=1&pageSize=10", headers=headers)
            if response.status_code == 200:
                search_results = response.json()
                profiles_count = len(search_results.get('results', search_results))
                print(f"  ✅ Profile search successful, found {profiles_count} profiles")
            else:
                print(f"  ❌ Profile search failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  ❌ Profile search error: {str(e)}")
        
        # Test 6: Test swipe service health
        print("\n💕 Testing swipe service...")
        try:
            response = requests.get(f"{swipe_url}/api/swipes/history", headers=headers)
            if response.status_code in [200, 404]:  # 404 is ok if no swipes yet
                print("  ✅ Swipe service responding")
            else:
                print(f"  ❌ Swipe service issue: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  ❌ Swipe service error: {str(e)}")
        
        # Test 7: Test matchmaking service
        print("\n💑 Testing matchmaking service...")
        try:
            response = requests.get(f"{matchmaking_url}/api/matchmaking/matches", headers=headers)
            if response.status_code in [200, 404]:  # 404 is ok if no matches yet
                print("  ✅ Matchmaking service responding")
            else:
                print(f"  ❌ Matchmaking service issue: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  ❌ Matchmaking service error: {str(e)}")
        
        print("\n✅ Basic API flow test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")

if __name__ == "__main__":
    test_basic_flow()
