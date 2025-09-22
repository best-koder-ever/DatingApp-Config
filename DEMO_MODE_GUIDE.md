# Demo Configuration for Dating App

## Overview
The dating app now includes a comprehensive demo mode that provides realistic test data without requiring actual user registration or complex setup.

## Demo Mode Features

### AuthService Demo Endpoints
- `POST /api/demo/register` - Always succeeds with any email/password
- `POST /api/demo/login` - Accepts any credentials and returns success
- `POST /api/demo/refresh` - Token refresh simulation
- `POST /api/demo/logout` - Logout simulation
- `POST /api/demo/forgot-password` - Password reset simulation
- `POST /api/demo/verify-email` - Email verification simulation
- `GET /api/demo/test-accounts` - Returns predefined test accounts

### UserService Demo Endpoints
- `GET /api/demo/profiles` - Returns realistic user profiles (default 10)
- `GET /api/demo/profiles/{id}` - Returns detailed profile for specific ID
- `POST /api/demo/search` - Performs search with filters on demo data
- `GET /api/demo/health` - Health check for demo endpoints

### MatchmakingService Demo Endpoints
- `GET /api/demo/matches/{userId}` - Returns potential matches for user
- `GET /api/demo/mutual-matches/{userId}` - Returns mutual matches
- `POST /api/demo/swipe` - Simulates swipe actions with 20% match rate
- `GET /api/demo/conversations/{userId}` - Returns user conversations
- `GET /api/demo/conversations/{id}/messages` - Returns conversation messages
- `POST /api/demo/conversations/{id}/messages` - Simulates sending messages

## Demo Data Characteristics

### User Profiles
- **Names**: Realistic Swedish/International names
- **Ages**: Range 22-36 years
- **Cities**: Swedish cities (Stockholm, Gothenburg, Malmö, etc.)
- **Photos**: High-quality placeholder images from Picsum
- **Bios**: Engaging, realistic profile descriptions
- **Interests**: Common dating app interests (Travel, Photography, etc.)
- **Verification**: 33% of profiles are verified
- **Online Status**: 75% of profiles show as online

### Matching System
- **Match Rate**: 20% chance of mutual match on swipe
- **Compatibility Scores**: Range 70-100%
- **Distance**: Simulated distances 1-50km
- **Common Interests**: 1-6 shared interests per match

### Conversations
- **Message Variety**: Realistic conversation starters and responses
- **Timing**: Messages spread across realistic timeframes
- **Read Status**: Proper read/unread message handling
- **Active Conversations**: 3-4 active conversations per user

## Using Demo Mode

### Environment Configuration
Set environment variable or config to enable demo mode:
```bash
export DEMO_MODE=true
```

### Flutter App Integration
The Flutter app should detect demo mode and route API calls to demo endpoints:

```dart
// Example configuration
class ApiConfig {
  static bool get isDemoMode => 
    const String.fromEnvironment('DEMO_MODE') == 'true';
  
  static String get baseUrl => isDemoMode 
    ? 'http://localhost:8080/api/demo'
    : 'http://localhost:8080/api';
}
```

### Testing Workflow
1. **Start Services**: Run all microservices with demo controllers
2. **Enable Demo Mode**: Set DEMO_MODE environment variable
3. **Run Demo Script**: Use the menu-driven demo system
4. **Verify UI**: Confirm all screens display data correctly
5. **Test Interactions**: Verify swipe, match, and messaging functionality

## Demo Test Accounts
Predefined accounts for consistent testing:
- **alice@demo.com** / password123 (Alice Johnson)
- **bob@demo.com** / password123 (Bob Smith)  
- **carol@demo.com** / password123 (Carol Williams)
- **demo@example.com** / demo123 (Demo User)
- **test@test.com** / test123 (Test User)

## Health Checks
Each service provides a demo health check endpoint:
- AuthService: `GET /api/demo/health`
- UserService: `GET /api/demo/health`
- MatchmakingService: `GET /api/demo/health`

## Benefits
1. **No Database Setup**: Works without complex database initialization
2. **Consistent Data**: Predictable, realistic test data
3. **Fast Testing**: Quick verification of UI and functionality
4. **Demo Ready**: Perfect for presentations and demos
5. **Development Speed**: Faster iteration during development
6. **CI/CD Friendly**: Easy to integrate into automated testing

## Implementation Notes
- Demo controllers return realistic but fake data
- All endpoints simulate real API behavior
- Error handling maintains consistency with production APIs
- Logging included for debugging and monitoring
- JWT tokens are simulated but structurally valid

## Next Steps
1. Update Flutter app to support demo mode routing
2. Add demo mode toggle in development settings
3. Integrate with existing menu-driven demo system
4. Add demo mode to CI/CD pipeline for automated testing
