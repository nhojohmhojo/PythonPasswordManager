"""
Description: login.py - Custom Component Class Login.
"""
import sqlite3
import customtkinter as ctk
from tkinter import messagebox
from PIL import ImageTk, Image
from app import App


class Login(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        # Set up Window
        self.title('Login')
        self.minsize(300, 400)
        self.maxsize(300, 400)
        # Open and Resize Image
        self.image = Image.open("images/password_image.png")
        self.new_image = ctk.CTkImage(light_image=self.image, dark_image=self.image, size=(100, 100))
        # Set up Database
        self.setup_db()
        # Create Widgets
        self.create_widgets()

    def create_widgets(self):
        self.image_label = ctk.CTkLabel(self, text="", image=self.new_image)
        self.image_label.pack(pady=20, padx=20)
        self.username_label = ctk.CTkLabel(self, text="Username:")
        self.username_entry = ctk.CTkEntry(self)
        self.username_label.pack()
        self.username_entry.pack()
        self.password_label = ctk.CTkLabel(self, text="Password:")
        self.password_entry = ctk.CTkEntry(self, show="*")
        self.password_label.pack()
        self.password_entry.pack()
        self.button = ctk.CTkButton(self, text="Login", command=self.validate_login)
        self.button.pack(pady=20)
        # Bind Enter key to Login
        self.bind('<Return>', lambda event: self.validate_login())

    def setup_db(self):
        connection = sqlite3.connect("users_db")
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY,
                        password TEXT NOT NULL
                    )''')
        connection.commit()
        connection.close()

    def validate_login(self):
        from utils import decrypt_password
        username = self.username_entry.get()
        password = self.password_entry.get()
        connection = sqlite3.connect("users_db")
        cursor = connection.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        connection.close()

        if not row:
            messagebox.showerror("Error", "Invalid username or password.")
        
        encrypted_password = row[0]

        try:
            decrypted_password = decrypt_password(encrypted_password)
        except Exception as e:
            messagebox.showerror("Error", f"Could not validate password: {e}")
            return
    
        if password == decrypted_password:
            self.open_app_window()
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    def open_app_window(self):
        App()
        self.withdraw()
    
        
if __name__ == "__main__":
    Login().mainloop()
