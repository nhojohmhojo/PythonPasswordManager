"""
Description: header.py - Custom Component Class header.
"""
from sqlalchemy.orm import Session
import customtkinter as ctk
from tkinter import messagebox
from database import Database

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

        db = Database()
        deleted = 0
        try:
            for item in selected_items:
                # Treeview rows store the entry ID in the first value
                entry_id = int(self.password_table.item(item, "values")[0])
                # Remove from UI
                self.password_table.delete(item)
                # Remove from DB via your helper
                db.delete_password_by_id(entry_id)
                deleted += 1

            messagebox.showinfo("Deleted", f"Successfully deleted {deleted} record{'s' if deleted != 1 else ''}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete record(s): {e}")
        finally:
            db.close()