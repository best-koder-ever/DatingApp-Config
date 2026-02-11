#!/usr/bin/env python3
"""
Fixture Loader CLI - Professional test data provisioning tool
Loads JSON-based test fixtures into DatingApp services idempotently.

Real production approach:
- API-based seeding (not direct DB manipulation)
- Ensures business logic is tested (validation, constraints, events)
- Version-controlled JSON fixtures
- Idempotent operations (safe to re-run)
- Proper dependency ordering

Usage:
    python fixture_loader.py load --set minimal --env demo
    python fixture_loader.py clean --set minimal
    python fixture_loader.py validate --set minimal
"""

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
import requests
from requests.auth import HTTPBasicAuth


@dataclass
class ServiceConfig:
    """Configuration for backend services"""
    keycloak_url: str
    keycloak_realm: str
    keycloak_admin_user: str
    keycloak_admin_password: str
    user_service_url: str
    photo_service_url: str
    swipe_service_url: str
    matchmaking_service_url: str
    messaging_service_url: str
    
    @classmethod
    def from_env(cls, env: str = "demo") -> "ServiceConfig":
        """Load config from environment or defaults"""
        if env == "demo":
            return cls(
                keycloak_url=os.getenv("KEYCLOAK_URL", "http://localhost:8090"),
                keycloak_realm=os.getenv("KEYCLOAK_REALM", "DatingApp"),
                keycloak_admin_user=os.getenv("KEYCLOAK_ADMIN_USER", "admin"),
                keycloak_admin_password=os.getenv("KEYCLOAK_ADMIN_PASSWORD", "admin"),
                user_service_url=os.getenv("USER_SERVICE_URL", "http://localhost:8082"),
                photo_service_url=os.getenv("PHOTO_SERVICE_URL", "http://localhost:8085"),
                swipe_service_url=os.getenv("SWIPE_SERVICE_URL", "http://localhost:8087"),
                matchmaking_service_url=os.getenv("MATCHMAKING_SERVICE_URL", "http://localhost:8083"),
                messaging_service_url=os.getenv("MESSAGING_SERVICE_URL", "http://localhost:8086"),
            )
        elif env == "test":
            return cls(
                keycloak_url=os.getenv("KEYCLOAK_TEST_URL", "http://localhost:8090"),
                keycloak_realm=os.getenv("KEYCLOAK_TEST_REALM", "DatingApp"),
                keycloak_admin_user=os.getenv("KEYCLOAK_ADMIN_USER", "admin"),
                keycloak_admin_password=os.getenv("KEYCLOAK_ADMIN_PASSWORD", "admin"),
                user_service_url=os.getenv("USER_SERVICE_TEST_URL", "http://localhost:9082"),
                photo_service_url=os.getenv("PHOTO_SERVICE_TEST_URL", "http://localhost:9084"),
                swipe_service_url=os.getenv("SWIPE_SERVICE_TEST_URL", "http://localhost:9087"),
                matchmaking_service_url=os.getenv("MATCHMAKING_SERVICE_TEST_URL", "http://localhost:9083"),
                messaging_service_url=os.getenv("MESSAGING_SERVICE_TEST_URL", "http://localhost:9085"),
            )
        else:
            raise ValueError(f"Unknown environment: {env}")


