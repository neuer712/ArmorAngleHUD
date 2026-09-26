# -*- coding: utf-8 -*-
"""
Local dev build script - regenerates src/armorangle/armor_db/*.py from
armor_data/vehicles.json (see generate_armor_db.py), compiles src/ to .pyc
with Python 2.7 (must match the game's embedded interpreter) and packages a
.wotmod zip (STORED, no compression, per the game's loader requirement).

This mod never touches Flash/GUI.Text-only HUD - so unlike the
DispersionReticle-based build this was extracted from, there is no SWF and
no res/gui/ tree at all.

Usage:
    C:\\Python27\\python.exe build_wotmod.py
"""
import compileall
import os
import zipfile

import generate_armor_db

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
BUILD_DIR = os.path.join(ROOT, "build")

MOD_ID = "com.github.laiwei.armorangle"
MOD_NAME = "ArmorAngleHUD"
MOD_VERSION = "1.0.0-dev"
MOD_DESCRIPTION = "Standalone HUD estimating your own hull's armor incidence angle along your current aim direction."

# fixed filename regardless of MOD_VERSION (which still goes into meta.xml)
# so build_and_deploy.bat can find the output without globbing/guessing. Lives under
# build/ (gitignored) rather than the repo root, to keep build output out
# of the way of tracked source.
OUTPUT_WOTMOD = os.path.join(BUILD_DIR, "laiwei.armor_angle_hud_dev.wotmod")

META_XML = """<root>
   <id>%s</id>
   <version>%s</version>
   <name>%s</name>
   <description>%s</description>
</root>
""" % (MOD_ID, MOD_VERSION, MOD_NAME, MOD_DESCRIPTION)


def cleanStrayPyc():
    for dirpath, _dirnames, filenames in os.walk(SRC):
        for filename in filenames:
            if filename.endswith(".pyc"):
                os.remove(os.path.join(dirpath, filename))


def compileAll():
    # compile_dir returns 1 (truthy) on full success in Python 2.7
    success = compileall.compile_dir(SRC, quiet=1)
    if not success:
        raise SystemExit("py_compile failed, see output above")


def buildZip():
    if not os.path.isdir(BUILD_DIR):
        os.makedirs(BUILD_DIR)

    if os.path.exists(OUTPUT_WOTMOD):
        os.remove(OUTPUT_WOTMOD)

    zf = zipfile.ZipFile(OUTPUT_WOTMOD, "w", zipfile.ZIP_STORED)
    try:
        zf.writestr("meta.xml", META_XML)

        packageRoot = os.path.join(SRC, "armorangle")
        for dirpath, _dirnames, filenames in os.walk(packageRoot):
            for filename in filenames:
                if not filename.endswith(".pyc"):
                    continue
                fullPath = os.path.join(dirpath, filename)
                relPath = os.path.relpath(fullPath, SRC)
                arcName = "res/scripts/client/" + relPath.replace(os.sep, "/")
                zf.write(fullPath, arcName)

        entryPyc = os.path.join(SRC, "mod_ArmorAngleHUD.pyc")
        zf.write(entryPyc, "res/scripts/client/gui/mods/mod_ArmorAngleHUD.pyc")
    finally:
        zf.close()

    print("Built: %s" % OUTPUT_WOTMOD)


if __name__ == "__main__":
    generate_armor_db.generateAll()
    cleanStrayPyc()
    compileAll()
    buildZip()
    cleanStrayPyc()
