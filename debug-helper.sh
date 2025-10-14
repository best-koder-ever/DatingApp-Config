#!/bin/bash
echo "🐛 Dating App Debug Helper"
echo "=========================="

# Function to test photo upload with full debugging
test_photo_upload() {
    echo "📸 Testing photo upload with FULL debugging..."
    
    # Get auth token
    echo "1. Getting auth token..."
    TOKEN=$(curl -s -X POST http://localhost:8081/api/Auth/login \
      -H "Content-Type: application/json" \
      -d '{"email":"erik.astrom@demo.com","password":"Demo123!"}' \
      | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])" 2>/dev/null)
    
    if [ -z "$TOKEN" ]; then
        echo "❌ Failed to get auth token"
        return 1
    fi
    
    echo "✅ Token obtained: ${TOKEN:0:30}..."
    
    # Upload photo with verbose output
    echo -e "\n2. Uploading photo..."
    RESPONSE=$(curl -s -X POST http://localhost:8085/api/Photos \
      -H "Authorization: Bearer $TOKEN" \
      -F "photo=@test_upload.jpg" \
      -F "description=Debug test upload")
    
    echo "📋 Upload response:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
    
    # Extract photo ID if successful
    PHOTO_ID=$(echo "$RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('photo', {}).get('id', ''))
except:
    pass
" 2>/dev/null)
    
    if [ ! -z "$PHOTO_ID" ]; then
        echo -e "\n3. Photo uploaded successfully! ID: $PHOTO_ID"
        
        # Test getting the photo
        echo -e "\n4. Testing photo retrieval..."
        curl -s http://localhost:8085/api/Photos/$PHOTO_ID \
          -H "Authorization: Bearer $TOKEN" \
          | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f'Photo ID: {data.get(\"id\")}')
    print(f'File: {data.get(\"originalFileName\")}')
    print(f'Size: {data.get(\"fileSizeFormatted\")}')
    print(f'Privacy: {data.get(\"privacyLevel\", \"Not set\")}')
    print(f'Created: {data.get(\"createdAt\")}')
    urls = data.get('urls', {})
    for size, url in urls.items():
        print(f'{size.title()} URL: {url}')
except Exception as e:
    print(f'Error parsing response: {e}')
"
    else
        echo "❌ Photo upload failed"
    fi
}

# Function to show all photos
show_all_photos() {
    echo "📂 All photos in database..."
    
    TOKEN=$(curl -s -X POST http://localhost:8081/api/Auth/login \
      -H "Content-Type: application/json" \
      -d '{"email":"erik.astrom@demo.com","password":"Demo123!"}' \
      | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])" 2>/dev/null)
    
    curl -s http://localhost:8085/api/Photos \
      -H "Authorization: Bearer $TOKEN" \
      | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    photos = data.get('photos', [])
    print(f'Found {len(photos)} photos:')
    for i, photo in enumerate(photos, 1):
        print(f'{i}. ID: {photo.get(\"id\")}, File: {photo.get(\"originalFileName\")}, Privacy: {photo.get(\"privacyLevel\", \"Unknown\")}')
except Exception as e:
    print(f'Error: {e}')
"
}

# Function to test privacy settings
test_privacy() {
    echo "🔒 Testing privacy settings..."
    read -p "Enter photo ID to test: " PHOTO_ID
    
    if [ -z "$PHOTO_ID" ]; then
        echo "❌ No photo ID provided"
        return 1
    fi
    
    TOKEN=$(curl -s -X POST http://localhost:8081/api/Auth/login \
      -H "Content-Type: application/json" \
      -d '{"email":"erik.astrom@demo.com","password":"Demo123!"}' \
      | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])" 2>/dev/null)
    
    echo "Setting photo to PRIVATE..."
    curl -s -X PUT http://localhost:8085/api/Photos/$PHOTO_ID/privacy \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"privacyLevel":"Private","blurIntensity":0.8}' \
      | python3 -m json.tool
}

# Menu
echo "Choose an option:"
echo "1. Test photo upload (with full debugging)"
echo "2. Show all photos"
echo "3. Test privacy settings"
echo "4. Watch logs in real-time"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1) test_photo_upload ;;
    2) show_all_photos ;;
    3) test_privacy ;;
    4) 
        echo "Starting log monitoring..."
        tail -f logs/photo-service.log
        ;;
    *) echo "Invalid choice" ;;
esac
