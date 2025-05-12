#!/bin/bash

# ――― Make script self-executable if needed
if [ ! -x "$0" ]; then
  echo "❌ Script not executable. Fixing permissions..."
  chmod +x "$0"
  echo "✅ Permissions fixed. Please re-run:"
  echo "./$(basename "$0")"
  exit 0
fi

# ――― Setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

APP_NAME="Python Password Manager"
ENTRY_SCRIPT="register_user.py"
ICON_FILE="icon.png"
ICON_URL="https://cdn-icons-png.flaticon.com/512/2889/2889676.png"
VENV="$SCRIPT_DIR/venv"
ACTIVATE="$VENV/bin/activate"
DIST_DIR="$SCRIPT_DIR/dist"
BUILD_DIR="$SCRIPT_DIR/build"
BUILD_NAME="${ENTRY_SCRIPT%.py}"
BUILD_BIN="$DIST_DIR/$BUILD_NAME"
FINAL_BIN="$SCRIPT_DIR/$APP_NAME"
DESKTOP_FILE="$HOME/Desktop/$APP_NAME.desktop"

echo "▶ Starting Linux build for: $APP_NAME"

# ――― 1. Clean old builds
echo "🧹 Cleaning previous builds..."
rm -rf "$DIST_DIR" "$BUILD_DIR" "$SCRIPT_DIR/__pycache__"
find . -name '__pycache__' -type d -exec rm -rf {} +
rm -f "$FINAL_BIN"

# ――― 2. Create virtual environment if needed
if [ ! -d "$VENV" ]; then
  echo "🔧 Creating virtual environment..."
  python3 -m venv "$VENV"
fi

# ――― 3. Activate virtual environment
source "$ACTIVATE"
echo "✅ Virtual environment activated."

# ――― 4. Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# ――― 5. Install PyInstaller if not present
if [ ! -f "$VENV/bin/pyinstaller" ]; then
  echo "📦 Installing PyInstaller..."
  pip install pyinstaller
fi

# ――― 6. Download icon.png if missing
if [ ! -f "$ICON_FILE" ]; then
  echo "🎨 Downloading icon..."
  curl -L -o "$ICON_FILE" "$ICON_URL"
  if [ $? -ne 0 ]; then
    echo "❌ Failed to download icon."
    exit 1
  fi
fi

# ――― 7. Build Linux executable
echo "🛠️ Building Linux executable..."
"$VENV/bin/pyinstaller" --onefile --windowed --icon="$ICON_FILE" "$ENTRY_SCRIPT"

# ――― 8. Copy and rename Linux binary
if [ -f "$BUILD_BIN" ]; then
  cp "$BUILD_BIN" "$FINAL_BIN"
  chmod +x "$FINAL_BIN"
  echo "✅ Final binary created: $FINAL_BIN"
else
  echo "❌ Build failed. No binary found at $BUILD_BIN"
  exit 1
fi

# ――― 9. Create .desktop launcher
echo "📎 Creating desktop launcher..."
cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=$APP_NAME
Exec=$FINAL_BIN
Icon=$SCRIPT_DIR/$ICON_FILE
Terminal=false
EOF

chmod +x "$DESKTOP_FILE"
echo "✅ Launcher created: $DESKTOP_FILE"

echo "🎉 Linux build complete."
