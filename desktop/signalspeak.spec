# PyInstaller recipe for the Windows app, SignalSpeak.exe.
# Build with:  python build_exe.py   (it runs this file, then zips the result)
#
# PyInstaller docs: https://pyinstaller.org/en/stable/spec-files.html
# Written with the assistance of Claude Code (Anthropic).

from PyInstaller.utils.hooks import collect_all, collect_submodules

# MediaPipe ships data files and native libraries that PyInstaller cannot
# find by itself, so collect the whole package.
datas, binaries, hiddenimports = collect_all("mediapipe")

# The face model goes inside the app, so nothing is downloaded on first run.
datas += [("face_landmarker.task", ".")]

# Libraries that pick their Windows backend at run time.
hiddenimports += collect_submodules("pynput")
hiddenimports += collect_submodules("pyttsx3")
hiddenimports += collect_submodules("screen_brightness_control")
hiddenimports += ["comtypes", "comtypes.client", "wmi"]

analysis = Analysis(
    ["launch.pyw"],
    pathex=["."],
    datas=datas,
    binaries=binaries,
    hiddenimports=hiddenimports,
    # Big libraries the program never uses.
    # (matplotlib must stay: MediaPipe imports it.)
    excludes=["tkinter", "pandas", "scipy", "IPython", "pytest",
              "PySide6.QtWebEngineCore", "PySide6.QtWebEngineWidgets",
              "PySide6.Qt3DCore", "PySide6.QtQuick3D", "PySide6.QtMultimedia",
              "PySide6.QtCharts", "PySide6.QtDataVisualization", "PySide6.QtPdf"],
)

program = PYZ(analysis.pure)

exe = EXE(
    program,
    analysis.scripts,
    exclude_binaries=True,
    name="SignalSpeak",
    console=False,   # no black terminal window
    upx=False,
)

COLLECT(exe, analysis.binaries, analysis.datas, name="SignalSpeak", upx=False)
