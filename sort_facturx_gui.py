#!/usr/bin/env python3
"""
Factur-X Sorter - GUI version

Sorts PDFs in a folder into two subfolders:
  - factur-x/  : PDFs that contain an embedded structured invoice XML
                 (Factur-X / ZUGFeRD / XRechnung-hybrid / Order-X)
  - regular/   : all other PDFs

No installation needed when packaged as an .exe - just double-click it.
"""

import csv
import shutil
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext

import pikepdf

KNOWN_XML_NAMES = {
    "factur-x.xml",
    "facturx.xml",
    "zugferd-invoice.xml",
    "zugferd.xml",
    "xrechnung.xml",
    "order-x.xml",
    "orderx.xml",
    "cii.xml",
}


def get_embedded_xml_names(pdf_path: Path):
    names = []
    try:
        with pikepdf.open(pdf_path) as pdf:
            try:
                for name in pdf.attachments.keys():
                    names.append(str(name))
            except Exception:
                pass
    except Exception as e:
        return None, str(e)
    return names, None


def classify(pdf_path: Path):
    names, error = get_embedded_xml_names(pdf_path)
    if error:
        return False, None, error
    for n in names:
        lower = n.lower()
        if lower in KNOWN_XML_NAMES:
            return True, n, None
        if lower.endswith(".xml") and any(
            kw in lower for kw in ("factur", "zugferd", "invoice", "xrechnung", "order-x", "orderx")
        ):
            return True, n, None
    return False, None, None


class App:
    def __init__(self, root):
        self.root = root
        root.title("Factur-X Sorter")
        root.geometry("620x480")
        root.resizable(True, True)

        pad = {"padx": 12, "pady": 8}

        tk.Label(
            root,
            text="Sort PDFs into Factur-X (hybrid invoice) vs regular PDFs",
            font=("Segoe UI", 12, "bold"),
        ).pack(**pad)

        frame = tk.Frame(root)
        frame.pack(fill="x", **pad)

        self.folder_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.folder_var, width=55).pack(side="left", fill="x", expand=True)
        tk.Button(frame, text="Browse...", command=self.browse).pack(side="left", padx=(8, 0))

        self.run_btn = tk.Button(
            root, text="Sort PDFs", font=("Segoe UI", 11, "bold"),
            bg="#2563eb", fg="white", command=self.run_sort, height=2
        )
        self.run_btn.pack(fill="x", **pad)

        self.log = scrolledtext.ScrolledText(root, height=18, font=("Consolas", 9))
        self.log.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.log.configure(state="disabled")

    def log_line(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")
        self.root.update_idletasks()

    def browse(self):
        folder = filedialog.askdirectory(title="Select the folder containing your PDFs")
        if folder:
            self.folder_var.set(folder)

    def run_sort(self):
        folder = self.folder_var.get().strip()
        if not folder:
            messagebox.showwarning("No folder selected", "Please choose a folder first.")
            return
        input_dir = Path(folder)
        if not input_dir.is_dir():
            messagebox.showerror("Invalid folder", "That folder doesn't exist.")
            return

        self.run_btn.configure(state="disabled", text="Sorting...")
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

        thread = threading.Thread(target=self.do_sort, args=(input_dir,))
        thread.start()

    def do_sort(self, input_dir: Path):
        facturx_dir = input_dir / "factur-x"
        regular_dir = input_dir / "regular"
        facturx_dir.mkdir(exist_ok=True)
        regular_dir.mkdir(exist_ok=True)

        pdf_files = sorted(input_dir.glob("*.pdf")) + sorted(input_dir.glob("*.PDF"))

        if not pdf_files:
            self.log_line("No PDF files found directly in this folder.")
            self.finish()
            return

        rows = []
        counts = {"factur-x": 0, "regular": 0, "error": 0}

        for pdf_path in pdf_files:
            is_facturx, matched_name, error = classify(pdf_path)

            if error:
                counts["error"] += 1
                rows.append([pdf_path.name, "ERROR", "", error])
                self.log_line(f"[ERROR]    {pdf_path.name}: {error}")
                continue

            if is_facturx:
                dest = facturx_dir / pdf_path.name
                counts["factur-x"] += 1
                rows.append([pdf_path.name, "factur-x", matched_name, ""])
                self.log_line(f"[FACTUR-X] {pdf_path.name}  (found: {matched_name})")
            else:
                dest = regular_dir / pdf_path.name
                counts["regular"] += 1
                rows.append([pdf_path.name, "regular", "", ""])
                self.log_line(f"[REGULAR]  {pdf_path.name}")

            shutil.copy2(pdf_path, dest)

        report_path = input_dir / "_report.csv"
        with open(report_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["filename", "classification", "embedded_xml_name", "error"])
            writer.writerows(rows)

        self.log_line("")
        self.log_line("--- Summary ---")
        self.log_line(f"Factur-X : {counts['factur-x']}")
        self.log_line(f"Regular  : {counts['regular']}")
        self.log_line(f"Errors   : {counts['error']}")
        self.log_line("")
        self.log_line(f"Copied into: {facturx_dir}")
        self.log_line(f"        and: {regular_dir}")
        self.log_line(f"Report saved to: {report_path}")

        self.finish()
        messagebox.showinfo(
            "Done",
            f"Factur-X: {counts['factur-x']}\nRegular: {counts['regular']}\nErrors: {counts['error']}\n\n"
            f"Sorted copies were placed in the 'factur-x' and 'regular' subfolders."
        )

    def finish(self):
        self.run_btn.configure(state="normal", text="Sort PDFs")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
