"""
Description: password_table.py - Custom Component Class PasswordTable.
"""
import sqlite3
from tkinter import CENTER, ttk
import customtkinter as ctk
import csv
from tkinter import filedialog, messagebox

# Custom Component Class PasswordTable
class PasswordTable(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        # Create the Treeview widget
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
        # Configure Row Height
        self.style = ttk.Style(self)
        self.style.configure('Treeview.Heading', rowheight=24, font=18)
        self.style.configure('Treeview', rowheight=24, font=18)
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
        # Open a file dialog for the user to select a CSV file
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=(("CSV files", "*.csv"),)
        )

        # If the user canceled the dialog, exit early
        if not file_path:
            return  # user cancelled

        try:
            # Open the selected CSV file for reading
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                # Read a sample to let Sniffer detect if there's a header row
                sample = csvfile.read(2048)
                csvfile.seek(0)  # rewind back to the start of the file

                sniffer = csv.Sniffer()
                has_header = sniffer.has_header(sample)
                reader = csv.reader(csvfile)
                # If a header exists, consume the first row as headers; otherwise headers=None
                headers = next(reader) if has_header else None

                # Default mapping: assume columns in order website, username, password
                header_map = {'website': 0, 'username': 1, 'password': 2}

                if headers:
                    # Normalize header names (strip whitespace, lowercase)
                    normalized = [h.strip().lower() for h in headers]
                    # Synonyms for each canonical field
                    synonym_map = {
                        "website":  ["website", "site", "url", "domain"],
                        "username": ["username", "user", "login", "email"],
                        "password": ["password", "pass", "pwd"]
                    }
                    # Build header_map only for matching synonyms
                    header_map = {}
                    for field, keys in synonym_map.items():
                        for key in keys:
                            if key in normalized:
                                header_map[field] = normalized.index(key)
                                break
                    # Ensure all required fields are present
                    if not all(k in header_map for k in ["website", "username", "password"]):
                        messagebox.showerror(
                            "Error",
                            "CSV must include columns for website, username, and password."
                        )
                        return

                # Read all remaining rows while file is open
                rows = list(reader)

            # Import the encryption function for passwords
            from components.form import encrypt_password
            # Connect to the SQLite database for storing passwords
            connection = sqlite3.connect("passwords_db")
            cursor = connection.cursor()
            rows_added = 0  # counter for successfully imported rows

            # Iterate over each row collected
            for row in rows:
                try:
                    # Extract and clean each field based on the header_map
                    website = row[header_map['website']].strip()
                    username = row[header_map['username']].strip()
                    password = row[header_map['password']].strip()
                except (IndexError, KeyError):
                    continue  # skip rows that don't have enough columns

                # Skip rows with any empty required field
                if not website or not username or not password:
                    continue

                # Encrypt the plaintext password
                encrypted_password = encrypt_password(password)

                # Insert the record into the database
                cursor.execute(
                    "INSERT INTO passwords (website, username, password) VALUES (?, ?, ?)",
                    (website, username, encrypted_password)
                )

                # Also add the entry to the GUI table, masking the password
                self.password_table.insert('', 'end', values=(website, username, "••••••••", "Show"))
                rows_added += 1  # increment success counter

            # Commit all changes and close the connection
            connection.commit()
            connection.close()

            # Inform the user of the number of records imported
            messagebox.showinfo("Success", f"{rows_added} record(s) imported successfully.")

        except Exception as e:
            # Show an error dialog if something went wrong during processing
            messagebox.showerror("Error", f"Failed to load CSV:\n{str(e)}")


