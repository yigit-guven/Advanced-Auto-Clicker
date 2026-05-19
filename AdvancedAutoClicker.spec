# -*- mode: python ; coding: utf-8 -*-
import re

# Read version dynamically from version.py
version = "1.0.0"
try:
    with open("version.py", "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("VERSION"):
                match = re.search(r'VERSION\s*=\s*["\']([^"\']+)["\']', line)
                if match:
                    version = match.group(1)
                    break
except Exception as e:
    print("Error reading version.py:", e)

# Dynamically generate file_version_info.txt
try:
    parts = version.split('.')
    while len(parts) < 4:
        parts.append("0")
    v_tuple = ", ".join(parts)
    v_str = ".".join(parts)
    
    version_info_content = f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({v_tuple}),
    prodvers=({v_tuple}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])]),
    StringFileInfo(
      [
        StringTable(
          u'040904b0',
          [
            StringStruct(u'CompanyName', u'Yi\\u011fit G\\u00fcven'),
            StringStruct(u'FileDescription', u'Advanced Auto Clicker Installer'),
            StringStruct(u'FileVersion', u'{v_str}'),
            StringStruct(u'InternalName', u'AdvancedAutoClickerInstaller'),
            StringStruct(u'LegalCopyright', u'Copyright (c) 2026 Yi\\u011fit G\\u00fcven. MIT License.'),
            StringStruct(u'OriginalFilename', u'AdvancedAutoClickerInstaller_{version}.exe'),
            StringStruct(u'ProductName', u'Advanced Auto Clicker'),
            StringStruct(u'ProductVersion', u'{v_str}')
          ]
        )
      ]
    )
  ]
)
"""
    with open("file_version_info.txt", "w", encoding="utf-8") as f:
        f.write(version_info_content)
except Exception as e:
    print("Error generating file_version_info.txt dynamically:", e)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('icon.png', '.')],
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
    a.binaries,
    a.datas,
    [],
    name='AdvancedAutoClickerInstaller_' + version,
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
    icon='icon.ico',
    version='file_version_info.txt',
)
