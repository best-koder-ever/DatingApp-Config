#!/usr/bin/env python3
"""
AI Helper: Backend State Verification

Strategy: Python script AI can run to verify backend state instantly
Benefits:
- AI can check database state without Flutter test context
- AI can verify fixtures loaded correctly before tests
- AI can debug backend issues independently
- Fast execution (100ms vs 5s for Flutter test)

Usage:
    python3 scripts/ai-verify-state.py                    # Quick check
    python3 scripts/ai-verify-state.py --verbose          # Detailed output
    python3 scripts/ai-verify-state.py --assert-minimal  # Fails if fixtures not loaded
"""

import sys
import json
import mysql.connector
import requests
from typing import Dict, Any

# Database connections (from docker-compose)
DATABASES = {
    'SwipeServiceDb': {'host': 'localhost', 'port': 3310, 'user': 'root', 'password': 'root_password'},
    'UserServiceDb': {'host': 'localhost', 'port': 3308, 'user': 'root', 'password': 'root_password'},
    'MessagingServiceDb': {'host': 'localhost', 'port': 3306, 'user': 'root', 'password': ''},  # Fixed: Correct DB name
    'PhotoDb': {'host': 'localhost', 'port': 3311, 'user': 'root', 'password': 'root_password'},
    'MatchmakingDb': {'host': 'localhost', 'port': 3309, 'user': 'root', 'password': 'root_password'},
}

def get_database_state(verbose=False) -> Dict[str, Any]:
    """Get current state of all databases"""
    state = {}
    
    try:
        # SwipeService
        conn = mysql.connector.connect(
            host=DATABASES['SwipeServiceDb']['host'],
            port=DATABASES['SwipeServiceDb']['port'],
            user=DATABASES['SwipeServiceDb']['user'],
            password=DATABASES['SwipeServiceDb']['password'],
            database='SwipeServiceDb'
        )
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM UserProfileMappings")
        state['user_mappings'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Swipes")
        state['swipes'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Matches WHERE IsActive = 1")
        state['matches'] = cursor.fetchone()[0]
        
        if verbose:
            cursor.execute("SELECT SwipeId, UserId, TargetUserId, IsLike FROM Swipes ORDER BY SwipeId DESC LIMIT 5")
            state['recent_swipes'] = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # UserService
        conn = mysql.connector.connect(
            host=DATABASES['UserServiceDb']['host'],
            port=DATABASES['UserServiceDb']['port'],
            user=DATABASES['UserServiceDb']['user'],
            password=DATABASES['UserServiceDb']['password'],
            database='UserServiceDb'
        )
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM UserProfiles")
        state['profiles'] = cursor.fetchone()[0]
        
        if verbose:
            cursor.execute("SELECT ProfileId, FirstName, Email FROM UserProfiles ORDER BY ProfileId LIMIT 5")
            state['recent_profiles'] = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # MessagingService
        conn = mysql.connector.connect(
            host=DATABASES['MessagingServiceDb']['host'],
            port=DATABASES['MessagingServiceDb']['port'],
            user=DATABASES['MessagingServiceDb']['user'],
            password=DATABASES['MessagingServiceDb']['password'],
            database='MessagingServiceDb'
        )
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM Messages")
        state['messages'] = cursor.fetchone()[0]
        
        if verbose:
            cursor.execute("SELECT MessageId, SenderId, ReceiverId, Content FROM Messages ORDER BY MessageId DESC LIMIT 5")
            state['recent_messages'] = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        state['error'] = str(e)
    
    return state

def verify_minimal_fixtures(state: Dict[str, Any]) -> bool:
    """Verify that minimal fixtures are loaded"""
    expected = {
        'user_mappings': 5,  # 5 fixture users
        'profiles': 5,       # 5 profiles
        'matches': 2,        # 2 known matches
    }
    
    all_good = True
    for key, min_value in expected.items():
        actual = state.get(key, 0)
        if actual < min_value:
            print(f"❌ {key}: expected >={min_value}, got {actual}")
            all_good = False
        else:
            print(f"✅ {key}: {actual} (expected >={min_value})")
    
    return all_good

def print_state(state: Dict[str, Any], verbose=False):
    """Print state in readable format"""
    print("\n" + "="*60)
    print("📊 Backend Database State")
    print("="*60)
    
    if 'error' in state:
        print(f"❌ Error: {state['error']}")
        return
    
    print(f"  User Mappings: {state.get('user_mappings', 0)}")
    print(f"  Profiles:      {state.get('profiles', 0)}")
    print(f"  Swipes:        {state.get('swipes', 0)}")
    print(f"  Matches:       {state.get('matches', 0)}")
    print(f"  Messages:      {state.get('messages', 0)}")
    
    if verbose:
        print("\n" + "-"*60)
        print("Recent Swipes:")
        for swipe in state.get('recent_swipes', []):
            print(f"  SwipeId={swipe[0]}, User={swipe[1]}, Target={swipe[2]}, Like={swipe[3]}")
        
        print("\nRecent Profiles:")
        for profile in state.get('recent_profiles', []):
            print(f"  ProfileId={profile[0]}, Name={profile[1]}, Email={profile[2]}")
        
        print("\nRecent Messages:")
        for msg in state.get('recent_messages', []):
            print(f"  MessageId={msg[0]}, Sender={msg[1]}, Receiver={msg[2]}, Content={msg[3][:50]}...")
    
    print("="*60 + "\n")

if __name__ == '__main__':
    verbose = '--verbose' in sys.argv
    assert_minimal = '--assert-minimal' in sys.argv
    
    state = get_database_state(verbose)
    print_state(state, verbose)
    
    if assert_minimal:
        if not verify_minimal_fixtures(state):
            print("\n❌ Minimal fixtures not loaded!")
            print("Run: make seed-minimal")
            sys.exit(1)
        else:
            print("\n✅ Minimal fixtures verified")
            sys.exit(0)
