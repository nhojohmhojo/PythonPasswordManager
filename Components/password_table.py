"""
Description: password_table.py - Custom Component Class PasswordTable.
"""
from tkinter import CENTER, ttk, messagebox
import customtkinter as ctk
from database import Database, Password
from sqlalchemy.exc import SQLAlchemyError
from utils import decrypt_password

class PasswordTable(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        # Track visibility state per row
        self.password_visibility = {}
        self.password_table = ttk.Treeview(self, show="headings")
        self.password_table['columns'] = ("ID", "Website", "Username", "Password", "Toggle")
        self.password_table.column("#0", width=0, minwidth=0, stretch=False)
        self.password_table.column("ID", width=0, minwidth=0, stretch=False)
        self.password_table.column("Website", anchor=CENTER, width=130)
        self.password_table.column("Username", anchor=CENTER, width=130)
        self.password_table.column("Password", anchor=CENTER, width=130)
        self.password_table.column("Toggle", anchor=CENTER, width=30)
        self.password_table.heading("Website", text="Website", anchor=CENTER)
        self.password_table.heading("Username", text="Username", anchor=CENTER)
        self.password_table.heading("Password", text="Password", anchor=CENTER)
        self.password_table.heading("Toggle", text="Toggle", anchor=CENTER)
        self.password_table["displaycolumns"] = ("Website", "Username", "Password", "Toggle")
        self.style = ttk.Style(self)
        self.style.configure('Treeview.Heading', rowheight=24, font=14)
        self.style.configure('Treeview', rowheight=24, font=12)
        self.scrollbar = ctk.CTkScrollbar(self, orientation="vertical", command=self.password_table.yview)
        self.password_table.configure(yscrollcommand=self.scrollbar.set)
        self.password_table.grid(row=0, column=0, sticky="nsew", padx=10)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.upload_button = ctk.CTkButton(self, text="Import CSV", command=self.upload_csv)
        self.upload_button.grid(row=1, column=0, columnspan=2)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.password_table.bind("<ButtonRelease-1>", self.handle_toggle_click)
        self.configure(corner_radius=0)
        # Initial load
        self.populate_treeview()

    def populate_treeview(self):
        # Clear existing rows and reset visibility
        for iid in self.password_table.get_children():
            self.password_table.delete(iid)
        self.password_visibility.clear()

        # Get current user
        user = Database.current_user
        if not user:
            messagebox.showerror("Error", "No user is logged in.")
            return

        db = Database()
        try:
            passwords = db.session.query(Password).filter_by(profile=user.id).all()
            for entry in passwords:
                iid = self.password_table.insert(
                    '', 'end',
                    values=(entry.id, entry.website, entry.username, "••••••••", "Show")
                )
                self.password_visibility[iid] = False
        except SQLAlchemyError as e:
            messagebox.showerror("Error", f"Could not load passwords:\n{e}")
        finally:
            db.close()

    def handle_toggle_click(self, event):
        if self.password_table.identify("region", event.x, event.y) != "cell": return
        col = self.password_table.identify_column(event.x)
        row = self.password_table.identify_row(event.y)
        # Toggle is the 5th column internally (ID=1, Website=2, Username=3, Password=4, Toggle=5)
        if col != "#4" or not row: return
        visible = self.password_visibility.get(row, False)
        entry_id, website, username, _, _ = self.password_table.item(row, "values")
        db = Database()
        try:
            entry = db.session.get(Password, int(entry_id))
        finally:
            db.close()
        if not entry: return
        try:
            decrypted = decrypt_password(entry.password, entry.profile) if not visible else "••••••••"
        except:
            decrypted = "[Error]"
        toggle = "Hide" if not visible else "Show"
        self.password_table.item(row, values=(entry_id, website, username, decrypted, toggle))
        self.password_visibility[row] = not visible

    def upload_csv(self):
        from tkinter import filedialog, messagebox
        import csv
        from database import Database, Password
        from utils import encrypt_password

        file_path = filedialog.askopenfilename(title="Select CSV File", filetypes=(("CSV files", "*.csv"),))
        if not file_path:
            return

        try:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                sample = csvfile.read(2048); csvfile.seek(0)
                reader = csv.reader(csvfile)
                has_header = csv.Sniffer().has_header(sample)
                headers = next(reader) if has_header else None
                # Map headers or assume order
                header_map = {'website': 0, 'username': 1, 'password': 2}
                if headers:
                    normalized = [h.strip().lower() for h in headers]
                    synonym_map = {
                        'website': ['website','site','url','domain'],
                        'username': ['username','user','login','email'],
                        'password': ['password','pass','pwd']
                    }
                    header_map.clear()
                    for field, keys in synonym_map.items():
                        for key in keys:
                            if key in normalized:
                                header_map[field] = normalized.index(key)
                                break
                    if not all(field in header_map for field in ['website','username','password']):
                        messagebox.showerror("Error", "CSV must include website, username, and password columns.")
                        return
                rows = list(reader)

            db = Database()
            user = Database.current_user
            if not user:
                messagebox.showerror("Error", "No user is logged in.")
                db.close()
                return

            count = 0
            for row in rows:
                try:
                    website = row[header_map['website']].strip()
                    username = row[header_map['username']].strip()
                    password = row[header_map['password']].strip()
                except Exception:
                    continue
                if not (website and username and password):
                    continue
                encrypted = encrypt_password(password, user.id)
                entry = Password(website=website, username=username, password=encrypted, profile=user.id)
                db.session.add(entry)
                db.session.flush()
                iid = self.password_table.insert('', 'end', values=(entry.id, website, username, '••••••••', 'Show'))
                self.password_visibility[iid] = False
                count += 1
            db.session.commit()
            db.close()
            messagebox.showinfo("Success", f"Imported {count} record{'s' if count != 1 else ''}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV:{e}")

    def set_theme(self, palette):
        self.configure(bg_color=palette["bg"])
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkLabel):
                widget.configure(text_color=palette["fg"])