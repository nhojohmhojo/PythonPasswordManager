"""
Description: password_table.py - Custom Component Class PasswordTable.
"""
from sqlalchemy import create_engine, ForeignKey, Column, Intger, String, Integer, CHAR
from sqlalchemy.orm import sessionmaker
from tkinter import CENTER, ttk
import customtkinter as ctk
import csv
from tkinter import filedialog, messagebox
from utils import encrypt_password
from components.form import Password, Base


# Custom Component Class PasswordTable
class PasswordTable(ctk.CTkFrame):
        # Create the Treeview widget
    def __init__(self, parent):
        super().__init__(parent)
        self.password_table = ttk.Treeview(self, show="headings")
        # Columns
        self.password_table['columns'] = ("Website", "Username", "Password", "Toggle")
        self.password_table.column("#0", width=0, minwidth=0)
        self.password_table.column("Website", anchor=CENTER, width=130)
        self.password_table.column("Username", anchor=CENTER, width=130)
        self.password_table.column("Password", anchor=CENTER, width=130)
        self.password_table.column("Toggle", anchor=CENTER, width=60)
        # Table Headings
        self.password_table.heading("#0")
        self.password_table.heading("Website", text="Website", anchor=CENTER)
        self.password_table.heading("Username", text="Username", anchor=CENTER)
        self.password_table.heading("Password", text="Password", anchor=CENTER)
        self.password_table.heading("Toggle", text="Toggle", anchor=CENTER)
        # Scrollbar setup
        self.scrollbar = ctk.CTkScrollbar(self, orientation="vertical", command=self.password_table.yview)
        self.password_table.configure(yscrollcommand=self.scrollbar.set)
        # Place Treeview and Scrollbar
        self.password_table.grid(row=0, column=0, sticky="nsew", padx=10)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        # Create Upload Button
        upload_button = ctk.CTkButton(self, text="Upload CSV", command=self.upload_csv)
        upload_button.grid(row=1, column=0, columnspan=2)
        # Allow resizing of the treeview and scrollbar with the window
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        def upload_csv(self):
            file_path = filedialog.askopenfilename(
                title="Select CSV File",
                filetypes=(("CSV files", "*.csv"),)
            )

            if not file_path:
                return

            try:
                with open(file_path, newline='', encoding='utf-8') as csvfile:
                    sample = csvfile.read(2048)
                    csvfile.seek(0)

                    sniffer = csv.Sniffer()
                    has_header = sniffer.has_header(sample)
                    reader = csv.reader(csvfile)
                    headers = next(reader) if has_header else None

                    header_map = {'website': 0, 'username': 1, 'password': 2}

                    if headers:
                        normalized = [h.strip().lower() for h in headers]
                        synonym_map = {
                            "website": ["website", "site", "url", "domain"],
                            "username": ["username", "user", "login", "email"],
                            "password": ["password", "pass", "pwd"]
                        }
                        header_map = {}
                        for field, keys in synonym_map.items():
                            for key in keys:
                                if key in normalized:
                                    header_map[field] = normalized.index(key)
                                    break
                        if not all(k in header_map for k in ["website", "username", "password"]):
                            messagebox.showerror("Error",
                                                 "CSV must include columns for website, username, and password.")
                            return

                    rows = list(reader)

                engine = create_engine('sqlite:///passwords_db', echo=True)
                Base.metadata.create_all(bind=engine)
                Session = sessionmaker(bind=engine)
                session = Session()

                rows_added = 0
                for row in rows:
                    try:
                        website = row[header_map['website']].strip()
                        username = row[header_map['username']].strip()
                        password = row[header_map['password']].strip()
                    except (IndexError, KeyError):
                        continue

                    if not website or not username or not password:
                        continue


                    encrypted_password = encrypt_password(password)
                    new_entry = Password(website=website, username=username, password=encrypted_password)
                    session.add(new_entry)

                    self.password_table.insert('', 'end', values=(website, username, "••••••••", "Show"))
                    rows_added += 1

                session.commit()
                session.close()

                messagebox.showinfo("Success", f"{rows_added} record(s) imported successfully.")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load CSV:\n{str(e)}")


