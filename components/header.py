"""
Description: header.py - Custom Component Class header.
"""
from sqlalchemy import delete
from sqlalchemy.orm import Session
from models import *
import customtkinter as ctk
from tkinter import messagebox

# Custom Component Header
class Header(ctk.CTkFrame):
    def __init__(self, parent, password_table):
        super().__init__(parent)
        self.password_table = password_table
        self.session = Session()
        # Grid Layout
        self.rowconfigure(0, weight=1)
        self.columnconfigure((0,1,2,3,4), weight=1)
        # Create Widgets
        self.create_header_widgets()

    def create_header_widgets(self):
        """Creates and places header widgets"""
        self.search_entry = ctk.CTkEntry(self)
        self.search_entry.grid(row=0, column=1)
        self.search_button = ctk.CTkButton(self, text="Search", width=60, command=self.search_treeview)
        self.search_button.grid(row=0, column=2)
        self.clear_button = ctk.CTkButton(self, text="Clear", width=60, command=self.clear_search)
        self.clear_button.grid(row=0, column=3, padx=5)
        self.delete_button =  ctk.CTkButton(self, text="Delete", width=60, command=self.delete_record)
        self.delete_button.grid(row=0, column=4)
        # Bind Enter key to search
        self.search_entry.bind('<Return>', lambda event: self.search_treeview())

    def search_treeview(self):
        search_term = self.search_entry.get().lower()
        self.password_table.selection_remove(self.password_table.selection())

        for row in self.password_table.get_children():
            values = self.password_table.item(row)['values']
            if any(search_term in str(val).lower() for val in values):
                self.password_table.selection_add(row)

    def clear_search(self):
        self.search_entry.delete(0, "end")
        self.password_table.selection_remove(self.password_table.selection())

    def delete_record(self):
        selected_items = self.password_table.selection()
        if not selected_items:
            messagebox.showwarning("No selection", "Please select a record to delete.")
            return

        session = Session()
        try:
            delete_count = 0
            for item in selected_items:
                website, username = self.password_table.item(item, "values")[:2]
                # Remove from the UI immediately
                self.password_table.delete(item)
                # Core-style DELETE using delete_statement
                delete_statement = delete(Passwords).where(Passwords.website == website, Passwords.username == username)
                session.execute(delete_statement)
                delete_count += 1

            session.commit()
            messagebox.showinfo("Deleted",f"Successfully deleted {delete_count} record{'s' if delete_count != 1 else ''}.")

        except Exception as e:
            session.rollback()
            messagebox.showerror("Error", f"Failed to delete record(s): {e}")
        finally:
            session.close()