from PyInstaller.utils.hooks import collect_submodules, collect_data_files

hiddenimports = collect_submodules('findpatientzero')
datas = collect_data_files('findpatientzero', include_py_files=True)
datas += [('findpatientzero/gamedata', 'findpatientzero/gamedata')]

a = Analysis(
    ['findpatientzero/console.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='Find Patient Zero',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)