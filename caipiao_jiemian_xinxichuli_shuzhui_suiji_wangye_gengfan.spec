# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['caipiao_jiemian_xinxichuli_shuzhui_suiji_wangye_gengfan.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
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
    name='caipiao_jiemian_xinxichuli_shuzhui_suiji_wangye_gengfan',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='caipiao_jiemian_xinxichuli_shuzhui_suiji_wangye_gengfan',
)
