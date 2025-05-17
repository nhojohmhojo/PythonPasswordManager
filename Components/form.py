"""
Description: form.py - Custom Component Class Form.
"""
from tkinter import messagebox
from tkinter import END, ttk
import customtkinter as ctk
from database import Database, Password
from utils import encrypt_password

# Custom Component Class CreatePassword
class Form(ctk.CTkFrame):
    def __init__(self, parent, password_table):
        super().__init__(parent)
        self.password_table = password_table
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

    def save_values(self):
        website = self.website_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not website or not username or not password:
            messagebox.showwarning("Missing Info", "Please fill in all fields.")
            return

        encrypted_password = encrypt_password(password)

        # Ensure a user is logged in
        user = Database.current_user
        if not user:
            messagebox.showerror("Error", "No user is logged in.")
            return

        db = Database()
        try:
            # 1. Create and add the new entry, but don't commit yet
            new_entry = Password(website=website, username=username, password=encrypted_password, profile=user.id)
            db.session.add(new_entry)

            # 2. Flush to send to DB and populate new_entry.id
            db.session.flush()

            # 3. Insert into the GUI using the now-available ID
            item_id = self.password_table.insert(
                "", "end",
                values=(
                    new_entry.id,  # auto-generated ID from flush()
                    website, username, "••••••••", "Show"))
            self.password_visibility[item_id] = False

            # 4. Finally, commit the transaction
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            messagebox.showerror("Error", f"Could not save password:\n{e}")

        finally:
            db.close()

        # Clear form fields
        self.website_entry.delete(0, END)
        self.username_entry.delete(0, END)
        self.password_entry.delete(0, END)


