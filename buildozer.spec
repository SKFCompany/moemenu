[app]
title = МоёМеню
package.name = moemenu
package.domain = org.moemenu
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db,ttf
source.exclude_dirs = venv,.git,.buildozer,bin,__pycache__
source.exclude_patterns = venv/*,*.pyc,*.pyo
version = 1.0

requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow==10.4.0,requests,cython==0.29.36

# Закреплённая версия python-for-android: без этого buildozer клонирует
# ветку master, которая сейчас таргетит Python 3.14 и ломает сборку Kivy
# (несовпадение сигнатур OpenGL-функций, приватные CPython C-API убраны в 3.14).
# v2024.01.21 — последний стабильный релиз p4a, официально совместимый с
# Kivy 2.3.0 и таргетящий Python 3.11.5.
p4a.branch = v2024.01.21

# Android
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 26
android.ndk = 25b
android.sdk = 33
android.archs = arm64-v8a, armeabi-v7a

# App icon (place icon.png 512x512 in project root)
icon.filename = %(source.dir)s/assets/icon.png
presplash.filename = %(source.dir)s/assets/splash.png
android.presplash_color = #2E660D

orientation = portrait
android.manifest.orientation = portrait
android.allow_backup = True
android.softinput_mode = adjustResize

# iOS (not configured)
[buildozer]
log_level = 2
warn_on_root = 1
