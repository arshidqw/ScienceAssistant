[app]

# (str) Title of your application
title = Science Assistant

# (str) Package name
package.name = scienceassistant

# (str) Package domain
package.domain = org.arshidqw

# (str) Source directory
source.dir = ui

# (str) Main entry point
source.main = app.py

# (list) Application source files
source.include_exts = py,json,png,jpg,jpeg,kv,atlas

# (str) Application version
version = 1.0.0

# (list) Required Python packages
requirements = python3,kivy,plyer,pyjnius

# (str) Orientation
orientation = portrait

# (list) Android permissions
android.permissions = RECORD_AUDIO

# (bool) Fullscreen
fullscreen = 0


[buildozer]

# (str) Log level
log_level = 2

# (bool) Warn about root user
warn_on_root = 0


[android]

# (str) Android API target
android.api = 35

# (str) Android minimum API
android.minapi = 23

# (str) Android NDK version
android.ndk = 27c

# (str) Android architecture
android.arch = arm64-v8a

# (bool) Accept Android SDK licenses
android.accept_sdk_license = True
