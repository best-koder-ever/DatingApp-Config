#!/usr/bin/env python3
"""
Comprehensive API Testing Suite for Dating App Backend Services
Tests all endpoints in AuthService, UserService, SwipeService, and MatchmakingService
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatingAppAPITester:
    def __init__(self):
        # Service base URLs
        self.auth_base = "http://localhost:5001"
        self.user_base = "http://localhost:5002" 
        self.swipe_base = "http://localhost:5003"
        self.matchmaking_base = "http://localhost:5004"
        
        # Test data
        self.test_users = []
        self.auth_tokens = {}
        self.user_profiles = []
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        
    def log_result(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        if success:
            self.test_results['passed'] += 1
            logger.info(f"✅ {test_name} - PASSED {details}")
        else:
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"{test_name}: {details}")
            logger.error(f"❌ {test_name} - FAILED {details}")
    
    def make_request(self, method: str, url: str, headers: Dict = None, data: Any = None, files: Any = None) -> tuple:
        """Make HTTP request and return response and success status"""
        try:
            if headers is None:
                headers = {'Content-Type': 'application/json'}
            
            response = None
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers)
            elif method.upper() == 'POST':
                if files:
                    # Don't set Content-Type for file uploads
                    headers.pop('Content-Type', None)
                    response = requests.post(url, headers=headers, files=files, data=data)
                else:
                    response = requests.post(url, headers=headers, json=data)
            elif method.upper() == 'PUT':
                if files:
                    headers.pop('Content-Type', None)
                    response = requests.put(url, headers=headers, files=files, data=data)
                else:
                    response = requests.put(url, headers=headers, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers)
            
            return response, True
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            return None, False
    
    def test_service_health(self):
        """Test health endpoints for all services"""
        logger.info("🏥 Testing service health endpoints...")
        
        services = [
            ("AuthService", f"{self.auth_base}/health"),
            ("UserService", f"{self.user_base}/health"),
            ("SwipeService", f"{self.swipe_base}/health"),
            ("MatchmakingService", f"{self.matchmaking_base}/health")
        ]
        
        for service_name, health_url in services:
            response, success = self.make_request('GET', health_url)
            if success and response and response.status_code == 200:
                self.log_result(f"{service_name} Health Check", True)
            else:
                self.log_result(f"{service_name} Health Check", False, 
                              f"Status: {response.status_code if response else 'No response'}")
    
    def test_auth_service(self):
        """Test AuthService endpoints"""
        logger.info("🔐 Testing AuthService endpoints...")
        
        # Test user registration
        test_users_data = [
            {"email": "john@test.com", "password": "Test123!", "firstName": "John", "lastName": "Doe"},
            {"email": "jane@test.com", "password": "Test123!", "firstName": "Jane", "lastName": "Smith"},
            {"email": "bob@test.com", "password": "Test123!", "firstName": "Bob", "lastName": "Johnson"}
        ]
        
        for user_data in test_users_data:
            response, success = self.make_request('POST', f"{self.auth_base}/api/auth/register", data=user_data)
            if success and response:
                if response.status_code in [200, 201]:
                    self.log_result(f"Register user {user_data['email']}", True)
                    self.test_users.append(user_data)
                elif response.status_code == 409:  # User already exists
                    self.log_result(f"Register user {user_data['email']}", True, "(User already exists)")
                    self.test_users.append(user_data)
                else:
                    self.log_result(f"Register user {user_data['email']}", False, 
                                  f"Status: {response.status_code}, Response: {response.text}")
            else:
                self.log_result(f"Register user {user_data['email']}", False, "Request failed")
        
        # Test user login
        for user_data in self.test_users:
            login_data = {"email": user_data["email"], "password": user_data["password"]}
            response, success = self.make_request('POST', f"{self.auth_base}/api/auth/login", data=login_data)
            if success and response and response.status_code == 200:
                try:
                    token_data = response.json()
                    if 'token' in token_data:
                        self.auth_tokens[user_data['email']] = token_data['token']
                        self.log_result(f"Login user {user_data['email']}", True)
                    else:
                        self.log_result(f"Login user {user_data['email']}", False, "No token in response")
                except:
                    self.log_result(f"Login user {user_data['email']}", False, "Invalid JSON response")
            else:
                self.log_result(f"Login user {user_data['email']}", False, 
                              f"Status: {response.status_code if response else 'No response'}")
    
    def test_user_service(self):
        """Test UserService endpoints"""
        logger.info("👤 Testing UserService endpoints...")
        
        if not self.auth_tokens:
            logger.error("No auth tokens available, skipping UserService tests")
            return
        
        # Test profile creation for each user
        profile_data_templates = [
            {
                "firstName": "John", "lastName": "Doe", "dateOfBirth": "1990-01-15",
                "city": "New York", "bio": "Love hiking and coffee", "occupation": "Software Engineer",
                "interests": ["hiking", "coffee", "technology"], "height": 180, "education": "Bachelor's"
            },
            {
                "firstName": "Jane", "lastName": "Smith", "dateOfBirth": "1992-03-22",
                "city": "Los Angeles", "bio": "Artist and traveler", "occupation": "Graphic Designer",
                "interests": ["art", "travel", "photography"], "height": 165, "education": "Master's"
            },
            {
                "firstName": "Bob", "lastName": "Johnson", "dateOfBirth": "1988-07-10",
                "city": "Chicago", "bio": "Fitness enthusiast", "occupation": "Personal Trainer",
                "interests": ["fitness", "sports", "cooking"], "height": 175, "education": "Diploma"
            }
        ]
        
        user_emails = list(self.auth_tokens.keys())
        for i, email in enumerate(user_emails):
            if i < len(profile_data_templates):
                token = self.auth_tokens[email]
                headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
                
                profile_data = profile_data_templates[i]
                response, success = self.make_request('POST', f"{self.user_base}/api/userprofiles", 
                                                    headers=headers, data=profile_data)
                if success and response:
                    if response.status_code in [200, 201]:
                        self.log_result(f"Create profile for {email}", True)
                        try:
                            profile = response.json()
                            self.user_profiles.append(profile)
                        except:
                            pass
                    elif response.status_code == 409:  # Profile already exists
                        self.log_result(f"Create profile for {email}", True, "(Profile already exists)")
                        # Try to get existing profile
                        get_response, get_success = self.make_request('GET', f"{self.user_base}/api/userprofiles/me", 
                                                                    headers=headers)
                        if get_success and get_response and get_response.status_code == 200:
                            try:
                                profile = get_response.json()
                                self.user_profiles.append(profile)
                            except:
                                pass
                    else:
                        self.log_result(f"Create profile for {email}", False, 
                                      f"Status: {response.status_code}, Response: {response.text}")
                else:
                    self.log_result(f"Create profile for {email}", False, "Request failed")
        
        # Test profile search
        if self.auth_tokens:
            first_email = list(self.auth_tokens.keys())[0]
            token = self.auth_tokens[first_email]
            headers = {'Authorization': f'Bearer {token}'}
            
            search_params = "?page=1&pageSize=10&minAge=18&maxAge=35"
            response, success = self.make_request('GET', f"{self.user_base}/api/userprofiles/search{search_params}", 
                                                headers=headers)
            if success and response and response.status_code == 200:
                self.log_result("Search profiles", True)
            else:
                self.log_result("Search profiles", False, 
                              f"Status: {response.status_code if response else 'No response'}")
    
    def test_swipe_service(self):
        """Test SwipeService endpoints"""
        logger.info("💕 Testing SwipeService endpoints...")
        
        if not self.auth_tokens or len(self.user_profiles) < 2:
            logger.error("Insufficient test data for SwipeService tests")
            return
        
        user_emails = list(self.auth_tokens.keys())
        if len(user_emails) < 2:
            return
        
        # Test swipe functionality
        swiper_email = user_emails[0]
        target_email = user_emails[1]
        
        swiper_token = self.auth_tokens[swiper_email]
        headers = {'Authorization': f'Bearer {swiper_token}', 'Content-Type': 'application/json'}
        
        # Get user IDs (assuming they match the profile IDs)
        if len(self.user_profiles) >= 2:
            target_user_id = self.user_profiles[1].get('id', 2)  # Use ID from profile or fallback to 2
            
            # Test single swipe (like)
            swipe_data = {"targetUserId": target_user_id, "isLike": True}
            response, success = self.make_request('POST', f"{self.swipe_base}/api/swipes/swipe", 
                                                headers=headers, data=swipe_data)
            if success and response:
                if response.status_code in [200, 201]:
                    self.log_result("Single swipe (like)", True)
                elif response.status_code == 409:  # Already swiped
                    self.log_result("Single swipe (like)", True, "(Already swiped)")
                else:
                    self.log_result("Single swipe (like)", False, 
                                  f"Status: {response.status_code}, Response: {response.text}")
            else:
                self.log_result("Single swipe (like)", False, "Request failed")
            
            # Test swipe history
            response, success = self.make_request('GET', f"{self.swipe_base}/api/swipes/history", headers=headers)
            if success and response and response.status_code == 200:
                self.log_result("Get swipe history", True)
            else:
                self.log_result("Get swipe history", False, 
                              f"Status: {response.status_code if response else 'No response'}")
        
        # Test batch swipe
        batch_swipe_data = {
            "swipes": [
                {"targetUserId": 3, "isLike": True},
                {"targetUserId": 4, "isLike": False}
            ]
        }
        response, success = self.make_request('POST', f"{self.swipe_base}/api/swipes/batch", 
                                            headers=headers, data=batch_swipe_data)
        if success and response:
            if response.status_code in [200, 201]:
                self.log_result("Batch swipe", True)
            else:
                self.log_result("Batch swipe", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
        else:
            self.log_result("Batch swipe", False, "Request failed")
    
    def test_matchmaking_service(self):
        """Test MatchmakingService endpoints"""
        logger.info("💑 Testing MatchmakingService endpoints...")
        
        if not self.auth_tokens:
            logger.error("No auth tokens available for MatchmakingService tests")
            return
        
        first_email = list(self.auth_tokens.keys())[0]
        token = self.auth_tokens[first_email]
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test find matches
        response, success = self.make_request('GET', f"{self.matchmaking_base}/api/matchmaking/matches", 
                                            headers=headers)
        if success and response:
            if response.status_code == 200:
                self.log_result("Find matches", True)
            elif response.status_code == 404:  # No matches found
                self.log_result("Find matches", True, "(No matches found)")
            else:
                self.log_result("Find matches", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
        else:
            self.log_result("Find matches", False, "Request failed")
        
        # Test compatibility check
        if len(self.user_profiles) >= 2:
            target_user_id = self.user_profiles[1].get('id', 2)
            response, success = self.make_request('GET', 
                                                f"{self.matchmaking_base}/api/matchmaking/compatibility/{target_user_id}", 
                                                headers=headers)
            if success and response and response.status_code == 200:
                self.log_result("Compatibility check", True)
            else:
                self.log_result("Compatibility check", False, 
                              f"Status: {response.status_code if response else 'No response'}")
        
        # Test matching stats
        response, success = self.make_request('GET', f"{self.matchmaking_base}/api/matchmaking/stats", 
                                            headers=headers)
        if success and response and response.status_code == 200:
            self.log_result("Get matching stats", True)
        else:
            self.log_result("Get matching stats", False, 
                          f"Status: {response.status_code if response else 'No response'}")
    
    def run_all_tests(self):
        """Run all API tests"""
        logger.info("🚀 Starting comprehensive API testing suite...")
        
        # Test in order of dependency
        self.test_service_health()
        self.test_auth_service()
        time.sleep(1)  # Give services time to process
        self.test_user_service() 
        time.sleep(1)
        self.test_swipe_service()
        time.sleep(1)
        self.test_matchmaking_service()
        
        # Print final results
        logger.info("\n" + "="*50)
        logger.info("📊 FINAL TEST RESULTS")
        logger.info("="*50)
        logger.info(f"✅ Tests Passed: {self.test_results['passed']}")
        logger.info(f"❌ Tests Failed: {self.test_results['failed']}")
        logger.info(f"📈 Success Rate: {(self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed']) * 100):.1f}%")
        
        if self.test_results['errors']:
            logger.info("\n🔍 FAILED TESTS:")
            for error in self.test_results['errors']:
                logger.info(f"  - {error}")
        
        return self.test_results['failed'] == 0

if __name__ == "__main__":
    tester = DatingAppAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
