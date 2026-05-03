import os
import sys

# Ensure backend directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.auth import get_password_hash, verify_password

# 1. Test long password
try:
    long_pwd = "a" * 100
    print("Hashing long password...")
    h = get_password_hash(long_pwd)
    print("Hash generated:", h)
    
    print("Verifying long password...")
    is_valid = verify_password(long_pwd, h)
    print("Is valid:", is_valid)
    assert is_valid, "Password verification failed"
    
except Exception as e:
    print("Error:", e)

# 2. Test bcrypt module load error
try:
    import passlib.context
    ctx = passlib.context.CryptContext(schemes=["bcrypt"], deprecated="auto")
    print("CryptContext created successfully")
except Exception as e:
    print("CryptContext error:", e)
