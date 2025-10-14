#!/bin/bash

echo "🎯 PHOTO UPLOAD FIX - STEP-BY-STEP TEST GUIDE"
echo "=============================================="
echo ""
echo "✅ FIXED: Photo grid now loads from PhotoService!"
echo "✅ ADDED: Refresh button in profile to reload grid photos"
echo "✅ AUTOMATIC: Grid refreshes when profile loads"
echo ""
echo "🔧 THE SOLUTION:"
echo "   - Profile pictures (working): userApi.uploadPhoto() → Shows immediately"
echo "   - Grid photos (now fixed): PhotoService uploads → Shows with refresh"
echo ""
echo "📱 FOLLOW THESE STEPS TO TEST:"
echo ""
echo "1️⃣  LOG INTO THE APP"
echo "   - Use: erik.astrom@demo.com / Demo123!"
echo "   - Navigate to Profile"
echo ""
echo "2️⃣  UPLOAD TO PHOTO GRID (Using PhotoService)"
echo "   - Tap 'Photos' tab or photo grid area"
echo "   - Go to Photo Upload Screen"
echo "   - Upload a photo - should work and show immediately"
echo ""
echo "3️⃣  GO BACK TO PROFILE"
echo "   - Navigate back to main profile"
echo "   - Photos should automatically load from PhotoService!"
echo "   - If not showing, tap the 🔄 refresh button next to 'Add at least 2 photos'"
echo ""
echo "4️⃣  TEST REFRESH BUTTON"
echo "   - The refresh button manually loads photos from PhotoService"
echo "   - Should show any photos you uploaded via the grid system"
echo ""
echo "🎯 EXPECTED RESULT:"
echo "   ✅ Photos uploaded via grid now appear in profile"
echo "   ✅ Refresh button works to reload grid photos"
echo "   ✅ Profile photos still work as before"
echo ""
echo "🔍 IF ISSUES PERSIST:"
echo "   - Check if PhotoService has photos:"

# Test PhotoService directly
echo ""
echo "🧪 Testing PhotoService directly..."
TOKEN=$(curl -s -X POST http://localhost:8081/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"erik.astrom@demo.com","password":"Demo123!"}' | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

echo "📸 Current photos in PhotoService:"
curl -s -X GET http://localhost:8085/api/Photos/user/1 \
  -H "Authorization: Bearer $TOKEN" | \
  python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if isinstance(data, dict) and 'photos' in data:
        photos = data['photos']
        print(f'✅ Found {len(photos)} photos in PhotoService')
        for i, photo in enumerate(photos):
            print(f'   {i+1}. {photo.get(\"originalFileName\", \"Unknown\")} - {photo.get(\"urls\", {}).get(\"medium\", \"No URL\")}')
    elif isinstance(data, list):
        print(f'✅ Found {len(data)} photos in PhotoService')
        for i, photo in enumerate(data):
            print(f'   {i+1}. {photo.get(\"originalFileName\", \"Unknown\")}')
    else:
        print('❌ No photos found or unexpected format')
        print(f'Response: {data}')
except Exception as e:
    print(f'❌ Error parsing PhotoService response: {e}')
    print('Raw response:', sys.stdin.read())
"

echo ""
echo "📱 NOW TEST IN THE APP:"
echo "   1. Go to Profile in the Flutter app"
echo "   2. Look for the refresh button (🔄) next to the photo instructions"
echo "   3. Tap it to load photos from PhotoService"
echo "   4. Your uploaded photos should appear!"
echo ""
echo "🎉 If this works, the fix is successful!"
