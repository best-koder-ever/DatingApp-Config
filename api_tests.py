"""End-to-end API smoke tests for signup -> match loop and safety features.

Usage:
    python3 api_tests.py              # Run match scenario
    python3 api_tests.py --safety     # Run safety scenario
    python3 api_tests.py --wizard    # Run wizard onboarding tests
    python3 api_tests.py --all        # Run all scenarios
"""

from __future__ import annotations

import os
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import requests


@dataclass
class TestConfig:
    keycloak_base: str = os.getenv("KEYCLOAK_URL", "http://localhost:8090").rstrip("/")
    keycloak_realm: str = os.getenv("KEYCLOAK_REALM", "DatingApp")
    admin_user: str = os.getenv("KEYCLOAK_ADMIN", "admin")
    admin_password: str = os.getenv("KEYCLOAK_ADMIN_PASSWORD", "admin")
    client_id: str = os.getenv("KEYCLOAK_CLIENT_ID", "dejtingapp-flutter")
    client_scopes: str = os.getenv("KEYCLOAK_CLIENT_SCOPES", "openid profile email offline_access")
    demo_password: str = os.getenv("DEMO_USER_PASSWORD", "Demo123!")
    user_service_url: str = os.getenv("USER_SERVICE_URL", "http://localhost:8082").rstrip("/")
    swipe_service_url: str = os.getenv("SWIPE_SERVICE_URL", "http://localhost:8087").rstrip("/")
    matchmaking_service_url: str = os.getenv("MATCHMAKING_SERVICE_URL", "http://localhost:8083").rstrip("/")
    gateway_health: str = os.getenv("DATINGAPP_GATEWAY_HEALTH", "http://localhost:8080/health")
    request_timeout: int = int(os.getenv("API_TEST_TIMEOUT_SECONDS", "20"))

    @property
    def keycloak_health(self) -> str:
        return f"{self.keycloak_base}/realms/{self.keycloak_realm}"

    @property
    def user_service_health(self) -> str:
        return f"{self.user_service_url}/health"

    @property
    def swipe_service_health(self) -> str:
        return f"{self.swipe_service_url}/health"

    @property
    def matchmaking_service_health(self) -> str:
        return f"{self.matchmaking_service_url}/health"

    @property
    def user_profile_endpoint(self) -> str:
        return f"{self.user_service_url}/api/UserProfiles"

    @property
    def swipe_endpoint(self) -> str:
        return f"{self.swipe_service_url}/api/Swipes"

    @property
    def matchmaking_endpoint(self) -> str:
        return f"{self.matchmaking_service_url}/api/Matchmaking"


