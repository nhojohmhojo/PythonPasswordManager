from cryptography.fernet import Fernet
import os

# Load and generate key
def load_key():
    if not os.path.exists("secret.key"):
        key = Fernet.generate_key()
        with open("secret.key", "wb") as f:
            f.write(key)
    else:
        with open("secret.key", "rb") as f:
            key = f.read()
    return key

key = load_key()
fernet = Fernet(key)

# Encrypt and Decrypt
def encrypt_password(password):
    return fernet.encrypt(password.encode())

def decrypt_password(encrypted_password):
    return fernet.decrypt(encrypted_password).decode()