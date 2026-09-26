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
  building, deploying, and having the user test in a training room and read back `python.log`.
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
  for "only armor calculation and display"); failures only surface in `python.log`.

## Deliberately NOT included (compared to the parent project)

- No reticle code, no Flash/SWF, no `gui/` resource tree.
- No ModsSettingsAPI / Mod Configurator settings page - config is edit-the-JSON-file + CTRL+P reload
  only. If the user ever wants a GUI settings page back, that's a new soft-dependency integration to
  design from scratch here, not a straightforward port (the parent project's version is tightly
  coupled to its own config-param abstraction).
- No config version-migration framework - if the config schema changes in a breaking way, decide at
  that time whether a migration path is actually needed (probably not, given how few settings exist)
  or if a "reset to new defaults" note is good enough.
- No in-game error dialog on init failure - `python.log` only.
- No multi-language translations (in-game HUD text is intentionally ASCII/English only anyway, same
  reasoning as the parent project: the target client is English even though the user communicates in
  Chinese).

## Known-unverified things (flag clearly if you touch them, don't silently assume they're fine)

- E-75's internal name and armor data (if present in `vehicles.json`) - never confirmed against a
  live client, inherited unverified from the parent project.
- Whether `vehicleTypeDescriptor.type.level` really is the 1-10 tier - a one-time diagnostic log
  line exists in `armor_angle_hud.py` (`vehicleTypeDescriptor.type.level = ...` in `python.log`).
- Most tiers still have no color threshold values in `tier_thresholds.json`.
- The standalone `config.py`/`hooks.py` written for this extraction have NOT yet been verified
  live in-game (no BigWorld available in this dev environment) - only the pure `armor_math`/
  `armor_db` logic and the `build_wotmod.py` zip output have been verified so far. Treat the
  config-reload hotkey and the `VehicleGunRotator` hook wiring as unverified until the user reports
  back from an actual training-room test with `python.log` in hand.

## Working style established in this project (keep doing this)

- Before claiming anything works, actually verify it: compile with real Python 2.7, write a
  standalone import-based test script for anything BigWorld-free, and for anything touching
  BigWorld, build and ask the user to test in-game and report back `python.log` output.
- When something can't be verified in this environment, say so explicitly and give the user a
  concrete way to verify it live, rather than presenting a guess as fact.
- Prefer asking a clarifying question over guessing when a design decision is genuinely the user's
  call (game-balance numbers, UI layout, scope cuts like "do we need a GUI settings page").
- This repo and `DispersionReticle_with_armor_angle` are separate projects now - don't assume a fix
  made in one should automatically apply to the other; ask if it's unclear whether the user wants a
  change ported both ways.
