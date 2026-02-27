# PBOPACKER

A lightweight tool for creating `.pbo` files for **Arma 3** from folders.
Designed for **Fedora/Nobara Linux** (KDE Plasma 5 & 6) with a one-click
Dolphin right-click context menu option.

## Requirements

- Python 3.6 or newer (pre-installed on Fedora/Nobara)
- `tkinter` for the GUI — install once if missing:
  ```bash
  sudo dnf install python3-tkinter   # Fedora / Nobara
  ```
- KDE Dolphin (for the right-click service menu)

## Installation

```bash
git clone https://github.com/UnRealxInferno/PBOPACKER.git
cd PBOPACKER
bash install.sh
```

The installer:
1. Copies `pbopacker` to `~/.local/bin/pbopacker`
2. Installs the Dolphin service menu for KDE 6 (`~/.local/share/kio/servicemenus/`)
3. Installs the Dolphin service menu for KDE 5 (`~/.local/share/kservices5/ServiceMenus/`)

If `~/.local/bin` is not already in your `PATH`, add this to `~/.bashrc` or `~/.zshrc`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Then restart Dolphin if it is already running:

```bash
dolphin --quit && dolphin &
```

## Usage

### GUI (graphical interface)

Run `pbopacker-gui` from a terminal, or double-click the installed launcher:

```bash
pbopacker-gui
```

A window opens with:
- **Source folder** — browse-button to pick the folder to pack
- **Output file** — optional; defaults to `<folder>.pbo` next to the source folder
- **PBO prefix** — optional; e.g. `z\my_mod`
- **Pack PBO** button — packs the folder and shows a success/error notification
- **Log** area — shows progress and any errors

### Terminal

```bash
# Pack a folder – output goes next to the folder as <folder>.pbo
pbopacker my_mission

# Explicit output path
pbopacker my_mod -o ~/Arma3Mods/my_mod.pbo

# Override the PBO prefix
pbopacker my_mod -p z\my_mod

# Full help
pbopacker --help
```

### Dolphin (right-click)

Right-click any folder in Dolphin → **Pack as PBO**.

A desktop notification appears when the `.pbo` file has been created
(or if an error occurred). The output file is placed next to the
source folder with a `.pbo` extension.

## PBO Prefix

The PBO prefix determines how Arma 3 locates files inside the addon.
`pbopacker` resolves the prefix in this order:

1. The `--prefix` / `-p` command-line argument (if provided)
2. A `$PBOPREFIX$` file in the root of the folder (text file containing
   the prefix, e.g. `z\my_mod`)
3. The folder name itself (fallback)

## File Structure

```
PBOPACKER/
├── pbopacker.py       # Main packing script (Python 3)
├── pbopacker_gui.py   # Graphical interface (tkinter)
├── pack_pbo.desktop   # KDE Dolphin service menu
├── install.sh         # Installer script
└── README.md
```

## PBO Format

PBO files are the standard Arma 3 addon/mission archive format.
Each `.pbo` contains:

- A **version entry** with optional key/value properties (including the prefix)
- A **file entry header** for every file in the archive
- A **boundary entry** (all-zero) ending the header section
- The raw **file data** concatenated in the same order
- A trailing **SHA-1 checksum** over all preceding bytes

Reference: <https://community.bistudio.com/wiki/PBO_File_Format>
