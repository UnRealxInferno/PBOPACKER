#!/usr/bin/env bash
# install.sh – Install PBO Packer and the KDE Dolphin service menu.
#
# Supports Fedora/Nobara Linux (KDE Plasma 5 and 6) and any
# other Linux distribution that uses Dolphin as the file manager.
#
# After installation:
#   • Run 'pbopacker <folder>' from any terminal.
#   • Right-click a folder in Dolphin → "Pack as PBO".

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── 1. Install the packer scripts ────────────────────────────────────────────
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"
install -m 755 "$SCRIPT_DIR/pbopacker.py" "$BIN_DIR/pbopacker"
echo "✔  Installed pbopacker → $BIN_DIR/pbopacker"

# GUI launcher (requires python3-tkinter)
install -m 755 "$SCRIPT_DIR/pbopacker_gui.py" "$BIN_DIR/pbopacker-gui"
echo "✔  Installed pbopacker-gui → $BIN_DIR/pbopacker-gui"

# Check for tkinter (optional – GUI will warn at runtime if missing)
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo ""
    echo "ℹ  tkinter not found. To use the GUI run:"
    echo "     sudo dnf install python3-tkinter   # Fedora/Nobara"
fi

# ── 2. Install the Dolphin service menu ──────────────────────────────────────
# KDE 6 location
KDE6_DIR="$HOME/.local/share/kio/servicemenus"
mkdir -p "$KDE6_DIR"
install -m 644 "$SCRIPT_DIR/pack_pbo.desktop" "$KDE6_DIR/pack_pbo.desktop"
echo "✔  Installed Dolphin service menu (KDE 6) → $KDE6_DIR/pack_pbo.desktop"

# KDE 5 compatibility location
KDE5_DIR="$HOME/.local/share/kservices5/ServiceMenus"
mkdir -p "$KDE5_DIR"
install -m 644 "$SCRIPT_DIR/pack_pbo.desktop" "$KDE5_DIR/pack_pbo.desktop"
echo "✔  Installed Dolphin service menu (KDE 5) → $KDE5_DIR/pack_pbo.desktop"

# ── 3. PATH reminder ─────────────────────────────────────────────────────────
if [[ ":${PATH}:" != *":${BIN_DIR}:"* ]]; then
    echo ""
    echo "⚠  $BIN_DIR is not in your PATH."
    echo "   Add the following line to your ~/.bashrc or ~/.zshrc and restart your shell:"
    echo ""
    echo "     export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

# ── 4. Notify the user ───────────────────────────────────────────────────────
echo ""
echo "Installation complete!"
echo ""
echo "Usage (terminal):"
echo "  pbopacker <folder>                 # creates <folder>.pbo next to the folder"
echo "  pbopacker <folder> -o output.pbo   # explicit output path"
echo "  pbopacker <folder> -p z\\my_mod    # explicit PBO prefix"
echo "  pbopacker --help                   # full help"
echo ""
echo "  pbopacker-gui                      # launch the graphical interface"
echo ""
echo "Usage (Dolphin):"
echo "  Right-click a folder → 'Pack as PBO'"
echo ""
echo "  If the context menu entry does not appear yet, restart Dolphin:"
echo "    dolphin --quit && dolphin &"
