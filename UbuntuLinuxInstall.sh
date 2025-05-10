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
BUILD_BIN="$DIST_DIR/$BUILD_NAME"
FINAL_BIN="$SCRIPT_DIR/$APP_NAME"

echo "▶ Starting Linux build for: $APP_NAME"

# ――― 1. Clean old builds
echo "🧹 Cleaning previous builds..."
rm -rf "$DIST_DIR" "$BUILD_DIR" "$SPEC_FILE" "$SCRIPT_DIR/__pycache__"
find . -name '__pycache__' -type d -exec rm -rf {} +
rm -f "$FINAL_BIN"

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

# ――― 5. Compile project with PyInstaller (with PIL hidden imports)
echo "🛠️ Compiling project with PyInstaller..."
pyinstaller --onefile --windowed \
  --hidden-import=PIL._tkinter_finder \
  --hidden-import=PIL.ImageTk \
  "$ENTRY_SCRIPT"

# ――― 6. Copy and rename binary
if [ -f "$BUILD_BIN" ]; then
  cp "$BUILD_BIN" "$FINAL_BIN"
  chmod +x "$FINAL_BIN"
  echo "✅ Final binary created: $FINAL_BIN"
else
  echo "❌ Build failed. No binary found at $BUILD_BIN"
  exit 1
fi

# ――― 7. Run the final binary
echo "🚀 Launching the app..."
"./$APP_NAME" &

echo "🎉 Linux build complete and app launched."
