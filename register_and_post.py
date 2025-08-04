import requests
import random
import string
import sys

# Generate random fake data
def generate_fake_user():
    first_name = ''.join(random.choices(string.ascii_lowercase, k=6)).capitalize()
    last_name = ''.join(random.choices(string.ascii_lowercase, k=8)).capitalize()
    username = f"{first_name.lower()}{last_name.lower()}"
    email = f"{username}@example.com"
    # Password must have at least one non-alphanumeric and one digit
    password = (
        ''.join(random.choices(string.ascii_letters, k=6)) + str(random.randint(0,9)) + '!'
    )  # e.g. abcdef1!
    phone_number = f"+1234{random.randint(100000, 999999)}"
    return {
        "firstName": first_name,
        "lastName": last_name,
        "email": email,
        "password": password,
        "phoneNumber": phone_number
    }

def generate_fake_profile():
    first_name = ''.join(random.choices(string.ascii_letters, k=8)).capitalize()
    last_name = ''.join(random.choices(string.ascii_letters, k=10)).capitalize()
    age = random.randint(18, 55)
    birth_year = 2024 - age
    date_of_birth = f"{birth_year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
    bio = f"A random bio for testing. Age {age}, loves adventure and good conversation."
    occupation = random.choice(["Software Engineer", "Teacher", "Doctor", "Artist", "Chef", "Designer"])
    city = random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia"])
    interests = random.sample(["hiking", "reading", "traveling", "cooking", "music", "sports", "art", "technology"], 3)
    
    return {
        "firstName": first_name,
        "lastName": last_name,
        "dateOfBirth": date_of_birth,
        "bio": bio,
        "occupation": occupation,
        "city": city,
        "interests": interests,
        "height": random.randint(150, 200),
        "education": random.choice(["High School", "Bachelor's", "Master's", "PhD"]),
        "latitude": round(random.uniform(25.0, 49.0), 6),  # US latitude range
        "longitude": round(random.uniform(-125.0, -66.0), 6)  # US longitude range
    }

def generate_invalid_profile():
    # Missing fields or malformed data
    profiles = [
        {"bio": "No required fields"},
        {"firstName": "", "lastName": "Empty first name", "dateOfBirth": "1990-01-01"},
        {"firstName": None, "lastName": "Smith", "dateOfBirth": "1990-01-01", "bio": "None firstName"},
        {"firstName": "John", "lastName": "Doe", "dateOfBirth": None, "bio": "None dateOfBirth"},
        {"firstName": "John", "lastName": "Doe", "dateOfBirth": "invalid-date", "bio": "Invalid date"},
        {"firstName": "John", "lastName": "Doe", "dateOfBirth": "1990-01-01", "height": "not-a-number"},
    ]
    return random.choice(profiles)

# Register a user in auth-service
def register_user(auth_service_url, user_data):
    register_endpoint = f"{auth_service_url}/api/auth/register"
    response = requests.post(register_endpoint, json=user_data)
    if response.status_code == 409:  # User already exists
        print(f"User {user_data['email']} already exists, skipping registration")
        return {"message": "User already exists"}
    response.raise_for_status()
    return response.json()

# Login to auth-service to get a token
def login_user(auth_service_url, user_data):
    login_endpoint = f"{auth_service_url}/api/auth/login"
    login_payload = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    response = requests.post(login_endpoint, json=login_payload)
    response.raise_for_status()
    result = response.json()
    return result.get("token") or result.get("accessToken")

# Post to user-service with the token
def post_to_user_service(user_service_url, token, profile_data):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    post_endpoint = f"{user_service_url}/api/userprofiles"
    response = requests.post(post_endpoint, json=profile_data, headers=headers)
    if response.status_code == 409:  # Profile already exists
        print(f"Profile already exists for this user, trying to get existing profile")
        get_response = requests.get(f"{user_service_url}/api/userprofiles/me", headers=headers)
        if get_response.status_code == 200:
            return get_response.json()
    response.raise_for_status()
    return response.json()

