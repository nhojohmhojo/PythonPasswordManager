"""
Description: header.py - Custom Component Class header.
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
        self.columnconfigure((0,1,2,3,4,5,6,7,8,9), weight=1)
        # Other Attributes
        self.login_window = login_window
        self.password_table = password_table
        self.form = form
        self.editing_item_id = None
        self.editing_record_id = None
        self.configure(corner_radius=0)
        # Create Widgets
        self.create_header_widgets()

    def create_header_widgets(self):
        """Creates and places header widgets"""
        self.search_entry = ctk.CTkEntry(self)
        self.search_entry.grid(row=0, column=0, columnspan=3, sticky="ew")
        self.search_button = ctk.CTkButton(self, text="Search", width=60, command=self.search_treeview)
        self.search_button.grid(row=0, column=3)
        self.clear_button = ctk.CTkButton(self, text="Clear", width=60, command=self.clear_search)
        self.clear_button.grid(row=0, column=4, padx=5)
        self.delete_button =  ctk.CTkButton(self, text="Delete", width=60, command=self.delete_record)
        self.delete_button.grid(row=0, column=5)
        self.edit_button = ctk.CTkButton(self, text="Edit", fg_color="teal", text_color="white", hover_color="#148f77", width=60, command=self.edit_record)
        self.edit_button.grid(row=0, column=6, padx=5)
        self.logout_button = ctk.CTkButton(self, text="", image=self.tk_image, width=10, fg_color="transparent", command=self.logout)
        self.logout_button.grid(row=0, column=9, sticky="e")
        # Bind Enter key to search
        self.search_entry.bind('<Return>', lambda event: self.search_treeview())
        print("Frame background color:", self.cget("fg_color"))

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

    def edit_record(self):
        selected = self.password_table.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a record to edit.")
            return
        # Set Form mode
        self.form.set_mode("Edit")
        # Change the Edit button to Cancel
        self.edit_button.configure(text="Cancel", fg_color="#c0392b", text_color="white", hover_color="red", command=self.cancel_edit)
        self.form.save_button.configure(text="Update", command=self.form.save_values)

        item_id = selected[0]
        item = self.password_table.item(item_id)
        values = item.get("values", [])

        if len(values) < 4:
            messagebox.showerror("Error", "Incomplete record.")
            return

        record_id = values[0]
        self.editing_item_id = item_id
        self.editing_record_id = record_id

        # Fill in website and username
        self.form.website_entry.delete(0, 'end')
        self.form.website_entry.insert(0, values[1])
        self.form.username_entry.delete(0, 'end')
        self.form.username_entry.insert(0, values[2])

        db = Database()
        try:
            record = db.session.query(Password).filter_by(id=record_id).first()
            if not record:
                messagebox.showerror("Error", "Record not found in database.")
                return

            decrypted_password = decrypt_password(record.password, record.profile)
            self.form.password_entry.configure(show="•" if self.form.password_entry.cget("show") == "•" else "•")
            self.form.password_entry.delete(0, 'end')
            self.form.password_entry.insert(0, decrypted_password)

        except Exception as e:
            messagebox.showerror("Error", f"Decryption failed:\n{e}")
        finally:
            db.close()

    def cancel_edit(self):
        # Clear form fields
        self.form.website_entry.delete(0, 'end')
        self.form.username_entry.delete(0, 'end')
        self.form.password_entry.delete(0, 'end')

        # Reset form mode
        self.form.set_mode("Create")

        # Restore Edit and Save button to normal
        self.edit_button.configure(text="Edit", fg_color="teal", text_color="white", hover_color="#148f77", command=self.edit_record)
        self.form.save_button.configure(text="Save", width=60, fg_color="teal", text_color="white", hover_color="#148f77", command=self.form.save_values)


        # Clear editing state
        if hasattr(self, 'editing_record_id'):
            del self.editing_record_id
        if hasattr(self, 'editing_item_id'):
            del self.editing_item_id

    def logout(self):
        try:
            self.logout_button.configure(state="disabled")
        except AttributeError:
            messagebox.showwarning("Warning", "Logout button not found. Proceeding anyway.")

        confirm = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if confirm:
            db = Database()
            db.current_user = None
            db.close()
            self.winfo_toplevel().destroy()
            try:
                self.login_window.deiconify()
            except AttributeError as e:
                messagebox.showerror("Error", f"Failed to reopen login window:\n{e}")
        else:
            try:
                self.logout_button.configure(state="normal")
            except AttributeError:
                messagebox.showwarning("Warning", "Logout button not found. Cannot re-enable.")

    def set_theme(self, palette):
        self.configure(bg_color=palette["bg"])
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkLabel):
                widget.configure(text_color=palette["fg"])