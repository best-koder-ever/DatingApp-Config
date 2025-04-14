import requests
import random
import string

# Generate random fake data
def generate_fake_user():
    username = ''.join(random.choices(string.ascii_lowercase, k=8))
    email = f"{username}@example.com"
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    phone_number = f"+1234{random.randint(100000, 999999)}"
    return {
        "username": username,
        "email": email,
        "password": password,
        "phoneNumber": phone_number
    }

def generate_fake_profile():
    name = ''.join(random.choices(string.ascii_letters, k=10))
    bio = "A random bio for testing."
    profile_picture_url = f"https://example.com/images/{name}.jpg"
    preferences = "Hiking, Reading, Traveling"
    return {
        "name": name,
        "bio": bio,
        "profilePictureUrl": profile_picture_url,
        "preferences": preferences
    }

# Register a user in auth-service
def register_user(auth_service_url, user_data):
    register_endpoint = f"{auth_service_url}/api/Auth/register"
    response = requests.post(register_endpoint, json=user_data)
    response.raise_for_status()
    return response.json()

# Login to auth-service to get a token
def login_user(auth_service_url, user_data):
    login_endpoint = f"{auth_service_url}/api/Auth/login"
    login_payload = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    response = requests.post(login_endpoint, json=login_payload)
    response.raise_for_status()
    return response.json()["token"]

# Post to user-service with the token
def post_to_user_service(user_service_url, token, profile_data):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    post_endpoint = f"{user_service_url}/api/UserProfiles"
    response = requests.post(post_endpoint, json=profile_data, headers=headers)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    # Base URLs for services
    auth_service_url = "http://localhost:8081"
    user_service_url = "http://localhost:8082"

    # Step 1: Generate random user data
    user_data = generate_fake_user()
    print("Registering user:", user_data)

    # Step 2: Register the user in auth-service
    register_user(auth_service_url, user_data)

    # Step 3: Login to auth-service to get a token
    token = login_user(auth_service_url, user_data)
    print("Received token:", token)

    # Step 4: Generate random profile data
    profile_data = generate_fake_profile()
    print("Posting profile:", profile_data)

    # Step 5: Post to user-service with the token
    result = post_to_user_service(user_service_url, token, profile_data)
    print("Profile created:", result)