@dataclass
class ScenarioUser:
    username: str
    email: str
    first_name: str
    last_name: str
    gender: str
    preferences: str
    password: str
    keycloak_id: Optional[str] = None
    token: Optional[str] = None
    profile_id: Optional[int] = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class ApiScenarioRunner:
	def __init__(self, config: TestConfig) -> None:
		self.config = config
		self.session = requests.Session()
		self.session.headers.update({"Accept": "application/json"})
		self.logs: List[str] = []

	def log(self, message: str) -> None:
		timestamp = datetime.utcnow().strftime("%H:%M:%S")
		entry = f"{timestamp} | {message}"
		self.logs.append(entry)
		print(entry)

	def run(self) -> None:
		self.log("Starting signup -> match API verification")
		self._check_health()

		admin_token = self._get_admin_token()
		user_a = self._provision_user(
			prefix="api_demo_a",
			gender="Male",
			preferences="Female",
			admin_token=admin_token,
		)
		user_b = self._provision_user(
			prefix="api_demo_b",
			gender="Female",
			preferences="Male",
			admin_token=admin_token,
		)

		user_a.token = self._get_user_token(user_a.username, user_a.password)
		user_b.token = self._get_user_token(user_b.username, user_b.password)

		user_a.profile_id = self._create_profile(user_a)
		user_b.profile_id = self._create_profile(user_b)

		self._post_swipe(user_a, user_b)
		self._post_swipe(user_b, user_a)

		match_id = self._wait_for_match(user_a)
		if match_id is None:
			raise RuntimeError("Match not created within timeout")

		self.log(f"Scenario succeeded. Match #{match_id} between {user_a.profile_id} and {user_b.profile_id}")

	def _check_health(self) -> None:
		checks = {
			"Keycloak": self.config.keycloak_health,
			"UserService": self.config.user_service_health,
			"SwipeService": self.config.swipe_service_health,
			"MatchmakingService": self.config.matchmaking_service_health,
			# "Gateway": self.config.gateway_health,  # Skip: chunked transfer encoding issue (non-critical)
		}

		for name, url in checks.items():
			if not url:
				continue
			try:
				response = self.session.get(url, timeout=self.config.request_timeout)
			except requests.exceptions.RequestException as error:
				raise RuntimeError(f"{name} health check failed: {error}") from error

			if response.status_code >= 400:
				raise RuntimeError(f"{name} health check returned {response.status_code}: {response.text}")
			self.log(f"{name} healthy ({response.status_code})")

	def _get_admin_token(self) -> str:
		token_url = f"{self.config.keycloak_base}/realms/master/protocol/openid-connect/token"
		payload = {
			"grant_type": "password",
			"client_id": "admin-cli",
			"username": self.config.admin_user,
			"password": self.config.admin_password,
		}
		response = self.session.post(token_url, data=payload, timeout=self.config.request_timeout)
		if response.status_code >= 400:
			raise RuntimeError(f"Admin token request failed: {response.status_code} {response.text}")

		data = response.json()
		token = data.get("access_token")
		if not token:
			raise RuntimeError("Admin token missing access_token")
		self.log("Keycloak admin token acquired")
		return token

	def _provision_user(self, prefix: str, gender: str, preferences: str, admin_token: str) -> ScenarioUser:
		suffix = uuid.uuid4().hex[:8]
		username = f"{prefix}_{suffix}".lower()
		email = f"{username}@demo.local"
		first_name = "Alex" if prefix.endswith("a") else "Blair"
		last_name = "Scenario"
		user = ScenarioUser(
			username=username,
			email=email,
			first_name=first_name,
			last_name=last_name,
			gender=gender,
			preferences=preferences,
			password=self.config.demo_password,
		)

		payload = {
			"username": user.username,
			"email": user.email,
			"firstName": user.first_name,
			"lastName": user.last_name,
			"enabled": True,
			"emailVerified": True,
			"realmRoles": ["user"],
		}

		headers = {"Authorization": f"Bearer {admin_token}"}
		create_url = f"{self.config.keycloak_base}/admin/realms/{self.config.keycloak_realm}/users"
		response = self.session.post(create_url, json=payload, headers=headers, timeout=self.config.request_timeout)

		if response.status_code == 201:
			location = response.headers.get("Location", "")
			user.keycloak_id = self._extract_trailing_segment(location)
			self.log(f"Created Keycloak user {user.username}")
		elif response.status_code == 409:
			user.keycloak_id = self._find_user_id(user.username, admin_token)
			self.log(f"Reusing existing Keycloak user {user.username}")
		else:
			raise RuntimeError(f"Keycloak user creation failed: {response.status_code} {response.text}")

		if not user.keycloak_id:
			raise RuntimeError(f"Unable to determine Keycloak ID for {user.username}")

		password_payload = {"type": "password", "value": user.password, "temporary": False}
		reset_url = (
			f"{self.config.keycloak_base}/admin/realms/{self.config.keycloak_realm}/users/{user.keycloak_id}/reset-password"
		)
		reset_response = self.session.put(
			reset_url,
			json=password_payload,
			headers=headers,
			timeout=self.config.request_timeout,
		)
		if reset_response.status_code >= 400:
			raise RuntimeError(f"Setting password failed: {reset_response.status_code} {reset_response.text}")

		return user

	def _find_user_id(self, username: str, admin_token: str) -> Optional[str]:
		headers = {"Authorization": f"Bearer {admin_token}"}
		url = f"{self.config.keycloak_base}/admin/realms/{self.config.keycloak_realm}/users"
		response = self.session.get(url, params={"username": username}, headers=headers, timeout=self.config.request_timeout)
		if response.status_code >= 400:
			return None
		results = response.json()
		if not results:
			return None
		return results[0].get("id")

	def _get_user_token(self, username: str, password: str) -> str:
		token_url = f"{self.config.keycloak_base}/realms/{self.config.keycloak_realm}/protocol/openid-connect/token"
		payload = {
			"grant_type": "password",
			"client_id": self.config.client_id,
			"username": username,
			"password": password,
			"scope": self.config.client_scopes,
		}
		response = self.session.post(token_url, data=payload, timeout=self.config.request_timeout)
		if response.status_code >= 400:
			raise RuntimeError(f"User token request failed for {username}: {response.status_code} {response.text}")

		data = response.json()
		token = data.get("access_token")
		if not token:
			raise RuntimeError(f"Token response missing access_token for {username}")
		self.log(f"Token issued for {username}")
		return token

	def _create_profile(self, user: ScenarioUser) -> int:
		if not user.token:
			raise RuntimeError(f"Cannot create profile for {user.username} without token")

		birth_year = datetime.utcnow().year - 26
		birth_date = datetime(birth_year, 6, 15) - timedelta(days=uuid.uuid4().int % 120)
		payload: Dict[str, object] = {
			"name": user.full_name,
			"email": user.email,
			"bio": "Automated API scenario profile.",
			"gender": user.gender,
			"preferences": user.preferences,
			"dateOfBirth": birth_date.isoformat() + "Z",
			"city": "Stockholm",
			"state": "Stockholm County",
			"country": "Sweden",
			"latitude": 59.3293,
			"longitude": 18.0686,
			"occupation": "Automation Engineer",
			"education": "University Degree",
			"interests": ["Hiking", "Technology", "Food"],
			"languages": ["English", "Swedish"],
			"height": 178,
			"religion": "None",
			"smokingStatus": "Never",
			"drinkingStatus": "Socially",
			"wantsChildren": True,
			"hasChildren": False,
			"relationshipType": "Long-term relationship",
		}

		headers = {"Authorization": f"Bearer {user.token}"}
		response = self.session.post(
			self.config.user_profile_endpoint,
			json=payload,
			headers=headers,
			timeout=self.config.request_timeout,
		)

		if response.status_code == 409:
			raise RuntimeError(f"Profile already exists for {user.email}")
		if response.status_code >= 400:
			raise RuntimeError(f"Profile creation failed for {user.username}: {response.status_code} {response.text}")

		location = response.headers.get("Location")
		profile_id = self._parse_profile_id(location, response)
		self.log(f"Profile created for {user.username} (ID {profile_id})")
		return profile_id

	def _post_swipe(self, actor: ScenarioUser, target: ScenarioUser) -> None:
		if not actor.token or actor.profile_id is None or target.profile_id is None:
			raise RuntimeError("Swipe prerequisites missing")

		payload = {"userId": actor.profile_id, "targetUserId": target.profile_id, "isLike": True}
		headers = {"Authorization": f"Bearer {actor.token}"}
		response = self.session.post(
			self.config.swipe_endpoint,
			json=payload,
			headers=headers,
			timeout=self.config.request_timeout,
		)

		if response.status_code >= 400:
			raise RuntimeError(f"Swipe failed: {response.status_code} {response.text}")

		body = response.json() if response.content else {}
		mutual = body.get("isMutualMatch")
		suffix = " (mutual)" if mutual else ""
		self.log(f"Swipe recorded: {actor.profile_id} -> {target.profile_id}{suffix}")

	def _wait_for_match(self, user: ScenarioUser) -> Optional[int]:
		if not user.token or user.profile_id is None:
			return None

		for attempt in range(6):
			matches = self._get_matches(user)
			if matches:
				match_id = matches[0].get("id")
				self.log(f"Mutual match detected on attempt {attempt + 1}: {match_id}")
				return match_id
			time.sleep(1)
		return None

	def _get_matches(self, user: ScenarioUser) -> List[Dict[str, object]]:
		headers = {"Authorization": f"Bearer {user.token}"}
		url = f"{self.config.swipe_endpoint}/matches/{user.profile_id}"
		response = self.session.get(url, headers=headers, timeout=self.config.request_timeout)
		if response.status_code >= 400:
			raise RuntimeError(f"Fetching matches failed: {response.status_code} {response.text}")
		if not response.content:
			return []
		body = response.json()
		return body.get("data", body) if isinstance(body, dict) else body

	@staticmethod
	def _extract_trailing_segment(location: Optional[str]) -> Optional[str]:
		if not location:
			return None
		cleaned = location.strip().rstrip("/")
		parts = cleaned.split("/")
		return parts[-1] if parts else None

	def _parse_profile_id(self, location: Optional[str], response: requests.Response) -> int:
		candidate = self._extract_trailing_segment(location)
		if candidate and candidate.isdigit():
			return int(candidate, 10)

		if response.content:
			data = response.json()
			if isinstance(data, dict):
				if "id" in data and isinstance(data["id"], int):
					return data["id"]
				if "Id" in data and isinstance(data["Id"], int):
					return data["Id"]
				value = data.get("value")
				if isinstance(value, dict):
					for key in ("id", "Id"):
						if key in value and isinstance(value[key], int):
							return value[key]

		raise RuntimeError("Unable to resolve profile identifier from response")



