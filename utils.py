import bcrypt
from cryptography.fernet import Fernet
import os

# === HASHING FUNCTIONS (for login passwords) ===

def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed.decode()

def check_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
    except ValueError:
        return False

# === ENCRYPTION FUNCTIONS (for saved passwords) ===

KEY_DIR = "data"
KEY_PATH = os.path.join(KEY_DIR, "secret.key")

def load_key():
    os.makedirs(KEY_DIR, exist_ok=True)
    if not os.path.exists(KEY_PATH):
        key = Fernet.generate_key()
        with open(KEY_PATH, "wb") as f:
            f.write(key)
    else:
        with open(KEY_PATH, "rb") as f:
            key = f.read()
    return key

# Initialize Fernet
fernet = Fernet(load_key())

def encrypt_password(password: str) -> str:
    return fernet.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password: str) -> str:
    return fernet.decrypt(encrypted_password.encode()).decode()
