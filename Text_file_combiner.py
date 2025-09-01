"""
Text Combiner (Tkinter)

Quick Start
- Run: `python app.py`
- Add files or a folder of .txt files (optionally include subfolders).
- Choose an output file, pick options, then click Combine.

Features
- Multi-select .txt files and folder scan (with optional recursion).
- Deduplicates files by absolute path; preserves add order.
- Options: add filename headers, custom separator, encoding choice.
- Responsive UI with progress indicator; safe error handling.

Notes
- Reading encodings: "UTF-8 (replace errors)" reads with errors replaced; "Latin-1" reads byte-for-byte.
- Output file encoding: UTF-8.
- Separator entry supports escapes like \n, \t, \r (e.g., "\n\n" for a blank line).
"""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from pathlib import Path
from typing import Iterable, List, Tuple
import os
import sys


ENCODING_OPTIONS = (
    "UTF-8 (replace errors)",
    "Latin-1",
)


def unescape_separators(text: str) -> str:
    """Interpret common backslash escapes in a small, safe way.

    Supports: \n, \r, \t, \\\n+    Other sequences remain as-is.
    """
    out = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "\\" and i + 1 < len(text):
            nxt = text[i + 1]
            if nxt == "n":
                out.append("\n")
                i += 2
                continue
            if nxt == "r":
                out.append("\r")
                i += 2
                continue
            if nxt == "t":
                out.append("\t")
                i += 2
                continue
            if nxt == "\\":
                out.append("\\")
                i += 2
                continue
        out.append(ch)
        i += 1
    return "".join(out)


def scan_txt_files(folder: Path, recursive: bool) -> List[Path]:
    """Return a list of .txt files under folder. Case-insensitive extension.

    If recursive is True, walks subfolders; otherwise scans only the top level.
    Returned list is sorted by path for predictability.
    """
    folder = folder.resolve()
    results: List[Path] = []
    if not folder.exists() or not folder.is_dir():
        return results
    if recursive:
        for root, _dirs, files in os.walk(folder):
            root_path = Path(root)
            for name in files:
                if name.lower().endswith(".txt"):
                    results.append((root_path / name).resolve())
    else:
        for p in folder.iterdir():
            if p.is_file() and p.name.lower().endswith(".txt"):
                results.append(p.resolve())
    # Sort for stable ordering
    results.sort(key=lambda p: str(p).lower())
    return results


def _read_file_text(path: Path, encoding_label: str) -> str:
    """Read a file as text according to selected encoding policy.

    - UTF-8 (replace errors): encoding="utf-8", errors="replace"
    - Latin-1: encoding="latin-1"
    Normalizes line endings to "\n".
    """
    if encoding_label.startswith("UTF-8"):
        enc = "utf-8"
        errors = "replace"
    else:
        enc = "latin-1"
        errors = "strict"
    with path.open("r", encoding=enc, errors=errors, newline=None) as f:
        text = f.read()
    # newline=None already converts to \n, but normalize explicitly for safety
    return text.replace("\r\n", "\n").replace("\r", "\n")


def combine_files(
    files: List[Path],
    output: Path,
    encoding_label: str,
    add_headers: bool,
    separator: str,
) -> Tuple[int, int, List[Path]]:
    """Combine file contents into output.

    Returns (files_count_written, total_bytes_written, skipped_files).
    Output is always UTF-8 encoded.
    Skips files that don't exist or aren't readable.
    """
    count = 0
    total_bytes = 0
    skipped: List[Path] = []

    # Ensure parent directory exists
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as out_f:
        for idx, p in enumerate(files):
            try:
                if not p.exists() or not p.is_file():
                    skipped.append(p)
                    continue
                text = _read_file_text(p, encoding_label)
            except Exception:
                skipped.append(p)
                continue

            if add_headers:
                header = f"=== {p.name} ===\n"
                out_f.write(header)
                total_bytes += len(header.encode("utf-8"))

            out_f.write(text)
            total_bytes += len(text.encode("utf-8"))
            count += 1

            if idx != len(files) - 1 and separator:
                out_f.write(separator)
                total_bytes += len(separator.encode("utf-8"))

    return count, total_bytes, skipped


class TextCombinerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Text Combiner")
        self.geometry("820x540")
        self.minsize(720, 460)

        # State
        self.files: List[Path] = []
        self.files_index: set[str] = set()  # for fast dedupe (case-insensitive)
        self.last_dir: Path | None = None

        # Tk variables
        self.include_subfolders_var = tk.BooleanVar(value=True)
        self.add_headers_var = tk.BooleanVar(value=False)
        self.encoding_var = tk.StringVar(value=ENCODING_OPTIONS[0])
        self.separator_var = tk.StringVar(value="\\n")  # default to blank line via escape
        self.output_path_var = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="Ready")

        # Build UI
        self._build_widgets()
        self._bind_events()
        self._refresh_buttons()

    # UI construction
    def _build_widgets(self) -> None:
        pad = 8

        # Top controls: Add Files / Add Folder / Include subfolders
        top = ttk.Frame(self)
        top.pack(fill=tk.X, padx=pad, pady=(pad, 4))

        self.btn_add_files = ttk.Button(top, text="Add Files…", command=self.on_add_files)
        self.btn_add_files.pack(side=tk.LEFT)

        self.btn_add_folder = ttk.Button(top, text="Add Folder…", command=self.on_add_folder)
        self.btn_add_folder.pack(side=tk.LEFT, padx=(pad, 0))

        self.chk_recursive = ttk.Checkbutton(
            top, text="Include subfolders", variable=self.include_subfolders_var
        )
        self.chk_recursive.pack(side=tk.LEFT, padx=(pad, 0))

        # Middle: listbox + side buttons
        mid = ttk.Frame(self)
        mid.pack(fill=tk.BOTH, expand=True, padx=pad, pady=(4, 4))

        self.lst_files = tk.Listbox(
            mid,
            selectmode=tk.EXTENDED,
            activestyle="dotbox",
        )
        yscroll = ttk.Scrollbar(mid, orient=tk.VERTICAL, command=self.lst_files.yview)
        self.lst_files.configure(yscrollcommand=yscroll.set)

        self.lst_files.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")

        side = ttk.Frame(mid)
        side.grid(row=0, column=2, sticky="nsw", padx=(pad, 0))

        self.btn_remove = ttk.Button(side, text="Remove Selected", command=self.on_remove_selected)
        self.btn_clear = ttk.Button(side, text="Clear All", command=self.on_clear_all)
        self.btn_up = ttk.Button(side, text="Move Up", command=lambda: self.on_move(-1))
        self.btn_down = ttk.Button(side, text="Move Down", command=lambda: self.on_move(1))

        for b in (self.btn_remove, self.btn_clear, self.btn_up, self.btn_down):
            b.pack(fill=tk.X, pady=(0, 4))

        mid.columnconfigure(0, weight=1)
        mid.rowconfigure(0, weight=1)

        # Output + options area
        opts = ttk.LabelFrame(self, text="Output & Options")
        opts.pack(fill=tk.X, padx=pad, pady=(4, 4))

        # Output row
        out_row = ttk.Frame(opts)
        out_row.pack(fill=tk.X, padx=pad, pady=(pad, 0))
        ttk.Label(out_row, text="Output:").pack(side=tk.LEFT)
        self.entry_output = ttk.Entry(out_row, textvariable=self.output_path_var, state="readonly")
        self.entry_output.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(pad, pad))
        self.btn_output = ttk.Button(out_row, text="Choose Output…", command=self.on_choose_output)
        self.btn_output.pack(side=tk.LEFT)

        # Options row 1
        row1 = ttk.Frame(opts)
        row1.pack(fill=tk.X, padx=pad, pady=(pad, 0))
        self.chk_headers = ttk.Checkbutton(row1, text="Add filename headers", variable=self.add_headers_var)
        self.chk_headers.pack(side=tk.LEFT)

        ttk.Label(row1, text="Encoding:").pack(side=tk.LEFT, padx=(pad, 0))
        self.cmb_encoding = ttk.Combobox(row1, textvariable=self.encoding_var, values=ENCODING_OPTIONS, state="readonly", width=24)
        self.cmb_encoding.pack(side=tk.LEFT)

        # Options row 2
        row2 = ttk.Frame(opts)
        row2.pack(fill=tk.X, padx=pad, pady=(pad, pad))
        ttk.Label(row2, text="Separator (escapes ok):").pack(side=tk.LEFT)
        self.entry_separator = ttk.Entry(row2, textvariable=self.separator_var)
        self.entry_separator.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(pad, 0))
        ttk.Label(row2, text="e.g., \\n for blank line").pack(side=tk.LEFT, padx=(pad, 0))

        # Bottom: progress + combine + status
        bottom = ttk.Frame(self)
        bottom.pack(fill=tk.X, padx=pad, pady=(4, pad))

        self.progress = ttk.Progressbar(bottom, mode="indeterminate")
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.btn_combine = ttk.Button(bottom, text="Combine", command=self.on_combine)
        self.btn_combine.pack(side=tk.LEFT, padx=(pad, 0))

        self.lbl_status = ttk.Label(self, textvariable=self.status_var, anchor="w")
        self.lbl_status.pack(fill=tk.X, padx=pad, pady=(0, pad))

    def _bind_events(self) -> None:
        self.output_path_var.trace_add("write", lambda *_: self._refresh_buttons())
        self.separator_var.trace_add("write", lambda *_: self._refresh_buttons())
        self.encoding_var.trace_add("write", lambda *_: self._refresh_buttons())
        self.add_headers_var.trace_add("write", lambda *_: self._refresh_buttons())
        self.include_subfolders_var.trace_add("write", lambda *_: None)

        # Keyboard shortcuts
        self.bind("<Delete>", lambda e: self.on_remove_selected())
        self.bind("<Control-Up>", lambda e: self.on_move(-1))
        self.bind("<Control-Down>", lambda e: self.on_move(1))

    # State helpers
    def _index_key(self, p: Path) -> str:
        # Case-insensitive dedupe on Windows; case-sensitive elsewhere
        key = str(p.resolve())
        if os.name == "nt":
            key = key.lower()
        return key

    def _add_files(self, paths: Iterable[Path]) -> int:
        added = 0
        for p in paths:
            try:
                rp = p.resolve()
            except Exception:
                continue
            key = self._index_key(rp)
            if key in self.files_index:
                continue
            self.files.append(rp)
            self.files_index.add(key)
            added += 1
        if added:
            self._refresh_listbox()
        self._refresh_buttons()
        return added

    def _refresh_listbox(self) -> None:
        self.lst_files.delete(0, tk.END)
        for p in self.files:
            self.lst_files.insert(tk.END, str(p))

    def _refresh_buttons(self) -> None:
        can = bool(self.files) and bool(self.output_path_var.get())
        self.btn_combine.configure(state=(tk.NORMAL if can else tk.DISABLED))
        self.btn_remove.configure(state=(tk.NORMAL if self.files else tk.DISABLED))
        self.btn_clear.configure(state=(tk.NORMAL if self.files else tk.DISABLED))
        self.btn_up.configure(state=(tk.NORMAL if self.files else tk.DISABLED))
        self.btn_down.configure(state=(tk.NORMAL if self.files else tk.DISABLED))

    def _set_status(self, msg: str) -> None:
        self.status_var.set(msg)

    def _choose_initial_dir(self) -> str | None:
        return str(self.last_dir) if self.last_dir else None

    # Event handlers
    def on_add_files(self) -> None:
        initdir = self._choose_initial_dir()
        filenames = filedialog.askopenfilenames(
            title="Select .txt files",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            initialdir=initdir,
        )
        if not filenames:
            return
        paths = [Path(f) for f in filenames]
        self.last_dir = Path(paths[0]).parent
        added = self._add_files(paths)
        self._set_status(f"Added {added} file(s). Total: {len(self.files)}")

    def on_add_folder(self) -> None:
        initdir = self._choose_initial_dir()
        foldername = filedialog.askdirectory(title="Select folder", initialdir=initdir or os.getcwd())
        if not foldername:
            return
        folder = Path(foldername)
        self.last_dir = folder
        recursive = bool(self.include_subfolders_var.get())
        found = scan_txt_files(folder, recursive)
        added = self._add_files(found)
        self._set_status(
            f"Scanned {folder}; found {len(found)} .txt; added {added}. Total: {len(self.files)}"
        )

    def on_remove_selected(self) -> None:
        sel = list(self.lst_files.curselection())
        if not sel:
            return
        # Remove from end to start to keep indices valid
        for idx in reversed(sel):
            p = self.files.pop(idx)
            self.files_index.discard(self._index_key(p))
            self.lst_files.delete(idx)
        self._refresh_buttons()
        self._set_status(f"Removed {len(sel)}. Total: {len(self.files)}")

    def on_clear_all(self) -> None:
        if not self.files:
            return
        self.files.clear()
        self.files_index.clear()
        self._refresh_listbox()
        self._refresh_buttons()
        self._set_status("Cleared all files.")

    def on_move(self, delta: int) -> None:
        if not self.files:
            return
        sel = list(self.lst_files.curselection())
        if not sel:
            return
        # Compute new indices and move items
        new_sel: list[int] = []
        items = self.files
        indexes = sel if delta > 0 else list(reversed(sel))
        for idx in indexes:
            new_idx = idx + delta
            if new_idx < 0 or new_idx >= len(items):
                continue
            items[idx], items[new_idx] = items[new_idx], items[idx]
        self._refresh_listbox()
        # Update selection
        for idx in sel:
            ni = idx + delta
            if 0 <= ni < len(items):
                self.lst_files.selection_set(ni)
                new_sel.append(ni)
        if new_sel:
            self.lst_files.see(new_sel[0])

    def on_choose_output(self) -> None:
        initdir = self._choose_initial_dir() or os.getcwd()
        filename = filedialog.asksaveasfilename(
            title="Choose output file",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            initialdir=initdir,
        )
        if not filename:
            return
        out = Path(filename)
        self.last_dir = out.parent
        self.output_path_var.set(str(out))
        self._set_status(f"Output set: {out}")

    # Combine flow
    def on_combine(self) -> None:
        if not self.files or not self.output_path_var.get():
            return
        # Prepare params
        out_path = Path(self.output_path_var.get()).resolve()
        add_headers = bool(self.add_headers_var.get())
        enc_label = self.encoding_var.get()
        sep_raw = self.separator_var.get()
        sep = unescape_separators(sep_raw)

        # Disable controls during work
        self._toggle_controls(False)
        self.progress.start(10)
        self._set_status("Combining…")

        def worker():
            try:
                count, total_bytes, skipped = combine_files(
                    self.files, out_path, enc_label, add_headers, sep
                )
                # re-enable in main thread
                self.after(0, self._combine_complete, True, count, total_bytes, skipped, str(out_path))
            except Exception as e:
                self.after(0, self._combine_failed, e)

        threading.Thread(target=worker, daemon=True).start()

    def _toggle_controls(self, enabled: bool) -> None:
        state = tk.NORMAL if enabled else tk.DISABLED
        for w in (
            self.btn_add_files,
            self.btn_add_folder,
            self.chk_recursive,
            self.btn_remove,
            self.btn_clear,
            self.btn_up,
            self.btn_down,
            self.btn_output,
            self.chk_headers,
            self.cmb_encoding,
            self.entry_separator,
            self.btn_combine,
        ):
            try:
                w.configure(state=state)
            except tk.TclError:
                pass

    def _combine_complete(
        self, success: bool, count: int, total_bytes: int, skipped: List[Path], out_path: str
    ) -> None:
        self.progress.stop()
        self._toggle_controls(True)
        self._refresh_buttons()
        msg = f"Combined {count} file(s). Wrote {total_bytes} bytes to:\n{out_path}"
        if skipped:
            msg += f"\n\nSkipped {len(skipped)} unreadable/missing file(s)."
        messagebox.showinfo("Success", msg)
        self._set_status(msg.replace("\n", " "))

    def _combine_failed(self, err: Exception) -> None:
        self.progress.stop()
        self._toggle_controls(True)
        self._refresh_buttons()
        messagebox.showerror("Error", f"Combine failed: {err}")
        self._set_status(f"Error: {err}")


def main() -> None:
    try:
        # Use Tk themed widgets
        try:
            import ctypes

            if os.name == "nt":
                # Enable High DPI Awareness for sharper UI on Windows
                try:
                    ctypes.windll.shcore.SetProcessDpiAwareness(1)
                except Exception:
                    pass
        except Exception:
            pass
        app = TextCombinerApp()
        app.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

