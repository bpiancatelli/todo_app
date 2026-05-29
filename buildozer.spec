[app]
title = Ma Todo List
package.name = mytodolist
package.domain = org.piancatelli
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0.0

requirements = python3,kivy==2.3.0,kivymd,plyer,pillow

orientation = portrait
fullscreen = 0

# Background service for notifications when app is closed
services = TodoNotification:service/main.py:foreground

android.permissions = RECEIVE_BOOT_COMPLETED,FOREGROUND_SERVICE,POST_NOTIFICATIONS,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 34
android.minapi = 26
android.ndk = 28c
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.icon.filename = %(source.dir)s/assets/icon.png

[buildozer]
log_level = 2
warn_on_root = 1
