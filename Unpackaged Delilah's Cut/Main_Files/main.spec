# -*- mode: python ; coding: utf-8 -*-

import os

# Define the base project directory
project_dir = r"C:\\Users\\Gaming PC\\Desktop\\Delilah's Cut"

# Add all necessary data files and directories
datas = [
    (os.path.join(project_dir, 'Main_Files', 'MarkDownFiles', 'InformationPage.md'), 'MarkDownFiles'),
    (os.path.join(project_dir, 'Main_Files', 'MarkDownFiles', 'UsagePage.md'), 'MarkDownFiles'),
    (os.path.join(project_dir, 'Main_Files', 'rnaFolding.py'), '.'),  # Include rnaFolding.py in the root of the bundle
    (os.path.join(project_dir, 'Main_Files', 'rnaBatchFolding.py'), '.'), 
    ('Assets/Delilah\'s_Cut_Logo.png', 'Assets'),
    # Add other necessary data directories/files as needed
    # (os.path.join(project_dir, 'SomeOtherFolder', 'file.extension'), 'DestinationFolderInPackage')
]

a = Analysis(
    [os.path.join(project_dir, 'Main_Files', 'main.py')],  # Main script to be executed
    pathex=[project_dir],  # Add the project directory to the path
    binaries=[],  # Any binary files if needed
    datas=datas,  # Include the data files
    hiddenimports=['RNA', 'ViennaRNA', 'PyQt6'],  # Hidden imports if needed, add PyQt6, ViennaRNA, etc. if required
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
    a.binaries,
    a.datas,
    [],
    name='Delilahs_Cut',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="Assets/Delilah's_Cut_Logo.ico"
)
