#!/bin/bash

# Quick test script to see exactly what's happening with photo uploads

echo "🔍 DEBUGGING PHOTO UPLOAD ISSUE"
echo "=================================="

# Get fresh token
echo "🔐 Getting auth token..."
TOKEN=$(curl -s -X POST http://localhost:8081/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"erik.astrom@demo.com","password":"Demo123!"}' | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

echo "✅ Token obtained"

# Create test image
echo "📸 Creating test image..."
echo "test photo data" > test_upload.txt

echo ""
echo "=== TEST 1: PhotoService Upload (Grid System) ==="
echo "Endpoint: http://localhost:8085/api/Photos"
PHOTO_RESPONSE=$(curl -s -X POST http://localhost:8085/api/Photos \
  -H "Authorization: Bearer $TOKEN" \
  -F "photo=@test_upload.txt")

echo "Response: $PHOTO_RESPONSE"
echo ""

echo "=== TEST 2: Get Photos from PhotoService ==="
PHOTOS_LIST=$(curl -s -X GET http://localhost:8085/api/Photos/user/0 \
  -H "Authorization: Bearer $TOKEN")
echo "Photos: $PHOTOS_LIST"
echo ""

echo "=== TEST 3: UserService Profile ==="
echo "Endpoint: http://localhost:8082/api/UserProfiles/0"
PROFILE_RESPONSE=$(curl -s -X GET http://localhost:8082/api/UserProfiles/0 \
  -H "Authorization: Bearer $TOKEN")

echo "Profile: $PROFILE_RESPONSE" | head -5
echo ""

echo "🎯 DIAGNOSIS:"
if [[ "$PHOTO_RESPONSE" == *"success"* ]]; then
  echo "✅ PhotoService upload works"
else
  echo "❌ PhotoService upload failed"
fi

if [[ "$PHOTOS_LIST" == *"["* ]]; then
  echo "✅ PhotoService retrieval works"
else
  echo "❌ PhotoService retrieval failed (this is likely the issue!)"
fi

# Cleanup
rm -f test_upload.txt

echo ""
echo "💡 LIKELY ISSUE:"
echo "   - Profile picture upload → Updates UserService → Grid shows immediately"
echo "   - Grid photo upload → Uses PhotoService → Grid doesn't reload from PhotoService"
echo ""
echo "🔧 SOLUTION: Grid needs to reload from PhotoService after upload"
