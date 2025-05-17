#!/bin/bash
# To use this script:
# 1. Run: chmod +x build_mac_app.sh
# 2. Then: ./build_mac_app.sh

# === CONFIG ===
APP_NAME="Python Password Manager"
ENTRY_SCRIPT="register.py"
ICON_PATH="images/password_icon.icns"
VENV_DIR="venv"
DIST_DIR="dist"
BUILD_DIR="build"
EXE_NAME="register"
APP_BUNDLE="$APP_NAME.app"

# === Check: Warn if not executable ===
if [ ! -x "$0" ]; then
  echo ⚠️ This script must be executable. Run:"
  echo "chmod +x $0"
  exit 1
fi

# === STEP 1: Go to script dir ===
cd "$(dirname "$0")"

# === STEP 2: Set up virtual environment ===
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

# === STEP 3: Install dependencies ===
echo "⬇️ Installing Python packages..."
pip install -r requirements.txt

# === STEP 4: Clean old builds ===
echo "🧹 Cleaning previous builds..."
rm -rf "$DIST_DIR" "$BUILD_DIR" *.spec "$APP_BUNDLE"

# === STEP 5: Build executable ===
echo "⚙️ Building standalone app with PyInstaller..."
pyinstaller --onefile --windowed --icon "$ICON_PATH" "$ENTRY_SCRIPT"

# === STEP 6: Create .app bundle ===
echo "📦 Packaging into .app bundle..."
mkdir -p "$APP_BUNDLE/Contents/MacOS"
mkdir -p "$APP_BUNDLE/Contents/Resources"

cp "$DIST_DIR/$EXE_NAME" "$APP_BUNDLE/Contents/MacOS/$APP_NAME"
cp "$ICON_PATH" "$APP_BUNDLE/Contents/Resources/AppIcon.icns"
chmod +x "$APP_BUNDLE/Contents/MacOS/$APP_NAME"

# === STEP 7: Write Info.plist ===
cat > "$APP_BUNDLE/Contents/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>$APP_NAME</string>
    <key>CFBundleDisplayName</key>
    <string>$APP_NAME</string>
    <key>CFBundleIdentifier</key>
    <string>com.example.$(echo $APP_NAME | tr ' ' '')</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleExecutable</key>
    <string>$APP_NAME</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

# === STEP 8: Launch App ===
echo "🚀 Launching your .app bundle..."
open "$APP_BUNDLE"

echo "✅ Done! App is ready: $APP_BUNDLE"
