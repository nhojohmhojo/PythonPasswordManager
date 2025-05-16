#!/bin/bash
# To use this script:
# 1. Run: chmod +x build_linux_app.sh
# 2. Then: ./build_linux_app.sh

# === CONFIG ===
APP_NAME="Python Password Manager"
ENTRY_SCRIPT="register_user.py"
ICON_PATH="images/password_image.png"   # PNG for Linux desktop files
VENV_DIR="venv"
DIST_DIR="dist"
BUILD_DIR="build"
EXE_NAME="register_user"
EXECUTABLE="$DIST_DIR/$EXE_NAME"
DESKTOP_FILE="$HOME/Desktop/$APP_NAME.desktop"

# === STEP 1: Go to script dir ===
cd "$(dirname "$0")"

# === STEP 2: Create virtual environment ===
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

# === STEP 3: Install dependencies ===
echo "⬇️ Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# === STEP 4: Clean previous builds ===
echo "🧹 Cleaning old builds..."
rm -rf "$DIST_DIR" "$BUILD_DIR" *.spec
rm -f "$APP_NAME" "$DESKTOP_FILE"

# === STEP 5: Build the app ===
echo "⚙️ Building with PyInstaller..."
pyinstaller --onefile --windowed --icon "$ICON_PATH" "$ENTRY_SCRIPT"

# === STEP 6: Rename binary ===
if [ -f "$EXECUTABLE" ]; then
    mv "$EXECUTABLE" "./$APP_NAME"
    chmod +x "$APP_NAME"
    echo "✅ App built: $APP_NAME"
else
    echo "❌ Build failed."
    exit 1
fi

# === STEP 7: Create .desktop launcher ===
echo "🖥️ Creating desktop shortcut..."
cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=$APP_NAME
Exec=$(pwd)/$APP_NAME
Icon=$(pwd)/$ICON_PATH
Terminal=false
Categories=Utility;
EOF

chmod +x "$DESKTOP_FILE"

# === STEP 8: Launch the app ===
echo "🚀 Launching the app..."
"./$APP_NAME"

echo "✅ Done! Shortcut placed at: $DESKTOP_FILE"
