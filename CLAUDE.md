# CLAUDE.md

Read this first. It orients you fast; go to `README.md` for user-facing docs (what the mod does,
how to install/configure it).

## What this repo is

A standalone World of Tanks Python client mod: a small on-screen HUD estimating the player's OWN
hull armor incidence angle, assuming a hypothetical enemy positioned along the current aim
direction (a defensive "am I angled enough" tool, not an offensive penetration calculator).

**This project was extracted on 2026-09-26 from `DispersionReticle_with_armor_angle`**
(`D:\GitHub\DispersionReticle_with_armor_angle` on this machine), where the same feature existed as
an add-on bolted onto Pruszko's DispersionReticle mod (`dispersionreticle.armorangle.*` package,
that mod's generic config/ModsSettingsAPI/hook infrastructure, packaged together with its reticle
Flash SWF). This repo is now fully independent: no DispersionReticle code, no Flash, no
ModsSettingsAPI - see git history / that other repo's `HANDOFF.md` and `ARMOR_ANGLE_PLAN.md` if you
need the original math-derivation rationale and design history; the derivations there are still
correct and worth reading, everything about *how it's packaged/configured* is now different (this
file describes the current, standalone reality).

That other repo's armor-angle feature was intentionally left in place, untouched, when this repo
was created - the two currently coexist as separate distributions of overlapping functionality.
Changes made here do NOT need to be mirrored there, and vice versa, unless the user explicitly asks
for a specific fix/data update to be ported both ways.

## Environment facts (confirmed on this machine, not guesses)

This repo is intended to be public/shareable - the specific paths below are the current
maintainer's own machine, recorded as a working example, not a requirement. A different contributor
should substitute their own Python 2.7 install and WoT game directory.