def post_swipe(swipe_service_url, target_user_id, is_like, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "targetUserId": target_user_id,
        "isLike": is_like
    }
    response = requests.post(f"{swipe_service_url}/api/swipes/swipe", json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

# Fetch all user profiles (simulate what swipe screen would show)
def fetch_all_profiles(user_service_url, token):
    headers = {"Authorization": f"Bearer {token}"}
    print(f"Fetching profiles with headers: {headers}")
    response = requests.get(f"{user_service_url}/api/userprofiles/search?page=1&pageSize=50", headers=headers)
    response.raise_for_status()
    result = response.json()
    return result.get('results', result)  # Handle both paginated and direct results

if __name__ == "__main__":
    # Base URLs for services
    auth_service_url = "http://localhost:8081"
    user_service_url = "http://localhost:8082"
    swipe_service_url = "http://localhost:8084"
    matchmaking_service_url = "http://localhost:8083"  # Fixed matchmaking service port

    # Allow user to specify number of users to create
    num_users = 10
    if len(sys.argv) > 1:
        try:
            num_users = int(sys.argv[1])
        except ValueError:
            print("Invalid number of users, defaulting to 10.")

    created_profiles = []
    for i in range(num_users):
        print(f"\n=== Creating user/profile {i+1} of {num_users} ===")
        # Step 1: Generate random user data
        user_data = generate_fake_user()
        print("Registering user:", user_data)

        # Step 2: Register the user in auth-service
        try:
            register_user(auth_service_url, user_data)
        except Exception as e:
            print(f"Registration failed: {e}")
            continue

        # Step 3: Login to auth-service to get a token
        try:
            token = login_user(auth_service_url, user_data)
            print("Received token:", token)
        except Exception as e:
            print(f"Login failed: {e}")
            continue

        # Step 4: Generate random profile data
        profile_data = generate_fake_profile()
        print("Posting profile:", profile_data)

        # Step 5: Post to user-service with the token
        try:
            result = post_to_user_service(user_service_url, token, profile_data)
            print("Profile created:", result)
            created_profiles.append({"user": user_data, "profile": result})
        except Exception as e:
            print(f"Profile post failed: {e}")
            continue

    print(f"\nCreated {len(created_profiles)} user profiles out of {num_users} attempts.")

    # Test 'no more profiles' scenario
    print("\n=== Testing 'no more profiles' scenario ===")
    # Register a new user and create their profile
    test_user = generate_fake_user()
    register_user(auth_service_url, test_user)
    test_token = login_user(auth_service_url, test_user)
    test_profile = generate_fake_profile()
    test_profile_result = post_to_user_service(user_service_url, test_token, test_profile)
    test_user_id = test_profile_result.get("id") or test_profile_result.get("userId")

    print(f"Test user token: {test_token}")
    # Fetch all profiles as the new user
    all_profiles = fetch_all_profiles(user_service_url, test_token)
    # Exclude own profile by id
    all_profiles = [p for p in all_profiles if (p.get("id") or p.get("userId")) != test_user_id]
    print(f"User sees {len(all_profiles)} profiles to swipe on.")

    # Swipe on all profiles as the test user
    for p in all_profiles:
        target_user_id = p.get("id") or p.get("userId")
        if not target_user_id:
            continue
        try:
            post_swipe(swipe_service_url, target_user_id=target_user_id, is_like=True, token=test_token)
        except Exception as e:
            print(f"Swipe failed for target {target_user_id}: {e}")

    # Try to fetch profiles again
    remaining_profiles = fetch_all_profiles(user_service_url, test_token)
    remaining_profiles = [p for p in remaining_profiles if (p.get("id") or p.get("userId")) != test_user_id]
    print(f"After swiping, user sees {len(remaining_profiles)} profiles.")
    if not remaining_profiles:
        print("'No more profiles' scenario works as expected!")
    else:
        print("There are still profiles left after swiping all. Check filtering logic.")

    # Inject some invalid profiles
    print("\n=== Creating invalid/malformed profiles for robustness testing ===")
    for _ in range(3):
        user_data = generate_fake_user()
        try:
            register_user(auth_service_url, user_data)
            token = login_user(auth_service_url, user_data)
            invalid_profile = generate_invalid_profile()
            post_to_user_service(user_service_url, token, invalid_profile)
            print("Posted invalid profile:", invalid_profile)
        except Exception as e:
            print(f"Failed to post invalid profile: {e}")

    # Verify user never sees their own profile
    print("\n=== Verifying user never sees their own profile ===")
    for i, entry in enumerate(created_profiles):
        user = entry["user"]
        token = login_user(auth_service_url, user)
        profiles = fetch_all_profiles(user_service_url, token)
        own_id = entry["profile"].get("id") or entry["profile"].get("userId")
        for p in profiles:
            pid = p.get("id") or p.get("userId")
            if pid == own_id:
                print(f"User {user['firstName']} sees their own profile! BUG.")
            else:
                print(f"User {user['firstName']} does not see their own profile. OK.")

    # Mutual match scenario
    print("\n=== Testing mutual match scenario ===")
    if len(created_profiles) >= 2:
        user1 = created_profiles[0]["user"]
        user2 = created_profiles[1]["user"]
        token1 = login_user(auth_service_url, user1)
        token2 = login_user(auth_service_url, user2)
        # Get user IDs (assume profile has 'id' or 'userId')
        profile1 = created_profiles[0]["profile"]
        profile2 = created_profiles[1]["profile"]
        id1 = profile1.get("id") or profile1.get("userId")
        id2 = profile2.get("id") or profile2.get("userId")
        if id1 and id2:
            try:
                post_swipe(swipe_service_url, target_user_id=id2, is_like=True, token=token1)
                post_swipe(swipe_service_url, target_user_id=id1, is_like=True, token=token2)
                # Check for mutual match
                headers = {"Authorization": f"Bearer {token1}"}
                resp = requests.get(f"{swipe_service_url}/api/swipes/match/{id1}/{id2}", headers=headers)
                if resp.ok and resp.json().get("isMutualMatch"):
                    print(f"Mutual match detected between {user1['firstName']} and {user2['firstName']}! OK.")
                else:
                    print(f"No mutual match detected between {user1['firstName']} and {user2['firstName']}. BUG.")
            except Exception as e:
                print(f"Mutual match test failed: {e}")
        else:
            print("Could not determine user IDs for mutual match test.")
    else:
        print("Not enough users for mutual match test.")