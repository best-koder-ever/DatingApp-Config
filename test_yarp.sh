#!/bin/bash

# Test auth-service
echo "Testing auth-service..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/auth/swagger/index.html)
if [ "$response" -eq 200 ]; then
  echo "auth-service is accessible through YARP."
else
  echo "Failed to access auth-service through YARP. HTTP status code: $response"
fi

# Test user-service
echo "Testing user-service..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/user/swagger/index.html)
if [ "$response" -eq 200 ]; then
  echo "user-service is accessible through YARP."
else
  echo "Failed to access user-service through YARP. HTTP status code: $response"
fi