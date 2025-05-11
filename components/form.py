"""
Description: form.py - Custom Component Class Form.
"""

import sqlite3
from tkinter import messagebox
from tkinter import END, ttk
import customtkinter as ctk
from utils import encrypt_password, decrypt_password
from sqlalchemy import create_engine, Column, String, Integer, CHAR
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Password(Base):
    __tablename__ = 'passwords'

    id = Column(Integer, primary_key=True)
    website = Column(String, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)


    def __init__(self, website, username, password):
        self.website = website
        self.username = username
        self.password = password

    def __repr__(self):
        return f"<Password(website='{self.website}', username='{self.username}')>"

# Custom Component Class CreatePassword
class Form(ctk.CTkFrame):
    def __init__(self, parent, password_table):
        super().__init__(parent)
        self.password_table = password_table
        self.password_table.bind("<Button-1>", self.handle_toggle_click)
        self.password_visibility = {}  # track which rows have visible passwords
        # Grid Layout
        self.rowconfigure(0, weight=1)
        self.columnconfigure((0,1,2,3,4,5), weight=1)
        # Create Widgets
        self.style = ttk.Style()
        self.style.configure("TButton", foreground="teal")
        self.website_label = ctk.CTkLabel(self, text="Website")
        self.username_label = ctk.CTkLabel(self, text="Username")
        self.password_label =ctk.CTkLabel(self, text="Password")
        self.website_entry = ctk.CTkEntry(self)
        self.username_entry = ctk.CTkEntry(self)
        self.password_entry = ctk.CTkEntry(self)
        self.save_button =  ctk.CTkButton(self, text="Save", width=60, command=self.save_values)
        
        # Place
        self.website_label.grid(row=0, column=1)
        self.website_entry.grid(row=1, column=1, padx=2.5, pady=10)
        self.username_label.grid(row=0, column=2)
        self.username_entry.grid(row=1, column=2, padx=2.5, pady=10)
        self.password_label.grid(row=0, column=3)
        self.password_entry.grid(row=1, column=3, padx=2.5, pady=10)
        # Bind Enter key to save from any input field
        self.website_entry.bind('<Return>', lambda event: self.save_values())
        self.username_entry.bind('<Return>', lambda event: self.save_values())
        self.password_entry.bind('<Return>', lambda event: self.save_values())
        self.save_button.grid(row=1, column=4, padx=5)
        
        # Set up Database
        self.setup_db()
        # Populate Treeview
        self.populate_treeview()

    def setup_db(self):
        engine = create_engine('sqlite:///passwords_db')
        Base.metadata.create_all(engine)

    def populate_treeview(self):
        engine = create_engine('sqlite:///passwords_db')
        Session = sessionmaker(bind=engine)
        session = Session()

        rows = session.query(Password.website, Password.username, Password.password).all()

        for website, username, encrypted_password in rows:
            item_id = self.password_table.insert('', 'end', values=(website, username, "••••••••", "Show"))
            self.password_visibility[item_id] = False

        session.close()

    def handle_toggle_click(self, event):
        region = self.password_table.identify("region", event.x, event.y)
        if region != "cell":
            return

        column = self.password_table.identify_column(event.x)
        row_id = self.password_table.identify_row(event.y)

        if column == "#4" and row_id:  # toggle column
            visible = self.password_visibility.get(row_id, False)
            values = self.password_table.item(row_id, "values")
            website, username, _, _ = values

            # Use SQLAlchemy to query the password
            engine = create_engine('sqlite:///passwords_db')
            Session = sessionmaker(bind=engine)
            session = Session()
            result = session.query(Password.password).filter_by(website=website, username=username).first()
            session.close()

            if result:
                encrypted_password = result[0]
                try:
                    decrypted = decrypt_password(encrypted_password)
                except Exception:
                    decrypted = "[Error]"

                if not visible:
                    self.password_table.item(row_id, values=(website, username, decrypted, "Hide"))
                    self.password_visibility[row_id] = True
                else:
                    self.password_table.item(row_id, values=(website, username, "••••••••", "Show"))
                    self.password_visibility[row_id] = False


    def save_values(self):
        website = self.website_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not website or not username or not password:
            messagebox.showwarning("Missing Info", "Please fill out all fields.")
            return

        encrypted_password = encrypt_password(password)

        # Insert masked password and "Show" into Treeview
        item_id = self.password_table.insert(parent="", index="end", values=(website, username, "••••••••", "Show"))
        self.password_visibility[item_id] = False  # Track visibility for this row

        # Save to DB
        connection = sqlite3.connect("passwords_db")
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO passwords (website, username, password)
            VALUES (?, ?, ?)
        ''', (website, username, encrypted_password))
        connection.commit()
        connection.close()

        # Clear entries
        self.website_entry.delete(0, END)
        self.username_entry.delete(0, END)
        self.password_entry.delete(0, END)