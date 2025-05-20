"""
Description: register_and_login.py - Custom Component Class RegisterAndLogin, which contains two frames: Register and Login.
"""
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import re
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from database import create_tables, User, Database
from utils import center_window


class RegisterAndLogin(ctk.CTk):
    def __init__(self):
        super().__init__()
        # Set up Window
        self.minsize(400, 500)
        self.maxsize(400, 500)
        self.title('Login')
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("dark-blue")
        # Load and resize Logo Image
        self.logo_image = Image.open("images/password_image.png")
        self.new_login_image = ctk.CTkImage(light_image=self.logo_image, dark_image=self.logo_image, size=(100, 100))
        self.new_register_image = ctk.CTkImage(light_image=self.logo_image, dark_image=self.logo_image, size=(50, 50))
        # Initialize Frames
        self.login_frame = self.create_login_frame()
        self.register_frame = self.create_register_frame()
        # Show login first
        self.show_frame(self.login_frame)
        # Setup Database
        create_tables()
        # Center Window
        self.center_window = center_window(self, 400, 500)

    def show_frame(self, frame):
        self.unbind("<Return>")
        self.login_frame.pack_forget()
        self.register_frame.pack_forget()
        if frame == self.login_frame:
            self.title('Login')
            self.bind('<Return>', lambda event: self.validate_login())
        elif frame == self.register_frame:
            self.title('Registration')
            self.bind('<Return>', lambda event: self.validate_registration())
        else:
            raise ValueError("Invalid frame.")
        frame.pack(fill="both", expand=True)


    def create_login_frame(self):
        self.login_frame = ctk.CTkFrame(self)
        self.login_image_label = ctk.CTkLabel(self.login_frame, text="", image=self.new_login_image)
        self.login_image_label.pack()

        self.username_label = ctk.CTkLabel(self.login_frame, text="Username:")
        self.username_entry = ctk.CTkEntry(self.login_frame)
        self.username_label.pack(pady=(20, 0))
        self.username_entry.pack(pady=(0, 10))

        self.password_label = ctk.CTkLabel(self.login_frame, text="Password:")
        self.password_entry = ctk.CTkEntry(self.login_frame, show="*")
        self.password_label.pack(pady=(20, 0))
        self.password_entry.pack(pady=(0, 10))

        self.button = ctk.CTkButton(self.login_frame, text="Login", command=self.validate_login)
        self.button.pack(pady=(20, 0))


        self.need_a_user_account = ctk.CTkLabel(self.login_frame, text="Need a user account?")
        self.need_a_user_account.pack(pady=(100, 0))
        self.register_link = ctk.CTkLabel(self.login_frame, text="Register", text_color="blue", cursor="hand2")
        self.register_link.pack()
        self.register_link.bind("<Button-1>", lambda event: self.show_frame(self.register_frame))
        return self.login_frame

    def validate_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        db = Database()
        try:
            user = db.verify_user(username, password)
            if not user:
                messagebox.showerror("Error", "Invalid username or password.")
                db.close()
                return
            # Clear entry fields after successful login
            self.username_entry.delete(0, 'end')
            self.password_entry.delete(0, 'end')
            self.withdraw()
            self.open_app_window()
        except SQLAlchemyError as e:
            messagebox.showerror("Error", f"Login error: {e}")
            return
        finally:
            db.close()

    def create_register_frame(self):
        self.register_frame = ctk.CTkFrame(self)
        self.register_image_label = ctk.CTkLabel(self.register_frame, text="", image=self.new_register_image)
        self.register_image_label.grid(row=0, column=0)

        self.register_frame.columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        self.register_frame.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9), weight=1)

        self.create_username_label = ctk.CTkLabel(self.register_frame, text="Create a username:", font=("Arial", 16, "bold"))
        self.create_username_label.grid(row=0, column=2)
        self.create_username_entry = ctk.CTkEntry(self.register_frame)
        self.create_username_entry.grid(row=1, column=2)

        self.create_password_label = ctk.CTkLabel(self.register_frame, text="Create a password:", font=("Arial", 16, "bold"))
        self.create_password_label.grid(row=2, column=2)
        self.create_password_entry = ctk.CTkEntry(self.register_frame, show="*")
        self.create_password_entry.grid(row=3, column=2)

        self.confirm_password_label = ctk.CTkLabel(self.register_frame, text="Confirm password:", font=("Arial", 16, "bold"))
        self.confirm_password_label.grid(row=4, column=2)
        self.confirm_password_entry = ctk.CTkEntry(self.register_frame, show="*")
        self.confirm_password_entry.grid(row=5, column=2)

        self.button = ctk.CTkButton(self.register_frame, text="Register", command=self.validate_registration)
        self.button.grid(row=6, column=2)

        self.already_a_user = ctk.CTkLabel(self.register_frame, text="Already a user?")
        self.already_a_user.grid(row=7, column=2, sticky="s")
        self.login_link = ctk.CTkLabel(self.register_frame, text="Login", text_color="blue", cursor="hand2")
        self.login_link.grid(row=8, column=2)
        self.login_link.bind("<Button-1>", lambda event: self.show_frame(self.login_frame))
        return self.register_frame

    def validate_registration(self):
        create_username = self.create_username_entry.get().strip()
        create_password = self.create_password_entry.get().strip()
        confirm = self.confirm_password_entry.get().strip()

        # === Validation ===
        if not create_username or not create_password or not confirm:
            messagebox.showwarning("Validation Error", "All fields are required.")
            return
        if create_password != confirm:
            messagebox.showwarning("Validation Error", "Passwords do not match.")
            return
        if len(create_username) < 3:
            messagebox.showwarning("Validation Error", "Username must be at least 3 characters.")
            return
        if not re.match(r"^[A-Za-z0-9_]+$", create_username):
            messagebox.showwarning("Validation Error", "Username may only contain letters, digits and underscores.")
            return
        if len(create_password) < 8:
            messagebox.showwarning("Validation Error", "Password must be at least 8 characters long.")
            return
        if not re.search(r"[A-Z]", create_password):
            messagebox.showwarning("Validation Error", "Password must include at least one uppercase letter.")
            return
        if not re.search(r"[a-z]", create_password):
            messagebox.showwarning("Validation Error", "Password must include at least one lowercase letter.")
            return
        if not re.search(r"\d", create_password):
            messagebox.showwarning("Validation Error", "Password must include at least one digit.")
            return
        if not re.search(r"[!@#$%^&*()\-_=+\[\]{};:'\",.<>/?\\|`~]", create_password):
            messagebox.showwarning("Validation Error", "Password must include at least one special character.")
            return

        # === Save to DB ===
        db = Database()
        try:
            new_user = User(username=create_username, password=create_password)
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
        self.show_frame(self.login_frame)

    def open_app_window(self):
        from app import App
        app = App(login_window=self)
        self.withdraw()

if __name__ == "__main__":
    RegisterAndLogin().mainloop()
