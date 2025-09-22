#!/bin/bash

# Simple HTTP server to mock photo-service for testing
echo "Starting mock photo-service on port 8084..."

# Create responses directory if it doesn't exist
mkdir -p /tmp/mock-photo-service

# Create health endpoint response
cat > /tmp/mock-photo-service/health.json << 'EOF'
{
  "status": "healthy",
  "service": "photo-service",
  "timestamp": "2025-09-19T12:00:00Z"
}
EOF

# Create photos endpoint response
cat > /tmp/mock-photo-service/photos.json << 'EOF'
{
  "photos": [],
  "totalCount": 0,
  "hasMore": false
}
EOF

# Start Python HTTP server with custom routes
python3 -c "
import http.server
import socketserver
import json
import os
from urllib.parse import urlparse, parse_qs

class MockPhotoServiceHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            with open('/tmp/mock-photo-service/health.json', 'r') as f:
                self.wfile.write(f.read().encode())
                
        elif parsed_path.path.startswith('/api/photos'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            with open('/tmp/mock-photo-service/photos.json', 'r') as f:
                self.wfile.write(f.read().encode())
        else:
            self.send_response(404)
            self.end_headers()
            
    def do_POST(self):
        # Handle photo upload
        self.send_response(201)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            'id': 1,
            'fileName': 'uploaded_photo.jpg',
            'success': True,
            'message': 'Photo uploaded successfully (mock)'
        }
        self.wfile.write(json.dumps(response).encode())
        
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

PORT = 8084
with socketserver.TCPServer(('', PORT), MockPhotoServiceHandler) as httpd:
    print(f'Mock PhotoService serving at http://localhost:{PORT}')
    print('Health check: http://localhost:8084/health')
    print('Photos API: http://localhost:8084/api/photos')
    httpd.serve_forever()
"
