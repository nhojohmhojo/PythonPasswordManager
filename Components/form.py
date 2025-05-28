"""
Description: form.py - Custom Component Class Form.
"""
import tkinter as tk
from tkinter import messagebox, Canvas
from tkinter import END, ttk
import customtkinter as ctk
from database import Database, Password
from utils import encrypt_password
import pyperclip

# Custom Component Class CreatePassword
class Form(tk.LabelFrame):
    def __init__(self, parent, header, password_table, generated_password):
        super().__init__(parent)
        self.password_visibility = {}
        self.mode = "Create"
        self.configure(text=self.mode, fg="teal", bg="#f9f9fa", relief="groove", font=("Arial", 16, "bold"))
        # Grid Layout
        self.rowconfigure(0, weight=1)
        self.columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        # Style
        self.style = ttk.Style()
        self.style.configure("TButton", foreground="teal")
        self.configure(background="gray90")
        # Other Attributes
        self.header = header
        self.password_table = password_table
        self.generated_password = generated_password
        # Widgets
        self.website_entry = ctk.CTkEntry(self, placeholder_text="Website URL")
        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username")
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password")
        self.password_entry.bind("<Button-1>", lambda event: self.password_entry.configure(show="") if self.password_entry.cget("show") == "•" else self.password_entry.configure(show="•"))
        self.paste_button = ctk.CTkButton(self, text="Paste", width=60, command=self.paste_password)
        self.save_button = ctk.CTkButton(self, text="Save", width=60, fg_color="teal", text_color="white", hover_color="#148f77", command=self.save_values)
        # Placement
        self.website_entry.grid(row=1, column=1, padx=5, pady=10)
        self.username_entry.grid(row=1, column=2, padx=(0,2.5), pady=10)
        self.password_entry.grid(row=1, column=3, padx=(2.5,0), pady=10)
        self.paste_button.grid(row=1, column=4)
        self.save_button.grid(row=1, column=5, padx=5)
        # Enter key binding
        self.website_entry.bind('<Return>', lambda event: self.save_values())
        self.username_entry.bind('<Return>', lambda event: self.save_values())
        self.password_entry.bind('<Return>', lambda event: self.save_values())

    def set_mode(self, mode):
        self.mode = mode
        if self.mode == "Edit":
            self.configure(text=self.mode, fg="red", relief="groove", font=("Arial", 16, "bold"))
        elif self.mode == "Create":
            self.configure(text=self.mode, fg="teal", relief="groove", font=("Arial", 16, "bold"))
    
    def paste_password(self):
        self.password_entry.delete(0, "end")
        self.password_entry.insert(0, pyperclip.paste())

    def save_values(self):
        website = self.website_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not website or not username or not password:
            messagebox.showwarning("Missing Info", "Please fill in all fields.")
            return

        user = Database.current_user
        if not user:
            messagebox.showerror("Error", "No user is logged in.")
            return

        encrypted_password = encrypt_password(password, user.id)
        db = Database()
        try:
            if self.mode == "Edit" and hasattr(self.header, 'editing_record_id'):
                # === UPDATE EXISTING RECORD USING update_password_entry ===
                db.update_password_entry(entry_id=self.header.editing_record_id, new_website=website, new_username=username, new_password=encrypted_password)

                # Update the selected item in the table
                self.password_table.item(self.header.editing_item_id, values=(self.header.editing_record_id, website, username, "••••••••", "Show"))

                del self.header.editing_record_id
                del self.header.editing_item_id
                self.set_mode("Create")
                self.header.edit_button.configure(text="Edit", fg_color="teal", text_color="white", hover_color="#148f77", command=self.header.edit_record)
                self.save_button.configure(text="Save", fg_color="teal", text_color="white", hover_color="#148f77", command=self.save_values)

            else:  # === ADD NEW RECORD ===
                new_entry = Password(website=website, username=username, password=encrypted_password, profile=user.id)
                db.session.add(new_entry)
                db.session.flush()

                item_id = self.password_table.insert(
                    "", "end",
                    values=(new_entry.id, website, username, "••••••••", "Show"))
                self.password_visibility[item_id] = False
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

    def set_theme(self, palette):
        self.configure(bg=palette["bg"])
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkLabel):
                widget.configure(text_color=palette["fg"])
