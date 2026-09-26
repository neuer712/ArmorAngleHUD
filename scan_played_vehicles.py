"""
Generic tool - scans one or more WoT python.log files for vehicles the
player has actually driven with "enabled" turned on in ArmorAngleHUD's
config, and adds any vehicle internal name not yet present in
armor_data/vehicles.json as a new entry with EMPTY armor data (safe
placeholder - confirmed by testing that armor_angle_hud.py just hides all
HUD slots for a vehicle with empty frontPlates/sidePlates, it does not
error).

Detection source: armor_angle_hud.py's _updateOnce already logs

    [ArmorAngleHUD] vehicle not in whitelist: <internal name>

exactly once per not-yet-whitelisted vehicle per battle, whenever the
player's OWN vehicle isn't found in armor_data/vehicles.json while the mod
is enabled (see armor_angle_hud.py). That is precisely "played but not
configured" - this script just harvests those lines.

CAVEAT: this only catches vehicles played while the mod's "enabled" setting
was true (default is false) - a vehicle played before the feature was ever
turned on won't have logged anything and won't be found here.

This script itself is generic/reusable and has no machine-specific paths
baked in (see CLAUDE.md's convention: personal hardcoded paths belong in
gitignored wrapper scripts, e.g. scan_played_vehicles.bat, not here).

Usage:
    C:\\Python27\\python.exe scan_played_vehicles.py <path-to-python.log> [more logs...]

    Or set the WOT_PYTHON_LOG environment variable and run with no args.
    Multiple log paths (e.g. python.log plus rotated python.log.1, .2, ...)
    can be passed to catch vehicles seen in older sessions.
"""
import json
import os
import re
import sys
from collections import OrderedDict

ROOT = os.path.dirname(os.path.abspath(__file__))
VEHICLES_JSON_PATH = os.path.join(ROOT, "armor_data", "vehicles.json")
ARMOR_DB_INIT_PATH = os.path.join(ROOT, "src", "armorangle", "armor_db", "__init__.py")

_LOG_LINE_RE = re.compile(r"\[ArmorAngleHUD\] vehicle not in whitelist:\s*(\S+)")
_NATION_MODULES_RE = re.compile(r"_NATION_MODULES\s*=\s*\{(.*?)\}", re.DOTALL)
_NATION_KEY_RE = re.compile(r'"(\w+)"\s*:')

_NEW_VEHICLE_NOTE = ("armor data not filled in yet, HUD shows nothing for this "
                      "vehicle until frontPlates/sidePlates are filled in and "
                      "generate_armor_db.py is re-run.")


def findPlayedUnlistedVehicles(logPaths):
    found = OrderedDict()  # internal name -> None, insertion-ordered, de-duped
    for logPath in logPaths:
        if not os.path.isfile(logPath):
            print("WARNING: log file not found, skipping: %s" % logPath)
            continue
        f = open(logPath, "r")
        try:
            for line in f:
                m = _LOG_LINE_RE.search(line)
                if m:
                    found[m.group(1)] = None
        finally:
            f.close()
    return list(found.keys())


def loadVehiclesJson():
    f = open(VEHICLES_JSON_PATH, "r")
    try:
        return json.load(f, object_pairs_hook=OrderedDict)
    finally:
        f.close()


def getWiredNations():
    """
    armor_db/__init__.py's _NATION_MODULES dict is a hardcoded, manually
    maintained lazy-load table (only nation keys listed there are ever
    reachable via getVehicleArmor - see armor_db/__init__.py). Parsed here
    (rather than duplicating the list) so a newly-discovered nation not yet
    wired up there can be flagged instead of silently added as a dead entry.
    """
    f = open(ARMOR_DB_INIT_PATH, "r")
    try:
        source = f.read()
    finally:
        f.close()

    m = _NATION_MODULES_RE.search(source)
    if not m:
        return set()
    return set(_NATION_KEY_RE.findall(m.group(1)))


