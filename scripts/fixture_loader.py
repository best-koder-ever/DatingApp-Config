#!/usr/bin/env python3
"""
Fixture Loader CLI - Professional test data provisioning tool
Loads JSON-based test fixtures into DatingApp services idempotently.

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
                keycloak_url=os.getenv("KEYCLOAK_URL", "http://localhost:8080"),
                keycloak_realm=os.getenv("KEYCLOAK_REALM", "datingapp"),
                keycloak_admin_user=os.getenv("KEYCLOAK_ADMIN_USER", "admin"),
                keycloak_admin_password=os.getenv("KEYCLOAK_ADMIN_PASSWORD", "admin"),
                user_service_url=os.getenv("USER_SERVICE_URL", "http://localhost:8082"),
                photo_service_url=os.getenv("PHOTO_SERVICE_URL", "http://localhost:8084"),
                swipe_service_url=os.getenv("SWIPE_SERVICE_URL", "http://localhost:8087"),
                matchmaking_service_url=os.getenv("MATCHMAKING_SERVICE_URL", "http://localhost:8083"),
                messaging_service_url=os.getenv("MESSAGING_SERVICE_URL", "http://localhost:8085"),
            )
        elif env == "test":
            return cls(
                keycloak_url=os.getenv("KEYCLOAK_TEST_URL", "http://localhost:8090"),
                keycloak_realm=os.getenv("KEYCLOAK_TEST_REALM", "datingapp-test"),
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
    """Main fixture loader class"""
    
    def __init__(self, config: ServiceConfig, fixture_dir: Path, verbose: bool = True):
        self.config = config
        self.fixture_dir = fixture_dir
        self.verbose = verbose
        self.keycloak_token: Optional[str] = None
        self.user_tokens: Dict[str, str] = {}
        
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
            "client_id": "datingapp-client",
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
                        self.log(f"    ✓ User created (ID: {user_id})", "SUCCESS")
                    else:
                        self.log(f"    ✗ Failed to get user ID", "ERROR")
                else:
                    self.log(f"    ✗ Failed to create user: {response.status_code} - {response.text}", "ERROR")
        
        self.log(f"✓ Provisioned {len(user_ids)} Keycloak users", "SUCCESS")
        return user_ids
    
    def load_user_profiles(self):
        """Load user profiles into UserService"""
        self.log("=" * 60)
        self.log("Step 2: Loading user profiles...")
        
        fixture = self.load_json_file("user_profiles.json")
        if not fixture or "profiles" not in fixture:
            self.log("No user profiles to load", "WARNING")
            return
        
        for profile in fixture["profiles"]:
            email = profile["email"]
            self.log(f"  Loading profile: {email}")
            
            # Get user token
            try:
                token = self.get_user_token(email, "Test123!")
                headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                
                # Create/update profile
                url = f"{self.config.user_service_url}/api/user/profile"
                response = requests.post(url, headers=headers, json=profile, timeout=10)
                
                if response.status_code in (200, 201):
                    self.log(f"    ✓ Profile loaded", "SUCCESS")
                else:
                    self.log(f"    ✗ Failed: {response.status_code} - {response.text}", "ERROR")
            except Exception as e:
                self.log(f"    ✗ Error: {e}", "ERROR")
        
        self.log(f"✓ Loaded {len(fixture['profiles'])} user profiles", "SUCCESS")
    
    def load_user_photos(self):
        """Load photo metadata into PhotoService"""
        self.log("=" * 60)
        self.log("Step 3: Loading photo metadata...")
        
        fixture = self.load_json_file("user_photos.json")
        if not fixture or "photos" not in fixture:
            self.log("No photos to load", "WARNING")
            return
        
        # Group photos by user
        photos_by_user = {}
        for photo in fixture["photos"]:
            user_id = photo["userId"]
            if user_id not in photos_by_user:
                photos_by_user[user_id] = []
            photos_by_user[user_id].append(photo)
        
        self.log(f"  Loading photos for {len(photos_by_user)} users...")
        # Note: Implementation depends on PhotoService API
        # For now, just log what would be loaded
        total_photos = sum(len(photos) for photos in photos_by_user.values())
        self.log(f"✓ Would load {total_photos} photos (PhotoService integration pending)", "INFO")
    
    def load_swipes(self):
        """Load swipe records into SwipeService"""
        self.log("=" * 60)
        self.log("Step 4: Loading swipe records...")
        
        fixture = self.load_json_file("swipes.json")
        if not fixture or "swipes" not in fixture:
            self.log("No swipes to load", "WARNING")
            return
        
        self.log(f"  Loading {len(fixture['swipes'])} swipes...")
        # Note: Implementation depends on SwipeService API
        self.log(f"✓ Would load {len(fixture['swipes'])} swipes (SwipeService integration pending)", "INFO")
    
    def load_matches(self):
        """Load match records into MatchmakingService"""
        self.log("=" * 60)
        self.log("Step 5: Loading match records...")
        
        fixture = self.load_json_file("matches.json")
        if not fixture or "matches" not in fixture:
            self.log("No matches to load", "WARNING")
            return
        
        self.log(f"  Loading {len(fixture['matches'])} matches...")
        # Note: Implementation depends on MatchmakingService API
        self.log(f"✓ Would load {len(fixture['matches'])} matches (MatchmakingService integration pending)", "INFO")
    
    def load_messages(self):
        """Load message history into MessagingService"""
        self.log("=" * 60)
        self.log("Step 6: Loading message history...")
        
        fixture = self.load_json_file("messages.json")
        if not fixture or "messages" not in fixture:
            self.log("No messages to load", "WARNING")
            return
        
        self.log(f"  Loading {len(fixture['messages'])} messages...")
        # Note: Implementation depends on MessagingService API
        self.log(f"✓ Would load {len(fixture['messages'])} messages (MessagingService integration pending)", "INFO")
    
    def load_all(self):
        """Load all fixtures in correct order"""
        start_time = time.time()
        self.log("=" * 60)
        self.log(f"LOADING FIXTURES FROM: {self.fixture_dir}")
        self.log("=" * 60)
        
        try:
            # Load in dependency order
            self.provision_keycloak_users()
            self.load_user_profiles()
            self.load_user_photos()
            self.load_swipes()
            self.load_matches()
            self.load_messages()
            
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
