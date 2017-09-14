import os
import site
import sys

from cx_Freeze import setup, Executable

## Get the site-package folder, not everybody will install
## Python into C:\PythonXX
site_dir = site.getsitepackages()[1]
include_dll_path = os.path.join(site_dir, "gnome")

## Collect the list of missing dll when cx_freeze builds the app
missing_dll = ['libgtk-3-0.dll',
               'libgdk-3-0.dll',
               'libatk-1.0-0.dll',
               'libcairo-gobject-2.dll',
               'libgdk_pixbuf-2.0-0.dll',
               'libjpeg-8.dll',
               'libpango-1.0-0.dll',
               'libpangocairo-1.0-0.dll',
               'libpangoft2-1.0-0.dll',
               'libpangowin32-1.0-0.dll',
               ]

## We also need to add the glade folder, cx_freeze will walk
## into it and copy all the necessary files
glade_folder = 'resources'

## We need to add all the libraries too (for themes, etc..)
gtk_libs = ['etc',
            'lib',
            'share',
            'lib/gdk-pixbuf-2.0',
            'lib/girepository-1.0',
            'share/glib-2.0'
            ]

## Create the list of includes as cx_freeze likes
include_files = []
for dll in missing_dll:
    include_files.append((os.path.join(include_dll_path, dll), dll))

## Let's add glade folder and files
include_files.append((glade_folder, glade_folder))

## Let's add gtk libraries folders and files
for lib in gtk_libs:
    include_files.append((os.path.join(include_dll_path, lib), lib))

base = None

## Lets not open the console while running the app
if sys.platform == "win32":
    base = "Win32GUI"

executables = [
    Executable("main.py",
               base=base,
               icon="icon.ico"
               )
]

buildOptions = dict(
    includes=["gi", "lxml._elementpath"],
    packages=["gi"],
    include_files=include_files
)

setup(
    name="TurBoSketcher",
    author="TurBoss",
    version="1.0",
    description="Tool to edit text in svg files",
    options=dict(build_exe=buildOptions),
    executables=executables
)
