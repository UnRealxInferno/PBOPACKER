#!/usr/bin/env python3
"""PBO Packer GUI - Simple graphical interface for pbopacker.

Requires Python 3.6+ and tkinter.
On Fedora/Nobara:  sudo dnf install python3-tkinter
"""

import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path

# Allow running as a standalone script next to pbopacker.py
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from pbopacker import pack_folder  # noqa: E402


class PBOPackerApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("PBO Packer")
        self.resizable(False, False)
        self._packing = False
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._build_ui()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        pad = {"padx": 8, "pady": 4}

        # Source folder row
        tk.Label(self, text="Source folder:", anchor="w").grid(
            row=0, column=0, sticky="w", **pad)
        self._folder_var = tk.StringVar()
        tk.Entry(self, textvariable=self._folder_var, width=48).grid(
            row=0, column=1, sticky="ew", **pad)
        tk.Button(self, text="Browse…", command=self._browse_folder).grid(
            row=0, column=2, **pad)

        # Output file row
        tk.Label(self, text="Output file:", anchor="w").grid(
            row=1, column=0, sticky="w", **pad)
        self._output_var = tk.StringVar()
        tk.Entry(self, textvariable=self._output_var, width=48).grid(
            row=1, column=1, sticky="ew", **pad)
        tk.Button(self, text="Browse…", command=self._browse_output).grid(
            row=1, column=2, **pad)
        tk.Label(self, text="(optional – defaults to <folder>.pbo)", font=("", 8),
                 fg="grey").grid(row=2, column=1, sticky="w", padx=8)

        # PBO prefix row
        tk.Label(self, text="PBO prefix:", anchor="w").grid(
            row=3, column=0, sticky="w", **pad)
        self._prefix_var = tk.StringVar()
        tk.Entry(self, textvariable=self._prefix_var, width=48).grid(
            row=3, column=1, sticky="ew", **pad)
        tk.Label(self, text="(optional – e.g. z\\my_mod)", font=("", 8),
                 fg="grey").grid(row=4, column=1, sticky="w", padx=8)

        # Pack button
        self._pack_btn = tk.Button(
            self, text="Pack PBO", command=self._on_pack,
            bg="#2a6496", fg="white", font=("", 10, "bold"),
            padx=12, pady=4,
        )
        self._pack_btn.grid(row=5, column=0, columnspan=3, pady=8)

        # Log / status area
        tk.Label(self, text="Log:", anchor="w").grid(
            row=6, column=0, sticky="nw", **pad)
        self._log = scrolledtext.ScrolledText(
            self, width=58, height=8, state="disabled",
            font=("Monospace", 9),
        )
        self._log.grid(row=6, column=1, columnspan=2, **pad)

        self.columnconfigure(1, weight=1)

    # ── Window close ─────────────────────────────────────────────────────────

    def _on_close(self):
        if self._packing:
            messagebox.showwarning(
                "Packing in progress",
                "Please wait for packing to finish before closing.",
            )
            return
        self.destroy()

    # ── Browse helpers ────────────────────────────────────────────────────────

    def _browse_folder(self):
        path = filedialog.askdirectory(title="Select folder to pack")
        if path:
            self._folder_var.set(path)
            # Auto-fill output if it's still empty
            if not self._output_var.get():
                self._output_var.set(str(Path(path).parent / (Path(path).name + ".pbo")))

    def _browse_output(self):
        path = filedialog.asksaveasfilename(
            title="Save PBO as…",
            defaultextension=".pbo",
            filetypes=[("PBO files", "*.pbo"), ("All files", "*")],
        )
        if path:
            self._output_var.set(path)

    # ── Packing logic ─────────────────────────────────────────────────────────

    def _log_append(self, text: str):
        self._log.configure(state="normal")
        self._log.insert("end", text + "\n")
        self._log.see("end")
        self._log.configure(state="disabled")

    def _on_pack(self):
        folder_str = self._folder_var.get().strip()
        if not folder_str:
            messagebox.showerror("Error", "Please select a source folder.")
            return

        folder_path = Path(folder_str).resolve()
        if not folder_path.is_dir():
            messagebox.showerror("Error", f"Not a directory:\n{folder_path}")
            return

        output_str = self._output_var.get().strip()
        output_path = (
            Path(output_str) if output_str
            else folder_path.parent / (folder_path.name + ".pbo")
        )

        prefix = self._prefix_var.get().strip() or None

        self._pack_btn.configure(state="disabled", text="Packing…")
        self._log_append(f"Packing: {folder_path}")
        self._log_append(f"Output:  {output_path}")
        self._packing = True

        def _worker():
            try:
                pack_folder(folder_path, output_path, prefix)
                self.after(0, lambda op=output_path: self._on_done(op, error=None))
            except Exception as exc:
                self.after(0, lambda op=output_path, e=exc: self._on_done(op, error=e))

        threading.Thread(target=_worker, daemon=False).start()

    def _on_done(self, output_path: Path, error):
        self._packing = False
        self._pack_btn.configure(state="normal", text="Pack PBO")
        if error:
            self._log_append(f"ERROR: {error}")
            messagebox.showerror("Pack failed", str(error))
        else:
            self._log_append(f"Done: {output_path}")
            messagebox.showinfo("Success", f"Created:\n{output_path}")


def main():
    app = PBOPackerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
