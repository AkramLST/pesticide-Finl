# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Jadeed Zarai Markaz
# Build: pyinstaller build.spec

import sys
from pathlib import Path

ROOT = Path(SPECPATH)

a = Analysis(
    [str(ROOT / 'main.py')],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        # QSS stylesheets
        (str(ROOT / 'assets' / 'styles' / 'light.qss'), 'assets/styles'),
        (str(ROOT / 'assets' / 'styles' / 'dark.qss'),  'assets/styles'),
        # Logo / images
        (str(ROOT / 'images'), 'images'),
        # Pre-existing DB is optional; migrations create it fresh if absent
        # (str(ROOT / 'database' / 'pesticide.db'), 'database'),
    ],
    hiddenimports=[
        'PySide6.QtSvg',
        'PySide6.QtPrintSupport',
        'reportlab.graphics',
        'reportlab.platypus',
        'openpyxl',
        'matplotlib',
        'matplotlib.backends.backend_agg',
        'PIL',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='JadeedZaraiMarkaz',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # No console window on launch
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT / 'images' / 'logo_2.png'),   # change if .ico available
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='JadeedZaraiMarkaz',
)
