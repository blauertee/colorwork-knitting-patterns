#!/bin/bash

# Configurable variables
SCRIPT_NAME="grid_pixelate_tool.py"
DEPENDENCIES=(pillow scikit-learn)

APP_NAME="Colorwork Pattern Generator"

USER_HOME=$(eval echo ~$SUDO_USER)
INSTALL_DIR="${USER_HOME:-$HOME}/.local/colorwork_pattern_generator"
DESKTOP_FILE="${USER_HOME:-$HOME}/.local/share/applications/colorwork_pattern_generator.desktop"
VENV_DIR="$INSTALL_DIR/env"

# Uninstall if first argument is "uninstall"
if [ "$1" == "uninstall" ]; then
    echo "Uninstalling $APP_NAME..."
    rm -rf "$INSTALL_DIR"
    rm -f "$DESKTOP_FILE"
    echo "Uninstallation complete."
    exit 0
fi

# Check if running on a system with apt and .desktop support
if ! command -v apt &> /dev/null || [ ! -d "/usr/share/applications" ]; then
    echo "This script is intended for Debian-based distributions with .desktop support. Exiting."
    exit 1
fi

# Ensure required package is installed
if ! dpkg -l | grep -q python3-venv; then
    echo "Installing python3-venv..."
    sudo apt update && sudo apt install -y python3-venv python3-tk 
fi

# Create installation directory
mkdir -p "$INSTALL_DIR"
mkdir -p "$USER_HOME/.local/share/applications"

# Set up virtual environment
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install "${DEPENDENCIES[@]}"
deactivate

# Move script to install directory
cp "$SCRIPT_NAME" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/$SCRIPT_NAME"

# Create .desktop entry
cat > "$DESKTOP_FILE" <<EOL
[Desktop Entry]
Type=Application
Name=$APP_NAME
Exec=$VENV_DIR/bin/python3 $INSTALL_DIR/$SCRIPT_NAME
Icon=applications-other
Terminal=false
Categories=Utility;
EOL

chmod +x "$DESKTOP_FILE"

echo "Installation complete. You can launch the app from your applications menu."

