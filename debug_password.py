#!/usr/bin/env python3
"""Debug password length issue"""

# Passwordlar test et
passwords = [
    'TestPass123!',
    'test123456',
    'burak@test.com:test123456',
]

print("=" * 50)
print("Password Length Test")
print("=" * 50)

for pwd in passwords:
    bytes_len = len(pwd.encode('utf-8'))
    print(f"\nPassword: {pwd}")
    print(f"  Chars: {len(pwd)}")
    print(f"  Bytes: {bytes_len}")
    print(f"  OK for bcrypt: {bytes_len <= 72}")

print("\n" + "=" * 50)

# Hash test
print("Hash Test")
print("=" * 50)

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

test_password = "TestPass123!"
print(f"\nTest password: {test_password}")

try:
    # Direct hash - should fail with >72 bytes
    h1 = pwd_context.hash(test_password)
    print(f"✓ Hash successful: {h1[:20]}...")
except Exception as e:
    print(f"✗ Hash failed: {e}")

try:
    # Truncated hash - should work
    h2 = pwd_context.hash(test_password[:72])
    print(f"✓ Truncated hash successful: {h2[:20]}...")
except Exception as e:
    print(f"✗ Truncated hash failed: {e}")
