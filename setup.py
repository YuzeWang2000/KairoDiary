from setuptools import setup

APP = ['main.py']  # 替换成你的主脚本文件名
DATA_FILES = ['KairoDiary.icns']  # 确保你有 .icns 图标文件
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'KairoDiary.icns',  # 应用图标
    'plist': {
        'CFBundleName': 'KairoDiary',  # 应用名称（显示在 Dock 和菜单栏）
        'CFBundleDisplayName': 'KairoDiary',  # 显示名称
        'CFBundleIdentifier': 'com.kairosoft.kairodiary',  # 唯一标识符
        'CFBundleVersion': '1.0.0',  # 版本号
        'NSHumanReadableCopyright': '© 2025 KairoSoft',  # 版权信息
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)