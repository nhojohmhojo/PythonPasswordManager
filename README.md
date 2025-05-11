# 🛡️ Python Password Manager
A GUI built with Python for Password management.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.html)
[![GUI: CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-lightgrey)](https://github.com/TomSchimansky/CustomTkinter)

A secure and elegant desktop password manager built with Python and CustomTkinter. Designed for local, offline use — with encryption, dark/light themes, a built-in password generator, and CSV import support.

---

## 🚀 Features

- 🔍 **Search**: View entries in a sortable table
- 🔒 **Secure Storage**: All passwords are encrypted with Fernet (AES-based)
- 📁 **CSV Upload**: Import large sets of credentials with ease
- 🛠️ **Built-in Generator**: Quickly create strong, random passwords
- 🌓 **Light/Dark Mode**: Instant toggle built into the interface
- 💾 **Offline-Only**: No network access, your data stays with you
- 📦 **Cross-platform Support**: Comes with build scripts that uses PyInstaller for compiling on Windows, macOS, and Linux

---

## 📷 Screenshots
<img width="302" alt="Screenshot - Register" src="https://github.com/user-attachments/assets/f574045b-794a-41a8-a2ec-209993c181d4" />
<img width="227" alt="Screenshot - Login" src="https://github.com/user-attachments/assets/c9a363a6-0dfd-449c-ad03-a1fae01c4630" />
<img width="415" alt="Screenshot - Password Manager - v0 0 1" src="https://github.com/user-attachments/assets/a11b780c-3a51-4907-8708-aa15116a7a8c" />

---

## 🧰 Installation
## 🧰 Build & Run as Executable

This project includes platform-specific build scripts using **PyInstaller**. They generate both a `dist/` version and a renamed copy in the **project root** for easy access.

| Platform     | Script                | Output Executable(s)                                               | Run Command                             |
|--------------|------------------------|----------------------------------------------------------------------|------------------------------------------|
| 🪟 Windows    | `WindowsInstall.bat`   | `dist/register_user.exe` and `Python Password Manager.exe` (root)   | `start "" "Python Password Manager.exe"` |
| 🍎 macOS      | `MacOSInstall.sh`      | `dist/PythonPasswordManager.app` and copy in root                   | `open PythonPasswordManager.app`         |
| 🐧 Linux      | `UbuntuLinuxInstall.sh`| `dist/register_user` and copy in root                               | `./register_user`                        |


### ✅ Each script will:

- Check for or create a virtual environment
- Install all dependencies from `requirements.txt`
- Use `pyinstaller` to build an executable (`.exe`,`.app` or `.bin`)
- Move or rename the build result to the project root for convenience
-
### Note ###
- The macOS Script has not been tested and I am unaware of any potential errors. 
- If you are compiling on Ubuntu Linux, these scripts were written on a Windows machine, the editor may have saved it with Windows-style line endings ('s/\r$//').
- Quick Fix:
  ```bash
  sudo apt install dos2unix
  dos2unix UbuntuLinuxInstall.sh
  ```

---

## 🧪 Development Setup (Optional)

To run directly from source:

```bash
git clone https://github.com/yourusername/PythonPasswordManager.git
cd PythonPasswordManager

python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

pip install -r requirements.txt
python register_user.py
```

---

### ✅ Requirements

- Python 3.9 or higher
- pip

---