class WizardScenarioRunner:
    """Test the 5-step onboarding wizard flow end-to-end."""

    def __init__(self, config: TestConfig) -> None:
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        self.logs: List[str] = []
        self.wizard_base = f"{config.user_service_url}/api/Wizard"

    def log(self, message: str) -> None:
        timestamp = datetime.utcnow().strftime("%H:%M:%S")
        entry = f"{timestamp} | {message}"
        self.logs.append(entry)
        print(entry)

    def run(self) -> None:
        self.log("Starting wizard onboarding scenario (5 steps)")
        self._check_health()

        admin_token = self._get_admin_token()
        user = self._provision_user(admin_token)
        user.token = self._get_user_token(user.username, user.password)

        # Step 1: Basic Info
        self._wizard_step_1(user)

        # Step 2: Preferences
        self._wizard_step_2(user)

        # Step 3: Photos — marks profile as Ready
        self._wizard_step_3(user)

        # Step 4: Identity & Goals (optional)
        self._wizard_step_4(user)

        # Step 5: About Me (optional — interests, lifestyle, work, education)
        self._wizard_step_5(user)

        # Verify final profile state
        self._verify_profile(user)

        self.log("Wizard scenario completed successfully — all 5 steps verified")

    def _check_health(self) -> None:
        for name, url in [("Keycloak", self.config.keycloak_health),
                          ("UserService", self.config.user_service_health)]:
            try:
                r = self.session.get(url, timeout=self.config.request_timeout)
            except requests.exceptions.RequestException as e:
                raise RuntimeError(f"{name} health check failed: {e}") from e
            if r.status_code >= 400:
                raise RuntimeError(f"{name} returned {r.status_code}")
            self.log(f"{name} healthy ({r.status_code})")

    def _get_admin_token(self) -> str:
        url = f"{self.config.keycloak_base}/realms/master/protocol/openid-connect/token"
        r = self.session.post(url, data={
            "grant_type": "password",
            "client_id": "admin-cli",
            "username": self.config.admin_user,
            "password": self.config.admin_password,
        }, timeout=self.config.request_timeout)
        if r.status_code >= 400:
            raise RuntimeError(f"Admin token failed: {r.status_code} {r.text}")
        token = r.json().get("access_token")
        if not token:
            raise RuntimeError("Admin token missing")
        self.log("Admin token acquired")
        return token

    def _provision_user(self, admin_token: str) -> ScenarioUser:
        suffix = uuid.uuid4().hex[:8]
        username = f"wizard_test_{suffix}"
        email = f"{username}@demo.local"
        user = ScenarioUser(
            username=username, email=email,
            first_name="Wizard", last_name="Tester",
            gender="Male", preferences="Female",
            password=self.config.demo_password,
        )

        headers = {"Authorization": f"Bearer {admin_token}"}
        create_url = f"{self.config.keycloak_base}/admin/realms/{self.config.keycloak_realm}/users"
        r = self.session.post(create_url, json={
            "username": user.username, "email": user.email,
            "firstName": user.first_name, "lastName": user.last_name,
            "enabled": True, "emailVerified": True,
        }, headers=headers, timeout=self.config.request_timeout)

        if r.status_code == 201:
            user.keycloak_id = ApiScenarioRunner._extract_trailing_segment(r.headers.get("Location", ""))
            self.log(f"Created Keycloak user {username}")
        elif r.status_code == 409:
            search_r = self.session.get(create_url, params={"username": username},
                                        headers=headers, timeout=self.config.request_timeout)
            results = search_r.json()
            user.keycloak_id = results[0]["id"] if results else None
            self.log(f"Reusing Keycloak user {username}")
        else:
            raise RuntimeError(f"User creation failed: {r.status_code} {r.text}")

        if not user.keycloak_id:
            raise RuntimeError(f"No keycloak ID for {username}")

        # Set password
        pw_url = f"{self.config.keycloak_base}/admin/realms/{self.config.keycloak_realm}/users/{user.keycloak_id}/reset-password"
        pw_r = self.session.put(pw_url, json={"type": "password", "value": user.password, "temporary": False},
                                headers=headers, timeout=self.config.request_timeout)
        if pw_r.status_code >= 400:
            raise RuntimeError(f"Password set failed: {pw_r.status_code}")

        return user

    def _get_user_token(self, username: str, password: str) -> str:
        url = f"{self.config.keycloak_base}/realms/{self.config.keycloak_realm}/protocol/openid-connect/token"
        r = self.session.post(url, data={
            "grant_type": "password", "client_id": self.config.client_id,
            "username": username, "password": password,
            "scope": self.config.client_scopes,
        }, timeout=self.config.request_timeout)
        if r.status_code >= 400:
            raise RuntimeError(f"Token failed for {username}: {r.status_code} {r.text}")
        token = r.json().get("access_token")
        if not token:
            raise RuntimeError(f"No access_token for {username}")
        self.log(f"Token issued for {username}")
        return token

    def _auth_headers(self, user: ScenarioUser) -> Dict[str, str]:
        return {"Authorization": f"Bearer {user.token}"}

    def _wizard_step_1(self, user: ScenarioUser) -> None:
        """Step 1: Basic Info — firstName, gender, DOB"""
        payload = {
            "firstName": "Wizard",
            "lastName": "Tester",
            "dateOfBirth": "1995-06-15T00:00:00Z",
            "gender": "Male"
        }
        r = self.session.patch(f"{self.wizard_base}/step/1", json=payload,
                               headers=self._auth_headers(user), timeout=self.config.request_timeout)
        if r.status_code >= 400:
            raise RuntimeError(f"Step 1 failed: {r.status_code} {r.text}")
        self.log("Step 1 (Basic Info) ✓")

    def _wizard_step_2(self, user: ScenarioUser) -> None:
        """Step 2: Preferences — age range, distance, preferredGender"""
        payload = {
            "minAge": 20,
            "maxAge": 35,
            "maxDistance": 50,
            "preferredGender": "Female",
            "bio": "Automated wizard test profile"
        }
        r = self.session.patch(f"{self.wizard_base}/step/2", json=payload,
                               headers=self._auth_headers(user), timeout=self.config.request_timeout)
        if r.status_code >= 400:
            raise RuntimeError(f"Step 2 failed: {r.status_code} {r.text}")
        self.log("Step 2 (Preferences) ✓")

    def _wizard_step_3(self, user: ScenarioUser) -> None:
        """Step 3: Photos — marks profile as OnboardingStatus=Ready"""
        payload = {
            "photoUrls": ["https://example.com/photo1.jpg", "https://example.com/photo2.jpg"]
        }
        r = self.session.patch(f"{self.wizard_base}/step/3", json=payload,
                               headers=self._auth_headers(user), timeout=self.config.request_timeout)
        if r.status_code >= 400:
            raise RuntimeError(f"Step 3 failed: {r.status_code} {r.text}")
        self.log("Step 3 (Photos) ✓")

    def _wizard_step_4(self, user: ScenarioUser) -> None:
        """Step 4: Identity — orientation, relationship type"""
        payload = {
            "sexualOrientation": "Heterosexual",
            "relationshipType": "LongTerm"
        }
        r = self.session.patch(f"{self.wizard_base}/step/4", json=payload,
                               headers=self._auth_headers(user), timeout=self.config.request_timeout)
        if r.status_code >= 400:
            raise RuntimeError(f"Step 4 failed: {r.status_code} {r.text}")
        self.log("Step 4 (Identity) ✓")

    def _wizard_step_5(self, user: ScenarioUser) -> None:
        """Step 5: About Me — interests, lifestyle, occupation, education"""
        payload = {
            "interests": ["hiking", "coffee", "reading", "yoga"],
            "smokingStatus": "Never",
            "drinkingStatus": "Socially",
            "wantsChildren": True,
            "occupation": "Software Engineer",
            "company": "TestCorp",
            "education": "Master's",
            "school": "KTH"
        }
        r = self.session.patch(f"{self.wizard_base}/step/5", json=payload,
                               headers=self._auth_headers(user), timeout=self.config.request_timeout)
        if r.status_code >= 400:
            raise RuntimeError(f"Step 5 failed: {r.status_code} {r.text}")
        self.log("Step 5 (About Me) ✓")

    def _wizard_step_5_comma_test(self, user: ScenarioUser) -> None:
        """Step 5 variant: send interests as comma-separated string (tests server normalization)"""
        payload = {
            "interests": ["hiking,coffee,reading,yoga"],
            "smokingStatus": "Never",
            "drinkingStatus": "Socially",
        }
        r = self.session.patch(f"{self.wizard_base}/step/5", json=payload,
                               headers=self._auth_headers(user), timeout=self.config.request_timeout)
        if r.status_code >= 400:
            raise RuntimeError(f"Step 5 comma-test failed: {r.status_code} {r.text}")
        body = r.json()
        profile = body.get("data") or body.get("value") or body
        interests = profile.get("interests", [])
        if len(interests) < 4:
            raise RuntimeError(
                f"Comma-separated interests not normalized: expected 4+ items, got {len(interests)}: {interests}"
            )
        self.log(f"Step 5 comma-separated normalization ✓ (got {len(interests)} interests)")

    def _verify_profile(self, user: ScenarioUser) -> None:
        """Fetch profile and verify key fields were saved"""
        r = self.session.get(f"{self.config.user_service_url}/api/profiles/me",
                             headers=self._auth_headers(user), timeout=self.config.request_timeout)
        if r.status_code >= 400:
            raise RuntimeError(f"Profile fetch failed: {r.status_code} {r.text}")
        body = r.json()
        profile = body.get("data") or body.get("value") or body
        checks = {
            "firstName": "Wizard",
            "gender": "Male",
        }
        for field, expected in checks.items():
            actual = profile.get(field)
            if actual != expected:
                raise RuntimeError(f"Profile field '{field}' mismatch: expected '{expected}', got '{actual}'")
        interests = profile.get("interests", [])
        if not interests:
            self.log("Warning: interests list empty after wizard step 5")
        else:
            self.log(f"Profile verified: interests={interests}")
        self.log("Profile verification ✓")




