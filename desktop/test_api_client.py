#!/usr/bin/env python3
"""
API Client test script - no GUI required
Tests backend connectivity without PyQt6
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from desktop.src.api.client import APIClient
from desktop.src.models.data_models import User

def test_api_connection():
    """Test API connectivity"""
    print("🔍 Testing API connection...")
    
    client = APIClient()
    
    try:
        # Test health check
        print("\n1️⃣  Checking backend health...")
        result = client.health_check()
        print(f"   Result: {result}")
        print("   ✅ Backend is responding")
        return True
            
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False
    
    return True

def test_register():
    """Test user registration"""
    print("\n2️⃣  Testing user registration...")
    
    client = APIClient()
    
    try:
        response = client.register(
            email="testuser@example.com",
            username="testuser123",
            password="TestPass123!",
            full_name="Test User"
        )
        print(f"   ✅ Registration successful")
        print(f"   Token: {response.get('token', 'N/A')[:20]}...")
        return response.get('token')
    except Exception as e:
        print(f"   ❌ Registration failed: {e}")
        return None

def test_login(email="testuser@example.com", password="TestPass123!"):
    """Test user login"""
    print("\n3️⃣  Testing user login...")
    
    client = APIClient()
    
    try:
        response = client.login(email, password)
        token = response.get('token')
        print(f"   ✅ Login successful")
        print(f"   Token: {token[:20]}...")
        return token
    except Exception as e:
        print(f"   ❌ Login failed: {e}")
        return None

def test_get_current_user(token):
    """Test getting current user info"""
    print("\n4️⃣  Testing get current user...")
    
    client = APIClient(token=token)
    
    try:
        user_data = client.get_current_user()
        print(f"   ✅ Retrieved user: {user_data.get('username')}")
        return True
    except Exception as e:
        print(f"   ❌ Failed to get user: {e}")
        return False

def main():
    print("=" * 50)
    print("Portföy Yönetim Sistemi - API Test")
    print("=" * 50)
    
    # Test connection
    if not test_api_connection():
        print("\n❌ Cannot connect to backend. Is it running? (uvicorn app.main:app --port 8000)")
        return 1
    
    # Try to register
    token = test_register()
    
    if not token:
        # Try to login with existing user
        print("\n   User might already exist, trying login...")
        token = test_login()
    
    if token:
        # Test authenticated endpoints
        test_get_current_user(token)
    
    print("\n" + "=" * 50)
    print("✅ API tests completed!")
    print("=" * 50)
    return 0

if __name__ == '__main__':
    sys.exit(main())
