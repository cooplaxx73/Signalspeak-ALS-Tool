"""
Where SignalSpeak keeps its files.

Run from source, everything lives next to the .py files. Run as the Windows
app (SignalSpeak.exe), the program's own files are unpacked into a bundle
folder, but the patient's files (settings, log, pairing) must sit next to
the .exe so they survive updates and are easy to find and delete.

Libraries: Python standard library only (sys, pathlib).
Written with the assistance of Claude Code (Anthropic).
"""

import sys
from pathlib import Path

# PyInstaller sets sys.frozen when the program runs as an .exe.
RUNNING_AS_EXE = getattr(sys, "frozen", False)

if RUNNING_AS_EXE:
    # Patient files: the folder that holds SignalSpeak.exe.
    APP_FOLDER = Path(sys.executable).resolve().parent
    # Files shipped inside the app, such as the face model.
    BUNDLE_FOLDER = Path(getattr(sys, "_MEIPASS", APP_FOLDER))
else:
    APP_FOLDER = BUNDLE_FOLDER = Path(__file__).resolve().parent