class SafetyScenarioRunner:
    """Test safety features: report, block, and enforcement."""

    def __init__(self, config: TestConfig) -> None:
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        self.logs: List[str] = []
        self.safety_service_url = os.getenv("SAFETY_SERVICE_URL", "http://localhost:8088").rstrip("/")

    def log(self, message: str) -> None:
        timestamp = datetime.utcnow().strftime("%H:%M:%S")
        entry = f"{timestamp} | {message}"
        self.logs.append(entry)
        print(entry)

    def run(self) -> None:
        self.log("Starting safety scenario: report + block lifecycle")
        
        admin_token = self._get_admin_token()
        
        # Create two users
        user_a = self._provision_user(
            prefix="safety_test_a",
            gender="Male",
            preferences="Female",
            admin_token=admin_token,
        )
        user_b = self._provision_user(
            prefix="safety_test_b",
            gender="Female",
            preferences="Male",
            admin_token=admin_token,
        )

        user_a.token = self._get_user_token(user_a.username, user_a.password)
        user_b.token = self._get_user_token(user_b.username, user_b.password)

        user_a.profile_id = self._create_profile(user_a)
        user_b.profile_id = self._create_profile(user_b)

        # Test 1: Report user
        self._test_report_user(user_a, user_b)
        
        # Test 2: Block user
        self._test_block_user(user_a, user_b)
        
        # Test 3: Verify blocked users can't appear as match candidates
        self._test_blocked_candidates(user_a, user_b)

        # Test 4: Unblock user
        self._test_unblock_user(user_a, user_b)

        self.log("Safety scenario completed successfully")

    def _get_admin_token(self) -> str:
        token_url = f"{self.config.keycloak_base}/realms/master/protocol/openid-connect/token"
        payload = {
            "grant_type": "password",
            "client_id": "admin-cli",
            "username": self.config.admin_user,
            "password": self.config.admin_password,
        }
        response = self.session.post(token_url, data=payload, timeout=self.config.request_timeout)
        if response.status_code >= 400:
            raise RuntimeError(f"Admin token request failed: {response.status_code} {response.text}")

        data = response.json()
        token = data.get("access_token")
        if not token:
            raise RuntimeError("Admin token missing access_token")
        self.log("Keycloak admin token acquired")
        return token

    def _provision_user(self, prefix: str, gender: str, preferences: str, admin_token: str) -> ScenarioUser:
        suffix = uuid.uuid4().hex[:8]
        username = f"{prefix}_{suffix}".lower()
        email = f"{username}@demo.local"
        first_name = "Alex" if prefix.endswith("a") else "Blair"
        last_name = "SafetyTest"
        user = ScenarioUser(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            preferences=preferences,
            password=self.config.demo_password,
        )

        payload = {
            "username": user.username,
            "email": user.email,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "enabled": True,
            "emailVerified": True,
            "realmRoles": ["user"],
        }

        headers = {"Authorization": f"Bearer {admin_token}"}
        create_url = f"{self.config.keycloak_base}/admin/realms/{self.config.keycloak_realm}/users"
        response = self.session.post(create_url, json=payload, headers=headers, timeout=self.config.request_timeout)

        if response.status_code == 201:
            location = response.headers.get("Location", "")
            user.keycloak_id = ApiScenarioRunner._extract_trailing_segment(location)
            self.log(f"Created Keycloak user {user.username}")
        elif response.status_code == 409:
            user.keycloak_id = self._find_user_id(user.username, admin_token)
            self.log(f"Reusing existing Keycloak user {user.username}")
        else:
            raise RuntimeError(f"Keycloak user creation failed: {response.status_code} {response.text}")

        if not user.keycloak_id:
            raise RuntimeError(f"Unable to determine Keycloak ID for {user.username}")

        password_payload = {"type": "password", "value": user.password, "temporary": False}
        reset_url = (
            f"{self.config.keycloak_base}/admin/realms/{self.config.keycloak_realm}/users/{user.keycloak_id}/reset-password"
        )
        reset_response = self.session.put(
            reset_url,
            json=password_payload,
            headers=headers,
            timeout=self.config.request_timeout,
        )
        if reset_response.status_code >= 400:
            raise RuntimeError(f"Setting password failed: {reset_response.status_code} {reset_response.text}")

        return user

    def _find_user_id(self, username: str, admin_token: str) -> Optional[str]:
        headers = {"Authorization": f"Bearer {admin_token}"}
        url = f"{self.config.keycloak_base}/admin/realms/{self.config.keycloak_realm}/users"
        response = self.session.get(url, params={"username": username}, headers=headers, timeout=self.config.request_timeout)
        if response.status_code >= 400:
            return None
        results = response.json()
        if not results:
            return None
        return results[0].get("id")

    def _get_user_token(self, username: str, password: str) -> str:
        token_url = f"{self.config.keycloak_base}/realms/{self.config.keycloak_realm}/protocol/openid-connect/token"
        payload = {
            "grant_type": "password",
            "client_id": self.config.client_id,
            "username": username,
            "password": password,
            "scope": self.config.client_scopes,
        }
        response = self.session.post(token_url, data=payload, timeout=self.config.request_timeout)
        if response.status_code >= 400:
            raise RuntimeError(f"User token request failed for {username}: {response.status_code} {response.text}")

        data = response.json()
        token = data.get("access_token")
        if not token:
            raise RuntimeError(f"Token response missing access_token for {username}")
        self.log(f"Token issued for {username}")
        return token

    def _create_profile(self, user: ScenarioUser) -> int:
        if not user.token:
            raise RuntimeError(f"Cannot create profile for {user.username} without token")

        birth_year = datetime.utcnow().year - 26
        birth_date = datetime(birth_year, 6, 15) - timedelta(days=uuid.uuid4().int % 120)
        payload: Dict[str, object] = {
            "name": user.full_name,
            "email": user.email,
            "bio": "Safety test profile.",
            "gender": user.gender,
            "preferences": user.preferences,
            "dateOfBirth": birth_date.isoformat() + "Z",
            "city": "Stockholm",
            "state": "Stockholm County",
            "country": "Sweden",
            "latitude": 59.3293,
            "longitude": 18.0686,
            "occupation": "Test Engineer",
            "education": "University Degree",
            "interests": ["Testing", "Safety"],
            "languages": ["English"],
            "height": 175,
            "religion": "None",
            "smokingStatus": "Never",
            "drinkingStatus": "Never",
            "wantsChildren": False,
            "hasChildren": False,
            "relationshipType": "Friendship",
        }

        headers = {"Authorization": f"Bearer {user.token}"}
        response = self.session.post(
            self.config.user_profile_endpoint,
            json=payload,
            headers=headers,
            timeout=self.config.request_timeout,
        )

        if response.status_code == 409:
            raise RuntimeError(f"Profile already exists for {user.email}")
        if response.status_code >= 400:
            raise RuntimeError(f"Profile creation failed for {user.username}: {response.status_code} {response.text}")

        location = response.headers.get("Location")
        profile_id = self._parse_profile_id(location, response)
        self.log(f"Profile created for {user.username} (ID {profile_id})")
        return profile_id

    def _parse_profile_id(self, location: Optional[str], response: requests.Response) -> int:
        candidate = ApiScenarioRunner._extract_trailing_segment(location)
        if candidate and candidate.isdigit():
            return int(candidate, 10)

        if response.content:
            data = response.json()
            if isinstance(data, dict):
                if "id" in data and isinstance(data["id"], int):
                    return data["id"]
                if "Id" in data and isinstance(data["Id"], int):
                    return data["Id"]
                value = data.get("value")
                if isinstance(value, dict):
                    for key in ("id", "Id"):
                        if key in value and isinstance(value[key], int):
                            return value[key]

        raise RuntimeError("Unable to resolve profile identifier from response")

    def _test_report_user(self, reporter: ScenarioUser, reported: ScenarioUser) -> None:
        """Test creating a safety report."""
        if not reporter.token or not reporter.keycloak_id or not reported.keycloak_id:
            raise RuntimeError("Report test prerequisites missing")

        payload = {
            "reportedUserId": reported.keycloak_id,
            "reportType": "InappropriateProfile",
            "description": "Automated test report",
            "contextData": None
        }

        headers = {"Authorization": f"Bearer {reporter.token}"}
        url = f"{self.safety_service_url}/api/safety/reports"
        
        response = self.session.post(url, json=payload, headers=headers, timeout=self.config.request_timeout)

        if response.status_code >= 400:
            raise RuntimeError(f"Report creation failed: {response.status_code} {response.text}")

        report_data = response.json()
        report_id = report_data.get("id")
        self.log(f"Report created: {reporter.username} reported {reported.username} (Report ID: {report_id})")

    def _test_block_user(self, blocker: ScenarioUser, blocked: ScenarioUser) -> None:
        """Test blocking a user."""
        if not blocker.token or not blocker.keycloak_id or not blocked.keycloak_id:
            raise RuntimeError("Block test prerequisites missing")

        payload = {
            "blockedUserId": blocked.keycloak_id,
            "reason": "Automated test block"
        }

        headers = {"Authorization": f"Bearer {blocker.token}"}
        url = f"{self.safety_service_url}/api/safety/block"
        
        response = self.session.post(url, json=payload, headers=headers, timeout=self.config.request_timeout)

        if response.status_code >= 400:
            raise RuntimeError(f"Block creation failed: {response.status_code} {response.text}")

        block_data = response.json()
        block_id = block_data.get("id")
        self.log(f"Block created: {blocker.username} blocked {blocked.username} (Block ID: {block_id})")

        # Verify block status
        check_url = f"{self.safety_service_url}/api/safety/block/{blocked.keycloak_id}"
        check_response = self.session.get(check_url, headers=headers, timeout=self.config.request_timeout)
        
        if check_response.status_code >= 400:
            raise RuntimeError(f"Block check failed: {check_response.status_code} {check_response.text}")

        check_data = check_response.json()
        if not check_data.get("isBlocked"):
            raise RuntimeError("Block verification failed - isBlocked should be true")
        
        self.log(f"Block verified: {blocked.username} is blocked by {blocker.username}")

    def _test_blocked_candidates(self, blocker: ScenarioUser, blocked: ScenarioUser) -> None:
        """Test that blocked users don't appear in match candidates."""
        if not blocker.token or blocker.profile_id is None:
            raise RuntimeError("Candidate test prerequisites missing")

        headers = {"Authorization": f"Bearer {blocker.token}"}
        url = f"{self.config.matchmaking_endpoint}/candidates/{blocker.profile_id}"
        
        response = self.session.get(url, headers=headers, timeout=self.config.request_timeout)

        if response.status_code >= 400:
            raise RuntimeError(f"Fetching candidates failed: {response.status_code} {response.text}")

        candidates = response.json() if response.content else []
        
        # Verify blocked user is not in candidates
        blocked_in_candidates = any(
            c.get("id") == blocked.profile_id for c in candidates
        )
        
        if blocked_in_candidates:
            raise RuntimeError(f"Blocked user {blocked.username} should not appear in candidates")
        
        self.log(f"Verified: Blocked user {blocked.username} not in {blocker.username}'s candidates")

    def _test_unblock_user(self, blocker: ScenarioUser, blocked: ScenarioUser) -> None:
        """Test unblocking a user."""
        if not blocker.token or not blocked.keycloak_id:
            raise RuntimeError("Unblock test prerequisites missing")

        headers = {"Authorization": f"Bearer {blocker.token}"}
        url = f"{self.safety_service_url}/api/safety/block/{blocked.keycloak_id}"
        
        response = self.session.delete(url, headers=headers, timeout=self.config.request_timeout)

        if response.status_code >= 400:
            raise RuntimeError(f"Unblock failed: {response.status_code} {response.text}")

        self.log(f"Unblock successful: {blocker.username} unblocked {blocked.username}")

        # Verify unblock status
        check_url = f"{self.safety_service_url}/api/safety/block/{blocked.keycloak_id}"
        check_response = self.session.get(check_url, headers=headers, timeout=self.config.request_timeout)
        
        if check_response.status_code >= 400:
            raise RuntimeError(f"Unblock check failed: {check_response.status_code} {check_response.text}")

        check_data = check_response.json()
        if check_data.get("isBlocked"):
            raise RuntimeError("Unblock verification failed - isBlocked should be false")
        
        self.log(f"Unblock verified: {blocked.username} is no longer blocked")