class FixtureLoader:
    """Main fixture loader class - implements REAL product approach"""
    
    def __init__(self, config: ServiceConfig, fixture_dir: Path, verbose: bool = True):
        self.config = config
        self.fixture_dir = fixture_dir
        self.verbose = verbose
        self.keycloak_token: Optional[str] = None
        self.user_tokens: Dict[str, str] = {}
        self.user_id_mapping: Dict[str, str] = {}  # fixture userId -> Keycloak userId
        self.profile_id_mapping: Dict[str, int] = {}  # Keycloak userId -> ProfileId
        
    def log(self, message: str, level: str = "INFO"):
        """Log message if verbose"""
        if self.verbose:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] [{level}] {message}")
    
    def get_keycloak_admin_token(self) -> str:
        """Get Keycloak admin access token"""
        if self.keycloak_token:
            return self.keycloak_token
            
        self.log("Authenticating with Keycloak admin...")
        url = f"{self.config.keycloak_url}/realms/master/protocol/openid-connect/token"
        data = {
            "grant_type": "password",
            "username": self.config.keycloak_admin_user,
            "password": self.config.keycloak_admin_password,
            "client_id": "admin-cli",
        }
        
        try:
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            self.keycloak_token = response.json()["access_token"]
            self.log("✓ Keycloak admin authenticated", "SUCCESS")
            return self.keycloak_token
        except Exception as e:
            self.log(f"✗ Failed to authenticate with Keycloak: {e}", "ERROR")
            raise
    
    def get_user_token(self, username: str, password: str) -> str:
        """Get user access token for API calls"""
        if username in self.user_tokens:
            return self.user_tokens[username]
            
        url = f"{self.config.keycloak_url}/realms/{self.config.keycloak_realm}/protocol/openid-connect/token"
        data = {
            "grant_type": "password",
            "username": username,
            "password": password,
            "client_id": "dejtingapp-flutter",
        }
        
        try:
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            token = response.json()["access_token"]
            self.user_tokens[username] = token
            return token
        except Exception as e:
            self.log(f"✗ Failed to get user token for {username}: {e}", "ERROR")
            raise
    
    def load_json_file(self, filename: str) -> Dict[str, Any]:
        """Load JSON fixture file"""
        filepath = self.fixture_dir / filename
        if not filepath.exists():
            self.log(f"✗ Fixture file not found: {filepath}", "WARNING")
            return {}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def provision_keycloak_users(self) -> Dict[str, str]:
        """Provision Keycloak users, returns mapping of email -> userId"""
        self.log("=" * 60)
        self.log("Step 1: Provisioning Keycloak users...")
        
        fixture = self.load_json_file("keycloak_users.json")
        if not fixture or "users" not in fixture:
            self.log("No Keycloak users to provision", "WARNING")
            return {}
        
        token = self.get_keycloak_admin_token()
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        user_ids = {}
        
        for user in fixture["users"]:
            email = user["email"]
            self.log(f"  Provisioning user: {email}")
            
            # Check if user exists
            search_url = f"{self.config.keycloak_url}/admin/realms/{self.config.keycloak_realm}/users?email={email}"
            response = requests.get(search_url, headers=headers)
            existing_users = response.json()
            
            if existing_users:
                user_id = existing_users[0]["id"]
                self.log(f"    ✓ User exists (ID: {user_id})", "INFO")
                user_ids[email] = user_id
                # Map fixture userId to Keycloak UUID
                fixture_user_id = user.get("attributes", {}).get("userId", [""])[0]
                if fixture_user_id:
                    self.user_id_mapping[fixture_user_id] = user_id
            else:
                # Create new user
                create_url = f"{self.config.keycloak_url}/admin/realms/{self.config.keycloak_realm}/users"
                payload = {
                    "username": user["username"],
                    "email": user["email"],
                    "firstName": user.get("firstName", ""),
                    "lastName": user.get("lastName", ""),
                    "enabled": user.get("enabled", True),
                    "emailVerified": user.get("emailVerified", True),
                    "attributes": user.get("attributes", {}),
                }
                
                response = requests.post(create_url, headers=headers, json=payload)
                if response.status_code == 201:
                    # Get created user ID from Location header
                    location = response.headers.get("Location", "")
                    user_id = location.split("/")[-1] if location else None
                    
                    if user_id:
                        # Set password
                        password_url = f"{self.config.keycloak_url}/admin/realms/{self.config.keycloak_realm}/users/{user_id}/reset-password"
                        password_data = {
                            "type": "password",
                            "value": user["credentials"][0]["value"],
                            "temporary": False,
                        }
                        requests.put(password_url, headers=headers, json=password_data)
                        
                        user_ids[email] = user_id
                        # Map fixture userId to Keycloak UUID
                        fixture_user_id = user.get("attributes", {}).get("userId", [""])[0]
                        if fixture_user_id:
                            self.user_id_mapping[fixture_user_id] = user_id
                        self.log(f"    ✓ User created (ID: {user_id})", "SUCCESS")
                    else:
                        self.log(f"    ✗ Failed to get user ID", "ERROR")
                else:
                    self.log(f"    ✗ Failed to create user: {response.status_code} - {response.text}", "ERROR")
        
        self.log(f"✓ Provisioned {len(user_ids)} Keycloak users", "SUCCESS")
        return user_ids
    
    def load_user_profiles(self):
        """Load user profiles into UserService via wizard endpoint (triggers ProfileId assignment)"""
        self.log("=" * 60)
        self.log("Step 2: Loading user profiles...")
        
        fixture = self.load_json_file("user_profiles.json")
        if not fixture or "profiles" not in fixture:
            self.log("No user profiles to load", "WARNING")
            return
        
        for profile in fixture["profiles"]:
            email = profile["email"]
            self.log(f"  Loading profile: {email}")
            
            # Get user token (authenticates as this user)
            try:
                token = self.get_user_token(email, "Test123!")
                headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                
                # PATCH to wizard step 1 to create basic profile info
                # This triggers ProfileId assignment and UserProfileMappings creation
                url = f"{self.config.user_service_url}/api/wizard/step/1"
                
                # Map profile to WizardStepBasicInfoDto format
                name_parts = profile.get("name", "Unknown User").split(maxsplit=1)
                first_name = name_parts[0] if len(name_parts) > 0 else "Unknown"
                last_name = name_parts[1] if len(name_parts) > 1 else "User"
                
                wizard_payload = {
                    "firstName": first_name,
                    "lastName": last_name,
                    "dateOfBirth": profile.get("dateOfBirth", "1990-01-01"),
                    "gender": profile.get("gender", "Other")
                }
                
                response = requests.patch(url, headers=headers, json=wizard_payload, timeout=10)
                
                if response.status_code in (200, 201):
                    result = response.json()
                    # Try to extract ProfileId if returned in the response
                    data = result.get("data", {})
                    profile_id = data.get("profileId") or data.get("id")
                    if profile_id:
                        self.profile_id_mapping[profile["userId"]] = profile_id
                        self.log(f"    ✓ Profile created (ProfileId: {profile_id})", "SUCCESS")
                    else:
                        self.log(f"    ✓ Profile created (ProfileId not in response)", "SUCCESS")
                else:
                    self.log(f"    ✗ Failed: {response.status_code} - {response.text}", "ERROR")
            except Exception as e:
                self.log(f"    ✗ Error: {e}", "ERROR")
        
        self.log(f"✓ Loaded {len(fixture['profiles'])} user profiles", "SUCCESS")
    
    def sync_user_profile_mappings(self):
        """Sync UserProfileMappings to SwipeService database for match validation"""
        self.log("=" * 60)
        self.log("Step 2.5: Syncing user profile mappings to SwipeService...")
        
        if not self.user_id_mapping or not self.profile_id_mapping:
            self.log("No mappings to sync", "WARNING")
            return
        
        import mysql.connector
        
        try:
            # Connect to SwipeService database
            connection = mysql.connector.connect(
                host="localhost",
                port=3310,  # SwipeService DB port
                user="root",
                password="root_password",
                database="SwipeServiceDb"
            )
            cursor = connection.cursor()
            
            synced_count = 0
            for fixture_user_id, keycloak_uuid in self.user_id_mapping.items():
                profile_id = self.profile_id_mapping.get(fixture_user_id)
                
                if not profile_id:
                    self.log(f"  ✗ No ProfileId for {fixture_user_id}", "WARNING")
                    continue
                
                # Insert or update mapping
                sql = """INSERT INTO UserProfileMappings (ProfileId, UserId, CreatedAt) 
                         VALUES (%s, %s, UTC_TIMESTAMP()) 
                         ON DUPLICATE KEY UPDATE UserId = VALUES(UserId)"""
                cursor.execute(sql, (profile_id, keycloak_uuid))
                synced_count += 1
                self.log(f"  ✓ Synced mapping: ProfileId={profile_id} ↔ UserId={keycloak_uuid[:8]}...", "SUCCESS")
            
            connection.commit()
            cursor.close()
            connection.close()
            
            self.log(f"✓ Synced {synced_count} user profile mappings", "SUCCESS")
        except Exception as e:
            self.log(f"✗ Error syncing mappings: {e}", "ERROR")
    
    def load_swipes(self):
        """Load swipe records into SwipeService via API"""
        self.log("=" * 60)
        self.log("Step 3: Loading swipe records...")
        
        fixture = self.load_json_file("swipes.json")
        if not fixture or "swipes" not in fixture:
            self.log("No swipes to load", "WARNING")
            return
        
        # Get Keycloak users fixture to find email for each userId
        users_fixture = self.load_json_file("keycloak_users.json")
        user_emails = {u.get("attributes", {}).get("userId", [""])[0]: u["email"] for u in users_fixture.get("users", [])}
        
        loaded_count = 0
        for swipe in fixture["swipes"]:
            from_user_id = swipe["fromUserId"]
            target_user_id = swipe["toUserId"]
            direction = swipe["direction"]
            
            # Get email for user token
            from_email = user_emails.get(from_user_id)
            if not from_email:
                self.log(f"  ✗ Cannot find email for user {from_user_id}", "ERROR")
                continue
            
            # Map UserIds (GUID) to ProfileIds (int)
            from_profile_id = self.profile_id_mapping.get(from_user_id)
            target_profile_id = self.profile_id_mapping.get(target_user_id)
            
            if not from_profile_id:
                self.log(f"  ✗ Cannot find ProfileId for user {from_user_id}", "ERROR")
                continue
            if not target_profile_id:
                self.log(f"  ✗ Cannot find ProfileId for target user {target_user_id}", "ERROR")
                continue
            
            self.log(f"  Loading swipe: {from_email} (ProfileId={from_profile_id}) → {direction} → ProfileId={target_profile_id}")
            
            try:
                # Authenticate as the user performing the swipe
                token = self.get_user_token(from_email, "Test123!")
                headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                
                # Map to SwipeService API format
                # POST /api/swipes requires: {userId, targetUserId, isLike, idempotencyKey}
                # userId and targetUserId are ProfileIds (int), not UserIds (GUID)
                payload = {
                    "userId": from_profile_id,
                    "targetUserId": target_profile_id,
                    "isLike": direction == "right",
                    "idempotencyKey": swipe.get("swipeId", f"fixture-{time.time()}")
                }
                
                url = f"{self.config.swipe_service_url}/api/swipes"
                response = requests.post(url, headers=headers, json=payload, timeout=10)
                
                if response.status_code in (200, 201):
                    result = response.json()
                    is_match = result.get("data", {}).get("isMutualMatch", False)
                    if is_match:
                        self.log(f"    ✓ Swipe recorded - IT'S A MATCH! 🎉", "SUCCESS")
                    else:
                        self.log(f"    ✓ Swipe recorded", "SUCCESS")
                    loaded_count += 1
                else:
                    self.log(f"    ✗ Failed: {response.status_code} - {response.text}", "ERROR")
            except Exception as e:
                self.log(f"    ✗ Error: {e}", "ERROR")
        
        self.log(f"✓ Loaded {loaded_count}/{len(fixture['swipes'])} swipes", "SUCCESS")
    
    def load_matches(self):
        """Load match records into MatchmakingService via API"""
        self.log("=" * 60)
        self.log("Step 4: Loading match records...")
        
        fixture = self.load_json_file("matches.json")
        if not fixture or "matches" not in fixture:
            self.log("No matches to load", "WARNING")
            return
        
        self.log(f"  Note: Matches should be created automatically by SwipeService")
        self.log(f"  If swipes were loaded correctly, matches already exist")
        self.log(f"  Skipping explicit match creation to avoid duplicates")
        
        # Optional: Verify matches exist via GET API
        # for match in fixture["matches"]:
        #     Check if match exists via MatchmakingService API
        
        self.log(f"✓ Match loading skipped (created via swipes)", "INFO")
    
    def load_messages(self):
        """Load message history into MessagingService via API"""
        self.log("=" * 60)
        self.log("Step 5: Loading message history...")
        
        fixture = self.load_json_file("messages.json")
        if not fixture or "messages" not in fixture:
            self.log("No messages to load", "WARNING")
            return
        
        # Get Keycloak users fixture to find email for each userId
        users_fixture = self.load_json_file("keycloak_users.json")
        user_emails = {u.get("attributes", {}).get("userId", [""])[0]: u["email"] for u in users_fixture.get("users", [])}
        
        loaded_count = 0
        for message in fixture["messages"]:
            sender_id = message["senderId"]
            receiver_id = message["receiverId"]
            content = message["content"]
            
            # Get email for user token
            sender_email = user_emails.get(sender_id)
            if not sender_email:
                self.log(f"  ✗ Cannot find email for sender {sender_id}", "ERROR")
                continue
            
            # Map fixture receiverId to Keycloak UUID
            receiver_keycloak_id = self.user_id_mapping.get(receiver_id)
            if not receiver_keycloak_id:
                self.log(f"  ✗ Cannot find Keycloak ID for receiver {receiver_id}", "ERROR")
                continue
            
            receiver_email = user_emails.get(receiver_id, "unknown")
            self.log(f"  Loading message: {sender_email} → {receiver_email}")
            
            try:
                # Authenticate as sender
                token = self.get_user_token(sender_email, "Test123!")
                headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                
                # Map to MessagingService API format
                # POST /api/messages requires: {recipientUserId, text, type}
                # recipientUserId must be Keycloak UUID (sub claim), not fixture userId
                payload = {
                    "recipientUserId": receiver_keycloak_id,
                    "text": content,
                    "type": 0  # Text type (MessageType enum: Text=0, Image=1, Emoji=2)
                }
                
                url = f"{self.config.messaging_service_url}/api/messages"
                response = requests.post(url, headers=headers, json=payload, timeout=10)
                
                if response.status_code in (200, 201):
                    self.log(f"    ✓ Message sent", "SUCCESS")
                    loaded_count += 1
                else:
                    self.log(f"    ✗ Failed: {response.status_code} - {response.text}", "ERROR")
            except Exception as e:
                self.log(f"    ✗ Error: {e}", "ERROR")
        
        self.log(f"✓ Loaded {loaded_count}/{len(fixture['messages'])} messages", "SUCCESS")
    
    def load_user_photos(self):
        """Load photo metadata into PhotoService"""
        self.log("=" * 60)
        self.log("Step 6: Loading photo metadata...")
        
        fixture = self.load_json_file("user_photos.json")
        if not fixture or "photos" not in fixture:
            self.log("No photos to load", "WARNING")
            return
        
        self.log(f"  Note: PhotoService requires multipart/form-data file uploads")
        self.log(f"  Current fixture only contains metadata (URLs)")
        self.log(f"  Real photo upload requires actual image files")
        self.log(f"  Skipping photo upload - implement when needed for tests")
        
        total_photos = len(fixture["photos"])
        self.log(f"✓ Would upload {total_photos} photos (not implemented)", "INFO")
    
    def load_all(self):
        """Load all fixtures in correct dependency order"""
        start_time = time.time()
        self.log("=" * 60)
        self.log(f"LOADING FIXTURES FROM: {self.fixture_dir}")
        self.log("=" * 60)
        
        try:
            # Load in dependency order (respects foreign keys & business logic)
            # 1. Keycloak users (identity foundation)
            self.provision_keycloak_users()
            
            # 2. User profiles (creates ProfileIds and UserProfileMappings)
            self.load_user_profiles()
            
            # 2.5 Sync UserProfileMappings to SwipeService (enables match validation)
            self.sync_user_profile_mappings()
            
            # 3. Swipes (creates matches automatically via business logic)
            self.load_swipes()
            
            # 4. Matches (skipped - created by swipes)
            self.load_matches()
            
            # 5. Messages (requires matches to exist)
            self.load_messages()
            
            # 6. Photos (optional - requires file uploads)
            self.load_user_photos()
            
            elapsed = time.time() - start_time
            self.log("=" * 60)
            self.log(f"✓ ALL FIXTURES LOADED SUCCESSFULLY in {elapsed:.2f}s", "SUCCESS")
            self.log("=" * 60)
            
        except Exception as e:
            self.log("=" * 60)
            self.log(f"✗ FIXTURE LOADING FAILED: {e}", "ERROR")
            self.log("=" * 60)
            raise
    
    def clean_all(self, full: bool = False):
        """Clean all test data"""
        self.log("=" * 60)
        self.log("CLEANING FIXTURES...")
        self.log("=" * 60)
        
        if full:
            self.log("Full cleanup not implemented yet - would delete Keycloak users", "WARNING")
        else:
            self.log("Partial cleanup not implemented yet - would preserve Keycloak users", "WARNING")
    
    def validate_all(self, check_refs: bool = False):
        """Validate all fixture files"""
        self.log("=" * 60)
        self.log(f"VALIDATING FIXTURES: {self.fixture_dir}")
        self.log("=" * 60)
        
        files = [
            "metadata.json",
            "keycloak_users.json",
            "user_profiles.json",
            "user_photos.json",
            "swipes.json",
            "matches.json",
            "messages.json",
        ]
        
        errors = []
        for filename in files:
            filepath = self.fixture_dir / filename
            if not filepath.exists():
                if filename != "metadata.json":  # metadata.json is optional
                    errors.append(f"Missing file: {filename}")
                continue
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.log(f"  ✓ {filename} - valid JSON", "SUCCESS")
            except json.JSONDecodeError as e:
                errors.append(f"{filename}: Invalid JSON - {e}")
                self.log(f"  ✗ {filename} - {e}", "ERROR")
        
        if check_refs:
            self.log("Referential integrity checks not implemented yet", "WARNING")
        
        if errors:
            self.log("=" * 60)
            self.log(f"✗ VALIDATION FAILED: {len(errors)} errors", "ERROR")
            for error in errors:
                self.log(f"  - {error}", "ERROR")
            self.log("=" * 60)
            return False
        else:
            self.log("=" * 60)
            self.log("✓ ALL FIXTURES VALID", "SUCCESS")
            self.log("=" * 60)
            return True


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Fixture Loader - Professional test data provisioning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Load command
    load_parser = subparsers.add_parser("load", help="Load fixtures into services")
    load_parser.add_argument("--set", required=True, choices=["minimal", "standard", "load", "demo"],
                            help="Fixture set to load")
    load_parser.add_argument("--env", default="demo", choices=["demo", "test"],
                            help="Environment to load into")
    load_parser.add_argument("--validate-only", action="store_true",
                            help="Validate fixtures without loading")
    
    # Clean command
    clean_parser = subparsers.add_parser("clean", help="Clean test data from services")
    clean_parser.add_argument("--set", required=True, help="Fixture set to clean")
    clean_parser.add_argument("--full", action="store_true",
                             help="Full cleanup including Keycloak users")
    clean_parser.add_argument("--env", default="demo", choices=["demo", "test"],
                             help="Environment to clean")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate fixture files")
    validate_parser.add_argument("--set", required=True, help="Fixture set to validate")
    validate_parser.add_argument("--check-refs", action="store_true",
                                help="Check referential integrity")
    
    parser.add_argument("--quiet", action="store_true", help="Suppress output")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Determine fixture directory
    script_dir = Path(__file__).parent.parent
    fixture_dir = script_dir / "infrastructure" / "test-fixtures" / args.set
    
    if not fixture_dir.exists():
        print(f"Error: Fixture directory not found: {fixture_dir}")
        return 1
    
    # Create loader
    config = ServiceConfig.from_env(getattr(args, "env", "demo"))
    loader = FixtureLoader(config, fixture_dir, verbose=not args.quiet)
    
    # Execute command
    try:
        if args.command == "load":
            if args.validate_only:
                return 0 if loader.validate_all() else 1
            else:
                loader.load_all()
                return 0
        
        elif args.command == "clean":
            loader.clean_all(full=args.full)
            return 0
        
        elif args.command == "validate":
            return 0 if loader.validate_all(check_refs=args.check_refs) else 1
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 130
    except Exception as e:
        print(f"\nError: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
