import bcrypt
from cryptography.fernet import Fernet
import os

# === HASHING FUNCTIONS (for login passwords) ===

def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed.decode()

def check_password(plain_password: str, hashed_password) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
    except ValueError:
        return False

# === ENCRYPTION FUNCTIONS (for saved passwords) ===

KEY_DIR = "data/keys"

def load_key(user_id: str) -> bytes:
    os.makedirs(KEY_DIR, exist_ok=True)
    key_path = os.path.join(KEY_DIR, f"{user_id}.key")

    if not os.path.exists(key_path):
        key = Fernet.generate_key()
        with open(key_path, "wb") as f:
            f.write(key)
    else:
        with open(key_path, "rb") as f:
            key = f.read()
    return key

def get_fernet(user_id: str) -> Fernet:
    return Fernet(load_key(user_id))

def encrypt_password(password: str, user_id: str) -> str:
    fernet = get_fernet(user_id)
    return fernet.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password: str, user_id: str) -> str:
    fernet = get_fernet(user_id)
    return fernet.decrypt(encrypted_password.encode()).decode()

# === WINDOW FUNCTIONS ===

def center_window(window, width, height):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width - width) / 2)
    y = int((screen_height - height) / 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

# === OTHER ===
COLOR_PALETTE = {
    "Light": {
        "bg": "gray90",
        "fg": "#1e1e1e",
        "tree_bg": "#ffffff",
        "tree_fg": "#1e1e1e",
        "tree_field_bg": "#ffffff"
    },
    "Dark": {
        "bg": "#1e1e1e",
        "fg": "#ffffff",
        "tree_bg": "#1e1e1e",
        "tree_fg": "#ffffff",
        "tree_field_bg": "#1e1e1e"
    }
}