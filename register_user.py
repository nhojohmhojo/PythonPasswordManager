"""
Description: register_user.py - Custom Component Class RegisterUser.
"""
import sqlite3
import customtkinter as ctk
from customtkinter import CTkImage, W
from tkinter import messagebox, PhotoImage
from PIL import ImageTk, Image
import re

class RegisterUser(ctk.CTk):
    def __init__(self):
        super().__init__()
        # Set up Window
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("dark-blue")
        self.title('Registration')
        # self.wm_iconbitmap("images/password_icon.ico")
        self.minsize(400, 500)
        self.maxsize(400, 500)
        # Grid Layout
        self.columnconfigure((0,1,2,3,4,5), weight=1)
        self.rowconfigure((0,1,2,3,4,5,6,7,8,9), weight=1)
        # Open and Resize Image
        self.image = Image.open("images/password_image.png")
        self.new_image = ctk.CTkImage(light_image=self.image, dark_image=self.image, size=(50, 50))
        # Set up Database
        self.setup_db()
        # Create Widgets
        self.create_widgets()

    def create_widgets(self):
        self.image_label = ctk.CTkLabel(self, text="", image=self.new_image)
        self.image_label.grid(row=0, column=0)
        
        self.create_username_label = ctk.CTkLabel(self, text="Create a username:", font=("Arial", 16, "bold"))
        self.create_username_label.grid(row=0, column=2)
        self.username_entry = ctk.CTkEntry(self)
        self.username_entry.grid(row=1, column=2)
        
        self.create_password_label = ctk.CTkLabel(self, text="Create a password:", font=("Arial", 16, "bold"))
        self.create_password_label.grid(row=2, column=2)
        self.password_entry = ctk.CTkEntry(self, show="*")
        self.password_entry.grid(row=3, column=2)

        self.confirm_password_label = ctk.CTkLabel(self, text="Confirm password:", font=("Arial", 16, "bold"))
        self.confirm_password_label.grid(row=4, column=2)
        self.confrim_password_entry = ctk.CTkEntry(self, show="*")
        self.confrim_password_entry.grid(row=5, column=2)

        self.button = ctk.CTkButton(self, text="Register", command=self.validate_registration)
        self.button.grid(row=6, column=2)

        self.already_a_user = ctk.CTkLabel(self, text="Already a user?")
        self.already_a_user.grid(row=8, column=2)
        self.login_link = ctk.CTkLabel(self, text="Login", text_color="blue", cursor="hand2")
        self.login_link.grid(row=9, column=2)
        self.login_link.bind("<Button-1>", self.open_app_window)
        # Bind Enter key to Login
        self.bind('<Return>', lambda event: self.validate_registration())

    def setup_db(self):
        connection = sqlite3.connect("users_db")
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY,
                        password TEXT NOT NULL
                    )''')
        connection.commit()
        connection.close()

    def validate_registration(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm = self.confrim_password_entry.get()

        if not username or not password or not confirm:
            messagebox.showwarning("Validation Error", "All fields are required.")
            return
        if password != confirm:
            messagebox.showwarning("Validation Error", "Passwords do not match.")
            return
        if len(username) < 3:
            messagebox.showwarning("Validation Error", "Username must be at least 3 characters.")
            return
        if not re.match(r"^[A-Za-z0-9_]+$", username):
            messagebox.showwarning("Validation Error", "Username may only contain letters, digits and underscores.")
            return
        
        if len(password) < 8:
            messagebox.showwarning(
                "Validation Error",
                "Password must be at least 8 characters long."
            )
            return
        if not re.search(r"[A-Z]", password):
            messagebox.showwarning(
                "Validation Error",
                "Password must include at least one uppercase letter."
            )
            return
        if not re.search(r"[a-z]", password):
            messagebox.showwarning(
                "Validation Error",
                "Password must include at least one lowercase letter."
            )
            return
        if not re.search(r"\d", password):
            messagebox.showwarning(
                "Validation Error",
                "Password must include at least one digit."
            )
            return
        if not re.search(r"[!@#$%^&*()\-_=+\[\]{};:'\",.<>/?\\|`~]", password):
            messagebox.showwarning(
                "Validation Error",
                "Password must include at least one special character."
            )
            return
        
        # Import the encryption function for passwords
        from components.form import encrypt_password
        encrypted_password = encrypt_password(password)
        # Try inserting into the database
        try:
            with sqlite3.connect("users_db", timeout=10) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, encrypted_password)
                )
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "That username is already taken.")
            return
        except sqlite3.OperationalError as e:
            messagebox.showerror("Error", f"Database error: {e}")
            return

        # Success!
        messagebox.showinfo("Success", "Registration complete. You can now log in.")
        self.open_app_window()

    def open_app_window(self, event=None):
        from login import Login
        Login()
        self.withdraw()


if __name__ == "__main__":
    RegisterUser().mainloop()
