"""
Name: John Roby
Date: 10/22/2024
Description: A password manager gui app.
"""
from tkinter import ttk
import customtkinter as ctk
from Components.header import Header
from Components.password_table import PasswordTable
from Components.form import Form
from Components.generate_password import GeneratePassword

# App class inherits tkinter
class App(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        __version__ = "0.0.1"
        self.title('Password Manager')
        self.minsize(550, 660)
        self.maxsize(550, 660)
        # Set default theme
        ctk.set_appearance_mode("system")  # Options: "Light", "Dark", "System"
        ctk.set_default_color_theme("dark-blue")
        # Initialize components
        self.password_table = PasswordTable(self)
        self.header = Header(self, self.password_table.password_table)
        self.form = Form(self, self.password_table.password_table)
        self.generate_password = GeneratePassword(self)
        self.version_label = ctk.CTkLabel(self, text=f"v{__version__}")
        # Theme switch
        self.theme_switch = ctk.CTkSwitch(self, text="Dark Mode", command=self.toggle_theme, onvalue="Dark", offvalue="System")
        # Place Components
        self.header.pack(pady=5)
        self.password_table.pack(fill="x")
        self.form.pack(fill="x")
        self.generate_password.pack(fill="both", expand="true", ipady=10, ipadx=10)
        self.theme_switch.pack()
        self.version_label.pack(side="bottom")

    def toggle_theme(self):
        style = ttk.Style()
        mode = self.theme_switch.get()

        if mode == "Dark":
            style.theme_use("clam")
            style.configure("Treeview", fieldbackground="#1e1e1e", background="#1e1e1e", foreground="#ffffff", rowheight=24)
        else:
            style.theme_use("default")
            style.configure("Treeview", fieldbackground="#ffffff", background="#ffffff", foreground="#1e1e1e", rowheight=24)

        ctk.set_appearance_mode(mode)


if __name__ == "__main__":
    App().mainloop()
