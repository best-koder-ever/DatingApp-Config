#!/usr/bin/env python3
"""
Clean up test photos for user 2122989523 to allow new uploads during testing.
This helps with the 6-photo-per-user limit during development.
"""

import requests
import os
import json

def get_auth_token():
    """Get auth token for test user"""
    auth_url = "http://localhost:8081/api/auth/login"
    
    # Demo user credentials
    login_data = {
        "email": "demo@example.com",
        "password": "Demo123!"
    }
    
    try:
        response = requests.post(auth_url, json=login_data)
        if response.status_code == 200:
            token = response.json().get('token')
            print(f"✅ Got auth token: {token[:20]}...")
            return token
        else:
            print(f"❌ Auth failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Auth error: {e}")
        return None

def get_user_photos(token):
    """Get all photos for the test user"""
    photos_url = "http://localhost:8085/api/photos/user/2122989523"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(photos_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            photos = data.get('photos', [])
            print(f"📸 Found {len(photos)} photos for user")
            return photos
        elif response.status_code == 404:
            print("📸 No photos found for user")
            return []
        else:
            print(f"❌ Failed to get photos: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error getting photos: {e}")
        return []

def delete_photo(token, photo_id):
    """Delete a specific photo"""
    delete_url = f"http://localhost:8085/api/photos/{photo_id}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.delete(delete_url, headers=headers)
        if response.status_code == 200:
            print(f"✅ Deleted photo {photo_id}")
            return True
        else:
            print(f"❌ Failed to delete photo {photo_id}: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error deleting photo {photo_id}: {e}")
        return False

def main():
    print("🧹 Cleaning up test photos...")
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("❌ Cannot proceed without auth token")
        return
    
    # Get user photos
    photos = get_user_photos(token)
    if not photos:
        print("✅ No photos to clean up")
        return
    
    # Delete all photos
    deleted_count = 0
    for photo in photos:
        photo_id = photo.get('id')
        if photo_id and delete_photo(token, photo_id):
            deleted_count += 1
    
    print(f"🧹 Cleanup complete! Deleted {deleted_count}/{len(photos)} photos")
    print("✅ Test user ready for new photo uploads")

if __name__ == "__main__":
    main()