- Target runtime: **Python 2.7** (WoT's embedded interpreter). Installed locally at
  `C:\Python27\python.exe` - use it for everything (compiling, running scratch test scripts).
- No test framework. Pattern: write a small standalone script that does
  `sys.path.insert(0, r"D:\GitHub\ArmorAngleHUD\src")` then imports `armorangle.armor_math` /
  `armorangle.armor_db` directly (both 100% BigWorld-free by design), run with
  `C:\Python27\python.exe`. Everything else in this repo (`armor_angle_hud.py`, `hooks.py`) touches
  `BigWorld`/`GUI`/`VehicleGunRotator`/`game` and CANNOT be unit tested here - only verified by
  building, deploying, and having the user test in a training room and read back the game's log.
- **On this machine's client (2.4.0.1), Python's `logging` output does NOT go to `python.log`
  anymore - it goes into `game.log`** (tagged `[SCRIPT]`), confirmed 2026-09-26 by noticing
  `python.log`'s mtime was stuck on 2026-08-29 while `game.log` had the same day's full mod
  init/tick/whitelist-miss lines (`[gui.mods.mod_armoranglehud]`, `[armorangle.config]`,
  `[armorangle.armor_angle_hud]`). Don't assume "no new lines in python.log" means the mod isn't
  running - check `game.log` first. `scan_played_vehicles.bat` already points at `game.log` for
  this reason; a different WoT version might behave differently, verify before assuming either way.
- **Gotcha inherited from the parent project**: `python -m py_compile` does NOT catch "non-ASCII
  character but no encoding declared" errors the way `import` does (Python 2 quirk). Never trust
  `py_compile` alone as a syntax gate for a file with non-ASCII content (e.g. the `# -*- coding:
  utf-8 -*-` files) - write a script that actually `import`s the module.
- No hardcoded WoT install path anywhere in tracked files. Deployment is manual: build with
  `build.bat`, then the user copies `build/laiwei.armor_angle_hud_dev.wotmod` into their
  `mods\<client version>\` folder themselves (or writes their own personal, gitignored
  `build_and_deploy.bat` if they want that automated - none is checked in, unlike the parent repo,
  since this repo has no single canonical target machine).

## Build

- `build.bat` (via `C:\Python27\python.exe build_wotmod.py`): runs `generate_armor_db.py` first,
  compiles `src/` to `.pyc`, packages `build/laiwei.armor_angle_hud_dev.wotmod` (STORED zip, no
  compression - required by the game's loader). `build/` is gitignored.
- `generate_armor_db.py`: reads `armor_data/*.json`, writes `src/armorangle/armor_db/*.py`.
  **Generated files are marked "DO NOT EDIT BY HAND" - edit the JSON, regenerate.**
- mod id `com.github.laiwei.armorangle`, entry point `res/scripts/client/gui/mods/mod_ArmorAngleHUD.pyc`,
  everything else under `res/scripts/client/armorangle/**`. No `res/gui/` tree at all (no images, no
  translations, no Mod Configurator page - see "Deliberately NOT included" below).
- Nothing in this repo gets committed automatically - only commit when explicitly asked.

## Discovering new vehicles

`scan_played_vehicles.py` (tracked, generic, no machine-specific paths) scans one or more
`python.log` files for `[ArmorAngleHUD] vehicle not in whitelist: <internal name>` lines (logged
once per battle by `armor_angle_hud.py._updateOnce` whenever the player's own vehicle isn't found
in `armor_data/vehicles.json` while the mod is enabled) and adds any not-yet-listed vehicle to
`vehicles.json` with empty placeholder armor data (safe - the HUD just shows nothing for it until
`frontPlates`/`sidePlates` are filled in). Ported forward from the parent project unchanged except
for the log-line prefix (`[ArmorAngleHUD]` here, was `[ArmorAngle]` there) and the
`armor_db/__init__.py` path it parses to detect not-yet-wired nations.

Usage: `C:\Python27\python.exe scan_played_vehicles.py <path-to-log>`, or set `WOT_PYTHON_LOG` and
run with no args. **On this machine, point it at `game.log`, not `python.log`** (see the log-location
Environment fact above) - `scan_played_vehicles.bat` already does. That `.bat` is the personal,
gitignored wrapper hardcoding this machine's log path (mirrors `build_and_deploy.bat`'s convention) -
not tracked, recreate it per-machine if missing. Already used once live on 2026-09-26: correctly
picked up `germany:G176_Jagdpanzer_E90` from `game.log` and added it as an empty placeholder entry.

## Data model (armor_data/*.json -> generated Python)

Same schema/conventions as the parent project (see that repo's `CLAUDE.md` for the full writeup if
needed, or the docstring at the top of `generate_armor_db.py` here, which carries the same
explanation forward):
- `armor_data/vehicles.json`: per-vehicle armor plate data, grouped by nation
  (`label`/`bearingDeg`/`slopeDeg`/`nominalMm`/`mirror`).
- `armor_data/tier_thresholds.json`: `{tier: [threshold1, threshold2]}` for HUD color-coding.
  Currently only tiers 7 (180/220) and 8 (230/270) have real numbers; the rest are `null`
  placeholders (always render neutral/blue until filled in - needs the user's own game-balance
  judgment).
- **`armor_db/__init__.py`'s `_NATION_MODULES` dict must list every nation key actually present in
  `vehicles.json`**, or `getVehicleArmor()` silently returns `None` for that nation's vehicles even
  though data exists for them. This exact gap existed in the parent repo (only `germany`/`ussr` were
  wired despite `france`/`uk`/`usa` already having JSON data) and was fixed when this repo was
  created - if you add a new nation's data, remember this step.
- Whitelisted vehicles as of the initial extraction (2026-09-26): whatever nations/vehicles were in
  `armor_data/vehicles.json` at that time - check the JSON directly rather than trusting a
  hardcoded list here, it will go stale as vehicles get added.

## Runtime architecture (src/armorangle/)

- `armor_math.py` - all actual math, zero BigWorld deps, fully unit-testable. Core function
  `plateIncidenceDeg(...)`. Also has 5deg flat shell-normalization (AP-only), UI-slot classification
  (`classifyFrontPlate`/`classifySidePlate`/`UI_SLOTS`), and the color-category resolver.
- `armor_db/__init__.py` - `ArmorPlate`/`VehicleArmor` namedtuples, `mirroredPair()` helper,
  `getVehicleArmor()` (lazy per-nation import).
- `armor_db/<nation>.py`, `armor_db/tier_thresholds.py` - GENERATED, don't hand-edit.
- `armor_angle_hud.py` - the only file touching `GUI`/`BigWorld`. Creates 8 independent `GUI.Text`
  components (one per grid slot) at a FIXED screen position computed once at creation
  (`config.py`'s `positionX`/`positionY` + per-slot column/row offset) - NOT dynamically tracking
  the reticle (this was deliberately fixed after an earlier reticle-tracking attempt broke badly in
  sniper mode - see the comment block in this file). A slot with nothing to show is just hidden.
- `config.py` - minimal standalone replacement for what used to be 4 files
  (`config_param.py`/`config_file.py`/`config_template.py`/`migrations.py`) in the parent project.
  No version migrations (this is a fresh v1 config) - unknown/missing keys just fall back to
  `DEFAULTS`. `g_config.onReload` is a plain list of callables (not a full Event framework) invoked
  at the end of `reload()`.
- `hooks.py` - two direct, explicit monkey-patches (not a generic `overrideIn` decorator, since
  there are only two things to hook): `VehicleGunRotator.start`/`.stop` tied to
  `g_armorAngleHud.start()`/`.stop()`, and `game.handleKeyEvent` for the CTRL+P config-reload
  hotkey.
- `mod_ArmorAngleHUD.py` - minimal `init()`/`fini()` entry point. **Deliberately does NOT** show an
  in-game error dialog on failure (that required `BWUtil`/`DialogsInterface`/`realm` - out of scope
  for "only armor calculation and display"); failures only surface in the game's script log
  (`python.log`, or `game.log` - see Environment facts above).

## Deliberately NOT included (compared to the parent project)

- No reticle code, no Flash/SWF, no `gui/` resource tree.
- No ModsSettingsAPI / Mod Configurator settings page - config is edit-the-JSON-file + CTRL+P reload
  only. If the user ever wants a GUI settings page back, that's a new soft-dependency integration to
  design from scratch here, not a straightforward port (the parent project's version is tightly
  coupled to its own config-param abstraction).
- No config version-migration framework - if the config schema changes in a breaking way, decide at
  that time whether a migration path is actually needed (probably not, given how few settings exist)
  or if a "reset to new defaults" note is good enough.
- No in-game error dialog on init failure - the game's script log only.
- No multi-language translations (in-game HUD text is intentionally ASCII/English only anyway, same
  reasoning as the parent project: the target client is English even though the user communicates in
  Chinese).

## Known-unverified things (flag clearly if you touch them, don't silently assume they're fine)

- E-75's internal name and armor data (if present in `vehicles.json`) - never confirmed against a
  live client, inherited unverified from the parent project.
- Whether `vehicleTypeDescriptor.type.level` really is the 1-10 tier - a one-time diagnostic log
  line exists in `armor_angle_hud.py` (`vehicleTypeDescriptor.type.level = ...`, seen firing
  correctly on 2026-09-26, e.g. `level = 6` for one battle - still not cross-checked against which
  specific vehicle/tier that was, so treat the *mapping* as unconfirmed even though the line itself
  fires).
- Most tiers still have no color threshold values in `tier_thresholds.json`.
- **Live-verified on 2026-09-26** (client 2.4.0.1, via `game.log`): mod package loads, `init()` runs,
  `config.py` creates the default file and reloads it correctly (`enabled` flipping from `False` to
  `True` across a restart was picked up), and the `VehicleGunRotator` hook in `hooks.py` fires (HUD
  ticked, correctly identified an off-whitelist vehicle via `getVehicleArmor`). **Not yet
  specifically isolated**: whether the CTRL+P hotkey path in `hooks.py` (as opposed to a full game
  restart) actually triggers a live mid-session reload - the observed `enabled` flip could have come
  from either. Confirm this distinctly next time before treating the hotkey as verified.

## Working style established in this project (keep doing this)

- Before claiming anything works, actually verify it: compile with real Python 2.7, write a
  standalone import-based test script for anything BigWorld-free, and for anything touching
  BigWorld, build and ask the user to test in-game and report back the game's script log output
  (check both `python.log` and `game.log` - don't assume which one a given client version uses).
- When something can't be verified in this environment, say so explicitly and give the user a
  concrete way to verify it live, rather than presenting a guess as fact.
- Prefer asking a clarifying question over guessing when a design decision is genuinely the user's
  call (game-balance numbers, UI layout, scope cuts like "do we need a GUI settings page").
- This repo and `DispersionReticle_with_armor_angle` are separate projects now - don't assume a fix
  made in one should automatically apply to the other; ask if it's unclear whether the user wants a
  change ported both ways.
