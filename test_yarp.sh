#!/bin/bash

# Test AuthService
echo "Testing AuthService..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/auth/swagger/index.html)
if [ "$response" -eq 200 ]; then
  echo "AuthService is accessible through YARP."
else
  echo "Failed to access AuthService through YARP. HTTP status code: $response"
fi

# Test UserService
echo "Testing UserService..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/user/swagger/index.html)
if [ "$response" -eq 200 ]; then
  echo "UserService is accessible through YARP."
else
  echo "Failed to access UserService through YARP. HTTP status code: $response"
fi