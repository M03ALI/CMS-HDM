# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec — builds the HDM Cattle Management Windows desktop app (onedir).
#
#   pyinstaller build_windows.spec --noconfirm --clean
#
# Result: dist\HDMCattle\HDMCattle.exe plus its support files.
# onedir (not onefile) is used deliberately: Streamlit ships a static frontend
# and package metadata that a onefile build often fails to unpack at runtime.
import os
from PyInstaller.utils.hooks import collect_all, copy_metadata

# The app script the launcher runs must travel with the bundle.
datas = [("cattlemanagementapp.py", ".")]
binaries = []
hiddenimports = []

# Collect data files, binaries and submodules for Streamlit and everything the
# app imports. Missing packages are skipped quietly.
_PACKAGES = [
    "streamlit", "altair", "pandas", "numpy", "pyarrow",
    "reportlab", "PIL", "tornado", "click", "blinker",
    "pydeck", "watchdog", "validators", "tenacity", "toml", "rich",
    "packaging", "tzlocal", "cachetools",
    # native desktop window
    "webview", "clr_loader",
]
for pkg in _PACKAGES:
    try:
        d, b, h = collect_all(pkg)
        datas += d
        binaries += b
        hiddenimports += h
    except Exception:
        pass

# pywebview loads its Windows backend and .NET bridge dynamically — name them so
# PyInstaller doesn't drop them.
hiddenimports += [
    "clr", "webview.platforms.edgechromium", "webview.platforms.winforms",
]

# importlib.metadata lookups (e.g. streamlit.__version__) need the dist-info.
for meta in ["streamlit", "pandas", "numpy", "pyarrow", "altair",
             "reportlab", "pillow", "pywebview", "pythonnet"]:
    try:
        datas += copy_metadata(meta)
    except Exception:
        pass

_icon = "cattle.ico" if os.path.exists("cattle.ico") else None

a = Analysis(
    ["run_desktop.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="HDMCattle",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # windowed app — no console window pops up
    disable_windowed_traceback=False,
    icon=_icon,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="HDMCattle",
)
