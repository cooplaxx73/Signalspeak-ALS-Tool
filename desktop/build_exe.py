"""
Build the Windows app and pack it into one zip for download.

Run from the desktop folder, inside the virtual environment:
    pip install pyinstaller
    python build_exe.py

Result: dist/SignalSpeak-windows.zip, holding a SignalSpeak folder with
SignalSpeak.exe, a "Pair with account" shortcut and a short READ ME.

Libraries:
- PyInstaller: https://pyinstaller.org
- shutil and subprocess (part of Python)

Written with the assistance of Claude Code (Anthropic).
"""

import shutil
import subprocess
import sys
from pathlib import Path

FOLDER = Path(__file__).resolve().parent
APP = FOLDER / "dist" / "SignalSpeak"

PAIR_SHORTCUT = '@start "" "%~dp0SignalSpeak.exe" --pair\r\n'

READ_ME = """SignalSpeak for Windows
=======================

Hands-free computer control with an ordinary webcam.

1. Keep this whole folder together (SignalSpeak.exe needs the _internal folder).
2. Double-click SignalSpeak.exe.
3. First launch only: connect to your patient account, or choose "Use offline".
4. Look at each dot to calibrate. Then look to move the cursor and close
   both eyes for half a second to click.

F8 pauses eye control. F9 closes SignalSpeak.
To connect to an account later, double-click "Pair with account.bat".

If Windows shows "Windows protected your PC", choose More info > Run anyway.
The app is not code-signed because it is a student prototype.

Your settings, activity log and pairing are saved in this folder.
Full documentation: https://github.com/cooplaxx73/QEC---2026
"""


def main() -> None:
    model = FOLDER / "face_landmarker.task"
    if not model.exists():
        sys.exit("face_landmarker.task is missing. Run python main.py once to download it.")

    subprocess.run([sys.executable, "-m", "PyInstaller", "signalspeak.spec",
                    "--noconfirm", "--clean"], cwd=FOLDER, check=True)

    (APP / "Pair with account.bat").write_text(PAIR_SHORTCUT, encoding="ascii")
    (APP / "READ ME.txt").write_text(READ_ME, encoding="utf-8")

    archive = shutil.make_archive(str(FOLDER / "dist" / "SignalSpeak-windows"),
                                  "zip", root_dir=APP.parent, base_dir=APP.name)
    size = Path(archive).stat().st_size / 1e6
    print(f"Built {archive} ({size:.0f} MB)")


if __name__ == "__main__":
    main()
