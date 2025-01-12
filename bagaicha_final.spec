# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all necessary data files
added_files = [
    ('cafe_manager/utils/*.py', 'cafe_manager/utils'),
    ('cafe_manager/pages/*.py', 'cafe_manager/pages'),
    ('cafe_manager/*.py', 'cafe_manager'),
    ('cafe_manager.db', '.'),  # Include the database file
]

# Collect all submodules
hidden_imports = [
    'customtkinter',
    'tkcalendar',
    'sqlite3',
    'PIL',
    'PIL._tkinter_finder',
    'tkinter',
] + collect_submodules('customtkinter')

a = Analysis(
    ['main.py'],
    pathex=[os.path.abspath(SPECPATH)],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Add additional data files from customtkinter
a.datas += collect_data_files('customtkinter')

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Tropical Bagaicha',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
) 