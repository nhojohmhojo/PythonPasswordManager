"""
Description: generate_password.py - Custom Component Class GeneratePassword.
"""
import secrets
import string
import tkinter as tk
import customtkinter as ctk
import pyperclip

# Custom Component Class GeneratePassword
class GeneratePassword(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        # Create Widgets
        self.generated_password = ctk.CTkEntry(self)
        self.button = ctk.CTkButton(self, text="Generate Password", command=lambda: self.generate_password(self.length_label.cget("text"), self.numbers_checkbox_var.get(), self.special_characters_checkbox_var.get()))
        self.slider = ctk.CTkSlider(self, from_=3, to=50, command=self.sliding)
        self.slider.set(16)
        self.length_label = ctk.CTkLabel(self, text=int(self.slider.get()))
        self.numbers_checkbox_var = tk.BooleanVar(value=True)
        self.numbers_checkbox = ctk.CTkCheckBox(self, text="Numbers", variable=self.numbers_checkbox_var, onvalue=True, offvalue=False)
        self.special_characters_checkbox_var = tk.BooleanVar(value=True)
        self.special_characters_checkbox = ctk.CTkCheckBox(self, text="Special", variable=self.special_characters_checkbox_var, onvalue=True, offvalue=False)
        self.copy_button = ctk.CTkButton(self, text="Copy", width=60, command=lambda: pyperclip.copy(self.generated_password.get()))
        # Place
        self.generated_password.pack(pady=10)
        self.button.pack()
        self.length_label.pack()
        self.slider.pack()
        self.numbers_checkbox.pack(pady=5)
        self.special_characters_checkbox.pack(pady=5)
        self.copy_button.pack(pady=5)


    def sliding(self, value):
        self.length_label.configure(text=int(value))

    def generate_password(self, min_length, numbers, special_characters):
        min_length = int(min_length)
        letters = string.ascii_letters
        digits = string.digits
        special = string.punctuation

        pool = letters
        if numbers:
            pool += digits
        if special_characters:
            pool += special

        password = ""
        meets_criteria = False
        has_number = False
        has_special = False

        while not meets_criteria or len(password) < min_length:
            new_char = secrets.choice(pool)
            password += new_char

            if new_char in digits:
                has_number = True
            elif new_char in special:
                has_special = True

            meets_criteria = True
            if numbers:
                meets_criteria = has_number
            if special_characters:
                meets_criteria = meets_criteria and has_special

        password = list(password)
        secrets.SystemRandom().shuffle(password)
        password = "".join(password[:min_length])

        self.generated_password.delete(0, "end")
        self.generated_password.insert(0, password)

    def set_theme(self, palette):
        self.configure(bg_color=palette["bg"])
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkLabel):
                widget.configure(text_color=palette["fg"])