#!/bin/bash

# ――― Basic Setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

APP_NAME="Python Password Manager"
ENTRY_SCRIPT="register_user.py"
VENV="$SCRIPT_DIR/venv"
DIST_DIR="$SCRIPT_DIR/dist"
BUILD_DIR="$SCRIPT_DIR/build"
SPEC_FILE="$SCRIPT_DIR/${ENTRY_SCRIPT%.py}.spec"
BUILD_NAME="${ENTRY_SCRIPT%.py}"
APP_BUNDLE="$DIST_DIR/$BUILD_NAME.app"
FINAL_APP="$SCRIPT_DIR/$APP_NAME.app"

echo "▶ Starting macOS build for: $APP_NAME"

# ――― 1. Clean old builds
echo "🧹 Cleaning previous builds..."
rm -rf "$DIST_DIR" "$BUILD_DIR" "$SPEC_FILE" "$SCRIPT_DIR/__pycache__"
find . -name '__pycache__' -type d -exec rm -rf {} +
rm -rf "$FINAL_APP"

# ――― 2. Create virtual environment if needed
if [ ! -d "$VENV" ]; then
  echo "🔧 Creating virtual environment..."
  python3 -m venv "$VENV"
  if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment."
    exit 1
  fi
fi

# ――― 3. Activate virtual environment
source "$VENV/bin/activate"
echo "✅ Virtual environment activated."

# ――― 4. Install dependencies
if [ ! -f requirements.txt ]; then
  echo "❌ requirements.txt not found in project root."
  exit 1
fi

echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# ――― 5. Compile project with PyInstaller for macOS
echo "🛠️ Compiling macOS .app with PyInstaller..."
pyinstaller --windowed \
  --hidden-import=PIL._tkinter_finder \
  --hidden-import=PIL.ImageTk \
  "$ENTRY_SCRIPT"

# ――― 6. Copy and rename .app bundle
if [ -d "$APP_BUNDLE" ]; then
  cp -R "$APP_BUNDLE" "$FINAL_APP"
  echo "✅ Final app created: $FINAL_APP"
else
  echo "❌ Build failed. No .app bundle found at $APP_BUNDLE"
  exit 1
fi

# ――― 7. Launch the app
echo "🚀 Launching the app..."
open "$FINAL_APP"

echo "🎉 macOS build complete and app launched."
