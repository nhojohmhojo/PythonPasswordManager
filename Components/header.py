
"""
Description: header.py - Custom Component Class Header.
"""

import customtkinter as ctk
from tkinter import messagebox
from PIL import Image

from database import Database, Password
from utils import decrypt_password


# Custom Component Header
class Header(ctk.CTkFrame):

    def __init__(self, parent, login_window, password_table, form):
        super().__init__(parent)

        logout_image = Image.open("images/account.png")
        resized_image = logout_image.resize((20, 20))

        self.tk_image = ctk.CTkImage(light_image=resized_image, dark_image=resized_image)

        # Grid Layout
        self.rowconfigure(0, weight=1)
        self.columnconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)

        # Other Attributes
        self.login_window = login_window
        self.password_table = password_table
        self.form = form
        # Configure search highlighting
        self.password_table.tag_configure("search_match", background="#FFD966", foreground="#000000")

        self.editing_item_id = None
        self.editing_record_id = None

        # Live Search Attributes
        self.all_passwords = {}
        self.search_initialized = False

        self.configure(corner_radius=0)

        # Create Widgets
        self.create_header_widgets()

    def create_header_widgets(self):
        """Creates and places header widgets."""
        self.search_entry = ctk.CTkEntry(self, width=250, placeholder_text="Search passwords...")
        self.search_entry.grid(row=0, column=0, columnspan=2, sticky="w")
        self.clear_button = ctk.CTkButton(self, text="Clear", width=60, command=self.clear_search)
        self.clear_button.grid(row=0, column=3, padx=5)
        self.delete_button = ctk.CTkButton(self, text="Delete", width=60, command=self.delete_record)
        self.delete_button.grid(row=0, column=4)
        self.edit_button = ctk.CTkButton(self,text="Edit", fg_color="teal",text_color="white", hover_color="#148f77", width=60, command=self.edit_record)
        self.edit_button.grid(row=0, column=5, padx=5)
        self.logout_button = ctk.CTkButton(self, text="", image=self.tk_image, width=10, fg_color="transparent", command=self.logout)
        self.logout_button.grid(row=0, column=7, sticky="e")
        # Bindings
        self.search_entry.bind("<Return>", self.search_treeview)
        # Live Search
        self.search_entry.bind("<KeyRelease>", self.search_treeview)

    # LIVE SEARCH

    def initialize_search(self):
        """Save original Treeview records and tags."""

        if self.search_initialized:
            return

        self.all_passwords.clear()

        for row in self.password_table.get_children():
            self.all_passwords[row] = {
                "values": self.password_table.item(row, "values"),
                "tags": self.password_table.item(row, "tags")
            }

        self.search_initialized = True

    def search_treeview(self, event=None):
        """Filter and highlight Treeview records as the user types."""

        # Initialize original records
        self.initialize_search()

        search_term = self.search_entry.get().lower().strip()

        # Clear current table
        for row in self.password_table.get_children():
            self.password_table.delete(row)

        # Remove previous selections
        self.password_table.selection_remove(
            self.password_table.selection()
        )

        # Repopulate matching records
        for row, record in self.all_passwords.items():

            values = record["values"]
            original_tags = record["tags"]

            # Website and Username
            searchable_values = values[1:3]

            if any(
                    search_term in str(value).lower()
                    for value in searchable_values
            ):

                # Preserve original tags and add search highlighting
                tags = original_tags

                if search_term:
                    tags = (*original_tags, "search_match")

                self.password_table.insert(
                    "",
                    "end",
                    iid=row,
                    values=values,
                    tags=tags
                )

    def clear_search(self):
        """Clear search and restore all records."""

        self.search_entry.delete(0, "end")

        # Restore original records
        self.search_treeview()

    def refresh_search_cache(self):
        """Refresh cached records from the Treeview.

        Call after adding or editing records when the
        complete, unfiltered table is displayed.
        """

        self.all_passwords.clear()

        for row in self.password_table.get_children():
            values = self.password_table.item(row, "values")
            self.all_passwords[row] = values

        self.search_initialized = True

    # DELETE RECORD

    def delete_record(self):

        selected_items = self.password_table.selection()

        if not selected_items:
            messagebox.showwarning(
                "No selection",
                "Please select a record to delete."
            )
            return

        db = Database()
        deleted = 0

        try:
            for item in selected_items:

                # Get database ID
                values = self.password_table.item(item, "values")
                entry_id = int(values[0])

                # Delete from database
                db.delete_password_by_id(entry_id)

                # Remove from Treeview
                if self.password_table.exists(item):
                    self.password_table.delete(item)

                # Remove from search cache
                self.all_passwords.pop(item, None)

                deleted += 1

            messagebox.showinfo(
                "Deleted",
                f"Successfully deleted {deleted} "
                f"record{'s' if deleted != 1 else ''}."
            )

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to delete record(s): {e}"
            )

        finally:
            db.close()

    # EDIT RECORD
    def edit_record(self):

        selected = self.password_table.selection()

        if not selected:
            messagebox.showwarning(
                "No selection",
                "Please select a record to edit."
            )
            return

        # Set Form mode
        self.form.set_mode("Edit")

        # Change Edit button to Cancel
        self.edit_button.configure(
            text="Cancel",
            fg_color="#c0392b",
            text_color="white",
            hover_color="red",
            command=self.cancel_edit
        )

        self.form.save_button.configure(
            text="Update",
            command=self.form.save_values
        )

        item_id = selected[0]
        item = self.password_table.item(item_id)
        values = item.get("values", [])

        if len(values) < 4:
            messagebox.showerror(
                "Error",
                "Incomplete record."
            )
            return

        record_id = values[0]

        self.editing_item_id = item_id
        self.editing_record_id = record_id

        # Fill website
        self.form.website_entry.delete(0, "end")
        self.form.website_entry.insert(0, values[1])

        # Fill username
        self.form.username_entry.delete(0, "end")
        self.form.username_entry.insert(0, values[2])

        db = Database()

        try:
            record = (
                db.session.query(Password)
                .filter_by(id=record_id)
                .first()
            )

            if not record:
                messagebox.showerror(
                    "Error",
                    "Record not found in database."
                )
                return

            decrypted_password = decrypt_password(
                record.password,
                record.profile
            )

            self.form.password_entry.configure(show="•")
            self.form.password_entry.delete(0, "end")
            self.form.password_entry.insert(
                0,
                decrypted_password
            )

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Decryption failed:\n{e}"
            )

        finally:
            db.close()

    def cancel_edit(self):

        # Clear form fields
        self.form.website_entry.delete(0, "end")
        self.form.username_entry.delete(0, "end")
        self.form.password_entry.delete(0, "end")

        # Reset form mode
        self.form.set_mode("Create")

        # Restore Edit button
        self.edit_button.configure(
            text="Edit",
            fg_color="teal",
            text_color="white",
            hover_color="#148f77",
            command=self.edit_record
        )

        # Restore Save button
        self.form.save_button.configure(
            text="Save",
            width=60,
            fg_color="teal",
            text_color="white",
            hover_color="#148f77",
            command=self.form.save_values
        )

        # Clear editing state
        self.editing_record_id = None
        self.editing_item_id = None


    # LOGOUT
    def logout(self):

        self.logout_button.configure(state="disabled")

        confirm = messagebox.askyesno(
            "Logout",
            "Are you sure you want to logout?"
        )

        if confirm:

            db = Database()

            try:
                db.current_user = None
            finally:
                db.close()

            self.winfo_toplevel().destroy()

            try:
                self.login_window.deiconify()

            except AttributeError as e:
                messagebox.showerror(
                    "Error",
                    f"Failed to reopen login window:\n{e}"
                )

        else:
            self.logout_button.configure(state="normal")


    # THEME
    def set_theme(self, palette):

        self.configure(bg_color=palette["bg"])

        for widget in self.winfo_children():

            if isinstance(widget, ctk.CTkLabel):
                widget.configure(
                    text_color=palette["fg"]
                )
