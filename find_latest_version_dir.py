"""
Generic tool - given a parent directory (e.g. WoT's "mods" or "res_mods"
folder), finds the subdirectory whose name looks like the highest dotted
version number (e.g. picks "2.4.1.0" over "2.4.0.1", and correctly picks
"2.10.0.0" over "2.4.1.0" - NUMERIC comparison per dot-separated part, not
string/alphabetic comparison, which would get those two backwards) and
prints its full path to stdout.

Exists because WoT's mods/res_mods folders are named after the client
version (e.g. "mods\\2.4.1.0\\"), which changes on every game update - a
personal build_and_deploy.bat with that version hardcoded silently starts
deploying into a stale, no-longer-loaded folder after the next game patch.

This script itself is generic/reusable and has no machine-specific paths
baked in (see CLAUDE.md's convention: personal hardcoded paths belong in
gitignored wrapper scripts, e.g. build_and_deploy.bat, not here) - it just
takes the parent directory to search as an argument.

Non-version-looking entries in the parent directory (e.g. a "configs" or
"mods" subfolder sitting next to the version folders - both exist under
WoT's res_mods\\) are silently ignored, not errors.

Usage:
    C:\\Python27\\python.exe find_latest_version_dir.py <parent-dir>

Prints the matched directory's full path on success (exit 0). On failure
(parent dir missing, or no version-looking subdirectory found), prints
nothing to stdout, an explanation to stderr, and exits 1.
"""
import os
import re
import sys

VERSION_DIR_RE = re.compile(r"^\d+(\.\d+)+$")


def findLatestVersionDir(parentDir):
    if not os.path.isdir(parentDir):
        raise ValueError("not a directory: %s" % parentDir)

    candidates = []
    for name in os.listdir(parentDir):
        fullPath = os.path.join(parentDir, name)
        if not os.path.isdir(fullPath):
            continue
        if not VERSION_DIR_RE.match(name):
            continue
        candidates.append((tuple(int(part) for part in name.split(".")), name))

    if not candidates:
        raise ValueError("no version-looking subdirectory (e.g. \"2.4.1.0\") found under: %s" % parentDir)

    candidates.sort()
    bestName = candidates[-1][1]
    return os.path.join(parentDir, bestName)


def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python find_latest_version_dir.py <parent-dir>\n")
        return 1

    try:
        print(findLatestVersionDir(sys.argv[1]))
    except ValueError as e:
        sys.stderr.write("%s\n" % e)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
