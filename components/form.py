"""
Description: form.py - Custom Component Class Form.
"""
from sqlalchemy.exc import SQLAlchemyError
from models import Passwords, Session as DBSession
from tkinter import messagebox
from tkinter import END, ttk
import customtkinter as ctk
from cryptography.fernet import Fernet
import os

# Define a secure path for secret key
KEY_DIR = "data"
KEY_PATH = os.path.join(KEY_DIR, "secret.key")

# Load or generate the secret key
def load_key():
    # Make sure the data directory exists
    os.makedirs(KEY_DIR, exist_ok=True)

    if not os.path.exists(KEY_PATH):
        key = Fernet.generate_key()
        with open(KEY_PATH, "wb") as f:
            f.write(key)
    else:
        with open(KEY_PATH, "rb") as f:
            key = f.read()
    return key

# Initialize Fernet with the key
key = load_key()
fernet = Fernet(key)

# Encrypt the password and return as UTF-8 string
def encrypt_password(password: str) -> str:
    encrypted = fernet.encrypt(password.encode())
    return encrypted.decode()  # Convert bytes to string for storage

# Decrypt the password from UTF-8 string
def decrypt_password(encrypted_password: str) -> str:
    decrypted = fernet.decrypt(encrypted_password.encode())
    return decrypted.decode()

# Custom Component Class CreatePassword
class Form(ctk.CTkFrame):
    def __init__(self, parent, password_table):
        super().__init__(parent)
        self.password_table = password_table
        self.password_table.bind("<Button-1>", self.handle_toggle_click)
        self.password_visibility = {}

        # Grid Layout
        self.rowconfigure(0, weight=1)
        self.columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        # Style
        self.style = ttk.Style()
        self.style.configure("TButton", foreground="teal")

        # Widgets
        self.website_label = ctk.CTkLabel(self, text="Website")
        self.username_label = ctk.CTkLabel(self, text="Username")
        self.password_label = ctk.CTkLabel(self, text="Password")
        self.website_entry = ctk.CTkEntry(self)
        self.username_entry = ctk.CTkEntry(self)
        self.password_entry = ctk.CTkEntry(self)
        self.save_button = ctk.CTkButton(self, text="Save", width=60, command=self.save_values)

        # Placement
        self.website_label.grid(row=0, column=1)
        self.website_entry.grid(row=1, column=1, padx=2.5, pady=10)
        self.username_label.grid(row=0, column=2)
        self.username_entry.grid(row=1, column=2, padx=2.5, pady=10)
        self.password_label.grid(row=0, column=3)
        self.password_entry.grid(row=1, column=3, padx=2.5, pady=10)
        self.save_button.grid(row=1, column=4, padx=5)

        # Enter key binding
        self.website_entry.bind('<Return>', lambda event: self.save_values())
        self.username_entry.bind('<Return>', lambda event: self.save_values())
        self.password_entry.bind('<Return>', lambda event: self.save_values())

        # Populate Treeview
        self.populate_treeview()

    def populate_treeview(self):
        session = DBSession()
        try:
            passwords = session.query(Passwords).all()
            for entry in passwords:
                item_id = self.password_table.insert('', 'end', values=(entry.website, entry.username, "••••••••", "Show"))
                self.password_visibility[item_id] = False
        except SQLAlchemyError as e:
            messagebox.showerror("Error", f"Could not load saved passwords:\n{e}")
        finally:
            session.close()

    def handle_toggle_click(self, event):
        region = self.password_table.identify("region", event.x, event.y)
        if region != "cell":
            return

        column = self.password_table.identify_column(event.x)
        row_id = self.password_table.identify_row(event.y)

        if column == "#4" and row_id:
            visible = self.password_visibility.get(row_id, False)
            values = self.password_table.item(row_id, "values")
            website, username, _, _ = values

            session = DBSession()
            try:
                entry = session.query(Passwords).filter_by(website=website, username=username).first()
                if entry:
                    try:
                        decrypted = decrypt_password(entry.password)
                    except Exception:
                        decrypted = "[Error]"

                    if not visible:
                        self.password_table.item(row_id, values=(website, username, decrypted, "Hide"))
                        self.password_visibility[row_id] = True
                    else:
                        self.password_table.item(row_id, values=(website, username, "••••••••", "Show"))
                        self.password_visibility[row_id] = False
            finally:
                session.close()

    def save_values(self):
        website = self.website_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not website or not username or not password:
            messagebox.showwarning("Missing Info", "Please fill out all fields.")
            return

        encrypted = encrypt_password(password)

        item_id = self.password_table.insert('', 'end', values=(website, username, "••••••••", "Show"))
        self.password_visibility[item_id] = False

        session = DBSession()
        try:
            new_entry = Passwords(website=website, username=username, password=encrypted)
            session.add(new_entry)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            messagebox.showerror("Error", f"Could not save password:\n{e}")
        finally:
            session.close()

        self.website_entry.delete(0, END)
        self.username_entry.delete(0, END)
        self.password_entry.delete(0, END)