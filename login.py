"""
Description: login.py - Custom Component Class Login.
"""
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from app import App
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from models import Session, Users
from components.form import decrypt_password

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

    def validate_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        session = Session()
        try:
            select_statement = select(Users).where(Users.username == username)
            result = session.execute(select_statement).first()
            user = result[0] if result else None
        except SQLAlchemyError as e:
            messagebox.showerror("Error", f"Database error: {e}")
            return
        finally:
            session.close()

        if not user:
            messagebox.showerror("Error", "Invalid username or password.")
            return

        try:
            decrypted_password = decrypt_password(user.password)
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
