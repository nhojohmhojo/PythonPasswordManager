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
from utils import center_window, COLOR_PALETTE


# App class inherits tkinter
class App(ctk.CTkToplevel):
    def __init__(self, login_window):
        super().__init__()
        __version__ = "0.0.1"
        self.title('Password Manager')
        self.minsize(550, 660)
        self.maxsize(550, 660)
        self.login_window = login_window
        # Set default theme
        ctk.set_appearance_mode("Light")  # Options: "Light", "Dark", "System"
        ctk.set_default_color_theme("dark-blue")
        # Initialize components
        self.password_table = PasswordTable(self)
        self.header = Header(self, login_window=self.login_window, password_table=self.password_table.password_table, form=None)
        self.form = Form(self, self.header, self.password_table.password_table)
        self.header.form = self.form
        self.generate_password = GeneratePassword(self)
        self.version_label = ctk.CTkLabel(self, text=f"v{__version__}")
        # Dark Mode Switch
        self.dark_mode_switch = ctk.CTkSwitch(self, text="Dark Mode", command=self.toggle_theme, onvalue="Dark", offvalue="Light")
        # Place Components
        self.header.pack(anchor="ne", pady=1)
        self.password_table.pack(fill="x")
        self.form.pack(fill="x", pady=(0, 0))
        self.generate_password.pack(fill="both", expand="true", ipady=10, ipadx=10)
        self.dark_mode_switch.pack()
        self.version_label.pack(side="bottom")
        # Center window
        self.center_window = center_window(self,550, 660)

    def toggle_theme(self):
        mode = self.dark_mode_switch.get()
        palette = COLOR_PALETTE[mode]
        # Apply appearance mode to CustomTkinter
        ctk.set_appearance_mode(mode)
        # Apply ttk styles
        style = ttk.Style()
        style.theme_use("clam" if mode == "Dark" else "default")
        style.configure('Treeview.Heading', font=14)
        style.configure("Treeview",
                        fieldbackground=palette["tree_field_bg"],
                        background=palette["tree_bg"],
                        foreground=palette["tree_fg"],
                        rowheight=24)
        style.configure("LabelFrame", background=palette["bg"], foreground=palette["fg"])

        # Apply to CustomTkinter components
        self.form.configure(bg=palette["bg"])
        self.form.set_theme(palette)
        self.header.set_theme(palette)
        self.password_table.set_theme(palette)
        self.generate_password.set_theme(palette)



if __name__ == "__main__":
    App().mainloop()
