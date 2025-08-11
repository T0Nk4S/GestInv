# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('ui/*.py', 'ui'),
        ('database.py', '.'),
    ],
    hiddenimports=[
        'sqlite3',
        'reportlab',
        'reportlab.lib',
        'reportlab.lib.pagesizes',
        'reportlab.pdfgen',
        'reportlab.pdfgen.canvas',
        'pandas',
        'cv2',
        'pyzbar',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GestorInventario',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False
)
