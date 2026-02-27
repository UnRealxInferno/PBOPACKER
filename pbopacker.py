#!/usr/bin/env python3
"""PBO Packer - Creates .pbo files for Arma 3 from folders.

Supports Fedora/Nobara Linux and any other Linux distribution with Python 3.

PBO format reference: https://community.bistudio.com/wiki/PBO_File_Format
"""

import os
import sys
import struct
import hashlib
import argparse
from pathlib import Path

# PBO version/product entry magic (little-endian 0x56657273 = "sreV" bytes = "Vers" conceptually)
_VERS_MAGIC = 0x56657273
# Uncompressed packing method
_PACK_UNCOMPRESSED = 0x00000000


def _read_prefix(folder_path: Path) -> str:
    """Return the PBO prefix: read from $PBOPREFIX$ file, falling back to folder name."""
    pboprefix_file = folder_path / "$PBOPREFIX$"
    if pboprefix_file.exists():
        return pboprefix_file.read_text(encoding="utf-8", errors="replace").strip()
    return folder_path.name


def _encode_entry(filename: str, packing: int, orig_size: int,
                  reserved: int, timestamp: int, data_size: int) -> bytes:
    """Return the 21+ byte PBO entry header for one file."""
    return (
        filename.encode("ascii", errors="replace") + b"\x00"
        + struct.pack("<IIIII", packing, orig_size, reserved, timestamp, data_size)
    )


def pack_folder(folder_path: Path, output_path: Path, prefix: str = None) -> None:
    """Pack *folder_path* into a PBO file at *output_path*.

    Args:
        folder_path: Source directory to pack.
        output_path: Destination .pbo file path.
        prefix: Override the PBO prefix; defaults to the value in $PBOPREFIX$
                or the folder name.
    """
    folder_path = folder_path.resolve()

    if prefix is None:
        prefix = _read_prefix(folder_path)

    # Collect files (deterministic order: directories and filenames sorted)
    files: list[tuple[str, Path]] = []
    for root, dirs, filenames in os.walk(folder_path):
        dirs.sort()
        for name in sorted(filenames):
            # $PBOPREFIX$ is metadata — exclude from the archive
            if name == "$PBOPREFIX$":
                continue
            filepath = Path(root) / name
            rel = filepath.relative_to(folder_path)
            # PBO paths use backslashes
            pbo_path = str(rel).replace("/", "\\")
            files.append((pbo_path, filepath))

    hasher = hashlib.sha1()

    with open(output_path, "wb") as f:

        def _write(data: bytes) -> None:
            hasher.update(data)
            f.write(data)

        # ── Version / properties entry ────────────────────────────────────
        _write(_encode_entry("", _VERS_MAGIC, 0, 0, 0, 0))
        # Properties: prefix key=value pair, terminated by an empty key
        if prefix:
            _write(b"prefix\x00" + prefix.encode("ascii", errors="replace") + b"\x00")
        _write(b"\x00")  # empty key = end of properties

        # ── File entry headers ────────────────────────────────────────────
        for pbo_path, filepath in files:
            stat = filepath.stat()
            size = stat.st_size
            ts = int(stat.st_mtime)
            _write(_encode_entry(pbo_path, _PACK_UNCOMPRESSED, size, 0, ts, size))

        # ── Boundary (empty) entry ────────────────────────────────────────
        _write(_encode_entry("", 0, 0, 0, 0, 0))

        # ── File data ────────────────────────────────────────────────────
        for _pbo_path, filepath in files:
            _write(filepath.read_bytes())

        # ── SHA-1 checksum ───────────────────────────────────────────────
        # The leading 0x00 byte and the digest itself are NOT hashed.
        f.write(b"\x00")
        f.write(hasher.digest())

    print(f"Created: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="pbopacker",
        description="Pack a folder into an Arma 3 PBO file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  pbopacker my_mission          # creates my_mission.pbo next to the folder\n"
            "  pbopacker my_mod -o out.pbo   # explicit output path\n"
            "  pbopacker my_mod -p z\\my_mod  # explicit prefix\n"
        ),
    )
    parser.add_argument("folder", help="folder to pack into a PBO")
    parser.add_argument(
        "-o", "--output",
        help="output PBO file path (default: <folder>.pbo alongside the source folder)",
    )
    parser.add_argument(
        "-p", "--prefix",
        help="PBO prefix override (default: content of $PBOPREFIX$ file, or folder name)",
    )

    args = parser.parse_args()

    folder_path = Path(args.folder).resolve()
    if not folder_path.is_dir():
        print(f"error: '{args.folder}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = folder_path.parent / (folder_path.name + ".pbo")

    pack_folder(folder_path, output_path, args.prefix)


if __name__ == "__main__":
    main()
