# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 打包配置文件
用于将水下目标识别系统打包为可执行文件
"""

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.py', '.'),
        ('models', 'models'),
        ('data', 'data'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtCharts',
        'ultralytics',
        'ultralytics.models',
        'ultralytics.nn',
        'ultralytics.utils',
        'pymysql',
        'pymysql.cursors',
        'cv2',
        'numpy',
        'pandas',
        'matplotlib',
        'matplotlib.pyplot',
        'seaborn',
        'torch',
        'torchvision',
        'PIL',
        'yaml',
        'tqdm',
        'requests',
        'cryptography',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'test',
        'unittest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='UnderwaterDetection',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='icon.ico'  # 如果有图标文件，取消注释此行
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='UnderwaterDetection',
)

# 打包说明：
# 1. 确保已安装所有依赖：pip install -r requirements.txt
# 2. 执行打包命令：pyinstaller UnderwaterDetection.spec
# 3. 打包完成后，在 dist/UnderwaterDetection/ 目录下找到可执行文件
# 4. 注意：首次运行需要配置数据库连接