def addMissingVehicles(data, playedNames):
    added = []
    newNations = []
    for name in playedNames:
        nation, sep, _tag = name.partition(":")
        if not sep:
            print("WARNING: vehicle name doesn't look like 'nation:Tag', skipping: %s" % name)
            continue

        nationVehicles = data.get(nation)
        if nationVehicles is None:
            nationVehicles = OrderedDict()
            data[nation] = nationVehicles
            newNations.append(nation)

        if name in nationVehicles:
            continue

        nationVehicles[name] = OrderedDict([
            ("notes", _NEW_VEHICLE_NOTE),
            ("safetyThreshold1", None),
            ("safetyThreshold2", None),
            ("frontPlates", []),
            ("sidePlates", [])
        ])
        added.append(name)

    wiredNations = getWiredNations()
    unwiredNations = sorted(set(newNations) - wiredNations)
    if unwiredNations:
        print("WARNING: nation(s) %s are new to vehicles.json but NOT in "
              "armor_db/__init__.py's _NATION_MODULES table - getVehicleArmor "
              "won't find these vehicles at runtime until you add a "
              "'<nation>.py' module entry there too (see the germany.py / "
              "generate_armor_db.py pattern)." % ", ".join(unwiredNations))

    return added


###########################################################
# Custom pretty-printer matching vehicles.json's existing hand-formatted
# style (plain json.dump(indent=4) would also expand each plate dict's
# fields onto separate lines, which doesn't match - plate dicts stay
# compact/single-line in this file).
###########################################################

def _dumpPlateList(plates, indent):
    if not plates:
        return "[]"

    innerIndent = indent + "    "
    lines = [innerIndent + json.dumps(p) for p in plates]
    return "[\n" + ",\n".join(lines) + "\n" + indent + "]"


def _dumpVehicle(vehicle, indent):
    innerIndent = indent + "    "
    lines = [
        innerIndent + '"notes": %s,' % json.dumps(vehicle.get("notes", "")),
        innerIndent + '"safetyThreshold1": %s,' % json.dumps(vehicle.get("safetyThreshold1")),
        innerIndent + '"safetyThreshold2": %s,' % json.dumps(vehicle.get("safetyThreshold2")),
        innerIndent + '"frontPlates": %s,' % _dumpPlateList(vehicle.get("frontPlates", []), innerIndent),
        innerIndent + '"sidePlates": %s' % _dumpPlateList(vehicle.get("sidePlates", []), innerIndent),
    ]
    return "{\n" + "\n".join(lines) + "\n" + indent + "}"


def _dumpNation(vehicles, indent):
    innerIndent = indent + "    "
    keys = list(vehicles.keys())
    lines = []
    for i, key in enumerate(keys):
        suffix = "," if i < len(keys) - 1 else ""
        lines.append(innerIndent + "%s: %s%s" % (json.dumps(key), _dumpVehicle(vehicles[key], innerIndent), suffix))
    return "{\n" + "\n".join(lines) + "\n" + indent + "}"


def dumpVehiclesJson(data):
    keys = list(data.keys())
    lines = []
    for i, key in enumerate(keys):
        suffix = "," if i < len(keys) - 1 else ""
        lines.append("    %s: %s%s" % (json.dumps(key), _dumpNation(data[key], "    "), suffix))
    return "{\n" + "\n".join(lines) + "\n}\n"


def main():
    logPaths = sys.argv[1:]
    if not logPaths:
        envPath = os.environ.get("WOT_PYTHON_LOG")
        if not envPath:
            print("Usage: python scan_played_vehicles.py <path-to-python.log> [more logs...]")
            print("       (or set the WOT_PYTHON_LOG environment variable)")
            sys.exit(1)
        logPaths = [envPath]

    playedNames = findPlayedUnlistedVehicles(logPaths)
    if not playedNames:
        print("No '[ArmorAngleHUD] vehicle not in whitelist' lines found in the given log(s).")
        return

    data = loadVehiclesJson()
    added = addMissingVehicles(data, playedNames)

    if not added:
        print("All %d vehicle(s) found in the log(s) are already in vehicles.json." % len(playedNames))
        return

    f = open(VEHICLES_JSON_PATH, "w")
    try:
        f.write(dumpVehiclesJson(data))
    finally:
        f.close()

    print("Added %d new vehicle(s) to %s:" % (len(added), VEHICLES_JSON_PATH))
    for name in added:
        print("  %s" % name)
    print("These have EMPTY armor data (HUD will show nothing for them). Fill in real")
    print("frontPlates/sidePlates, then run generate_armor_db.py (build.bat already does")
    print("this automatically).")


if __name__ == "__main__":
    main()
