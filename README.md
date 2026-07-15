# Factur-X Sorter — build & distribute a Windows .exe

This folder builds a standalone Windows program (`FacturXSorter.exe`) that
your end users can just double-click. No install, no admin rights, no
Python required on their machines — the .exe is self-contained.

I can't compile a Windows binary directly (I run in a Linux sandbox), so
this uses GitHub Actions — a free service — to do the actual Windows build
for you. You only need a free GitHub account; you do NOT need a Windows
machine yourself.

## One-time setup (about 5 minutes)

1. Go to https://github.com and create a free account if you don't have one.
2. Create a new repository (it can be private) — e.g. "facturx-sorter".
3. Upload all the files in this folder to that repository, keeping the
   folder structure (the `.github/workflows/build.yml` file must stay at
   that exact path — it's what tells GitHub to build the exe).
   Easiest way: on the repo page, click "Add file" → "Upload files", drag
   in everything (including the hidden `.github` folder — if your upload
   method hides dotfiles, use `git` on the command line instead, or a tool
   like GitHub Desktop which shows them).
4. Once uploaded, go to the "Actions" tab of your repository. A workflow
   run should start automatically (or click "Run workflow" if not).
5. Wait 2-3 minutes for it to finish (green checkmark).
6. Click into the finished run, scroll to "Artifacts", and download
   "FacturXSorter-windows-exe" — this is a zip containing your .exe.

## Giving it to your users

- Unzip it and send them `FacturXSorter.exe` directly (email, shared
  drive, USB stick — anything).
- They double-click it. No install. No admin rights needed.
- **Important:** because the .exe isn't digitally signed (that costs
  money and requires a registered publisher), Windows SmartScreen will
  likely show a blue "Windows protected your PC" warning the first time
  it's run. Users click "More info" → "Run anyway". This is normal for
  small unsigned tools and only appears once per machine typically.

## What the program does

1. User clicks "Browse..." and picks the folder containing their PDFs.
2. Clicks "Sort PDFs".
3. The tool creates two subfolders inside that folder:
   - `factur-x\` — PDFs with an embedded structured invoice XML
     (Factur-X / ZUGFeRD / XRechnung-hybrid / Order-X)
   - `regular\` — all other PDFs
   - a `_report.csv` log of what was found in each file
   Originals are left untouched (files are copied, not moved).

## Updating it later

If you want to tweak the detection logic or the interface, edit
`sort_facturx_gui.py`, push the change to the repository, and GitHub
Actions will automatically rebuild the .exe — just download the new
artifact from the Actions tab again.

## Files in this folder

- `sort_facturx_gui.py` — the actual program (Python + tkinter GUI)
- `requirements.txt` — dependencies needed to build it
- `.github/workflows/build.yml` — tells GitHub Actions how to build the
  Windows exe automatically on every push
