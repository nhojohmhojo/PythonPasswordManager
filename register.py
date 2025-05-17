"""
Description: register.py - Custom Component Class RegisterUser.
"""
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import re
from sqlalchemy.exc import OperationalError
from database import create_tables, User, Database
class RegisterUser(ctk.CTk):
    def __init__(self):
        super().__init__()
        # Set up Window
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("dark-blue")
        self.title('Registration')
        self.minsize(400, 500)
        self.maxsize(400, 500)
        # Grid Layout
        self.columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        self.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9), weight=1)
        # Load and Resize Image
        self.image = Image.open("images/password_image.png")
        self.new_image = ctk.CTkImage(light_image=self.image, dark_image=self.image, size=(50, 50))
        # Create Widgets
        self.create_widgets()
        # Set up Database
        create_tables()

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
        self.confirm_password_entry = ctk.CTkEntry(self, show="*")
        self.confirm_password_entry.grid(row=5, column=2)

        self.button = ctk.CTkButton(self, text="Register", command=self.validate_registration)
        self.button.grid(row=6, column=2)

        self.already_a_user = ctk.CTkLabel(self, text="Already a user?")
        self.already_a_user.grid(row=8, column=2)
        self.login_link = ctk.CTkLabel(self, text="Login", text_color="blue", cursor="hand2")
        self.login_link.grid(row=9, column=2)
        self.login_link.bind("<Button-1>", self.open_login_window)
        self.bind('<Return>', lambda event: self.validate_registration())

    def validate_registration(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm = self.confirm_password_entry.get().strip()

        # === Validation ===
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
            messagebox.showwarning("Validation Error", "Password must be at least 8 characters long.")
            return
        if not re.search(r"[A-Z]", password):
            messagebox.showwarning("Validation Error", "Password must include at least one uppercase letter.")
            return
        if not re.search(r"[a-z]", password):
            messagebox.showwarning("Validation Error", "Password must include at least one lowercase letter.")
            return
        if not re.search(r"\d", password):
            messagebox.showwarning("Validation Error", "Password must include at least one digit.")
            return
        if not re.search(r"[!@#$%^&*()\-_=+\[\]{};:'\",.<>/?\\|`~]", password):
            messagebox.showwarning("Validation Error", "Password must include at least one special character.")
            return

        # === Save to DB ===
        db = Database()
        try:
            new_user = User(username=username, password=password)
            db.add_user(new_user)
        except ValueError as ve:
            db.session.rollback()
            messagebox.showerror("Error", str(ve))  # Shows "Username already exists."
            return
        except OperationalError as e:
            db.session.rollback()
            messagebox.showerror("Error", f"Database error: {e}")
            return
        finally:
            db.close()

        messagebox.showinfo("Success", "Registration complete. You can now log in.")
        self.open_login_window()

    def open_login_window(self, event=None):
        from login import Login
        Login()
        self.withdraw()

if __name__ == "__main__":
    RegisterUser().mainloop()