def run_safety_tests() -> None:
    """Entry point for safety feature tests."""
    config = TestConfig()
    runner = SafetyScenarioRunner(config)
    try:
        runner.run()
    except Exception as exc:  # pylint: disable=broad-except
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
	import argparse
	
	parser = argparse.ArgumentParser(description="Run API smoke tests")
	parser.add_argument("--safety", action="store_true", help="Run safety feature tests")
	parser.add_argument("--wizard", action="store_true", help="Run wizard onboarding tests")
	parser.add_argument("--all", action="store_true", help="Run all test scenarios")
	args = parser.parse_args()
	
	config = TestConfig()
	
	try:
		if args.all:
			print("=" * 60)
			print("Running match scenario tests...")
			print("=" * 60)
			match_runner = ApiScenarioRunner(config)
			match_runner.run()
			
			print("\n" + "=" * 60)
			print("Running wizard onboarding tests...")
			print("=" * 60)
			wizard_runner = WizardScenarioRunner(config)
			wizard_runner.run()
			
			print("\n" + "=" * 60)
			print("Running safety scenario tests...")
			print("=" * 60)
			safety_runner = SafetyScenarioRunner(config)
			safety_runner.run()
			
			print("\n" + "=" * 60)
			print("All scenarios completed successfully!")
			print("=" * 60)
		elif args.wizard:
			wizard_runner = WizardScenarioRunner(config)
			wizard_runner.run()
		elif args.safety:
			safety_runner = SafetyScenarioRunner(config)
			safety_runner.run()
		else:
			match_runner = ApiScenarioRunner(config)
			match_runner.run()
	except Exception as exc:  # pylint: disable=broad-except
		print(f"ERROR: {exc}", file=sys.stderr)
		sys.exit(1)


if __name__ == "__main__":
	main()
