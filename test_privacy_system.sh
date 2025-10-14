#!/bin/bash
echo "🔐 Privacy System Testing Script"
echo "================================"

# Set your auth token here (get from login)
TOKEN="YOUR_TOKEN_HERE"

echo "Test 1: Upload photo with privacy settings"
curl -X POST http://localhost:8085/api/Photos/privacy \
  -H "Authorization: Bearer $TOKEN" \
  -F "photo=@test_upload.jpg" \
  -F "privacyLevel=Private" \
  -F "blurIntensity=0.8" \
  -F "description=Private photo test"

echo -e "\nTest 2: Update privacy level"
curl -X PUT http://localhost:8085/api/Photos/2/privacy \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"privacyLevel":"MatchOnly","requiresMatch":true}'

echo -e "\nTest 3: Access blurred version"
curl -I http://localhost:8085/api/Photos/2/blurred \
  -H "Authorization: Bearer $TOKEN"

echo -e "\nTest 4: Test access control"
curl http://localhost:8085/api/Photos/2/image/privacy \
  -H "Authorization: Bearer $TOKEN"

echo -e "\nPrivacy testing complete!"
