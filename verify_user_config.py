#!/usr/bin/env python3
"""Verify the new user configuration loads correctly"""
import yaml
import sys

try:
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    print("✅ Configuration loaded successfully!")
    print("\n--- Users Configuration ---")
    users_list = config.get('users', [])
    
    if not users_list:
        print("❌ ERROR: No users found in configuration!")
        sys.exit(1)
    
    print(f"Found {len(users_list)} user(s):\n")
    
    # Build user lookup dictionary
    users_by_id = {user['telegram_id']: user for user in users_list}
    
    for user in users_list:
        print(f"  Telegram ID: {user.get('telegram_id')}")
        print(f"  Name: {user.get('name', 'N/A')}")
        print(f"  Description: {user.get('description', 'N/A')}")
        print()
    
    # Test auth function
    print("--- Testing Auth Function ---")
    def check_auth(user_id):
        """Check if user is authorized and return user data if authorized, None otherwise"""
        user_data = users_by_id.get(user_id)
        if not user_data:
            print(f"⚠️  Unauthorized access attempt from {user_id}")
            return None
        return user_data
    
    # Test with valid user
    test_id = users_list[0]['telegram_id']
    result = check_auth(test_id)
    if result:
        print(f"✅ Auth check passed for user {test_id}: {result.get('name')}")
    else:
        print(f"❌ Auth check failed for user {test_id}")
        sys.exit(1)
    
    # Test with invalid user
    invalid_id = 999999999
    result = check_auth(invalid_id)
    if not result:
        print(f"✅ Auth correctly rejected invalid user {invalid_id}")
    else:
        print(f"❌ Auth incorrectly accepted invalid user {invalid_id}")
        sys.exit(1)
    
    print("\n✅ All configuration tests passed!")
    
except FileNotFoundError:
    print("❌ ERROR: config.yaml not found!")
    sys.exit(1)
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
