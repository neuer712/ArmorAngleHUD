# ArmorAngleHUD

A standalone World of Tanks Python client mod. It shows a small on-screen HUD estimating **your
own vehicle's hull armor incidence angle**, assuming a hypothetical enemy positioned along your
current aim direction - a defensive "am I angled enough" tool, not an offensive penetration
calculator. It does not read enemy vehicles, does not calculate whether you can penetrate anyone,
and does not touch reticle/aiming behavior at all.

This project is inspired by an add-on originally built on top of Pruszko's
[DispersionReticle](https://github.com/Pruszko/DispersionReticle) mod (MIT licensed), but it is an
**independent, unaffiliated project** - it does not include DispersionReticle's reticle code, its
Flash UI, or its Mod Configurator integration, and is not endorsed by or associated with Pruszko.

## What it shows

For a whitelisted list of vehicles (see `armor_data/vehicles.json`), a fixed grid of up to 8 text
slots near your reticle (left/right side upper+lower, left/right pike cheek, front upper+lower)
showing either:
- the approximate effective thickness in mm along your current aim line, or
- `RICOCHET` if the shot would ricochet at that angle.

Grid position alone identifies which plate a number belongs to - a slot with nothing to show is
just hidden, it never shifts other slots around. A vehicle not in the whitelist simply shows
nothing.

This is a rough approximation:
- only vehicles with hand-filled armor data in `armor_data/vehicles.json` are supported
- "equivalent thickness" ignores shell normalization bonus and 3x caliber overmatch, because the
  incoming shell's caliber is unknown
- ignores terrain pitch (uphill/downhill), tracks, and spaced armor

## Known-unverified things

- E-75's internal name and armor data have never been confirmed against a live client.
- Whether `vehicleTypeDescriptor.type.level` really is the 1-10 tier is logged once per session
  (`python.log`, search for `vehicleTypeDescriptor.type.level =`) but not independently confirmed.
- Most tiers have no color threshold values yet in `armor_data/tier_thresholds.json` (only tiers 7
  and 8 have real numbers) - other tiers always render the neutral/safe color.
- Only German and Soviet heavies have been entered so far; the data model supports pike/wedge nose
  armor (multiple front plates at nonzero bearing) but few vehicles using it have been added.

## Building

Requires Python 2.7 (WoT's embedded interpreter) - the same one you'd use to test any BigWorld
client mod. No other dependencies.

```
build.bat
```

This regenerates `src/armorangle/armor_db/*.py` from `armor_data/*.json` (see
`generate_armor_db.py`), compiles everything, and packages
`build/laiwei.armor_angle_hud_dev.wotmod` (gitignored build output).

To deploy, copy that `.wotmod` file into your WoT install's
`mods\<client version>\` folder (find the current version folder name under your WoT install
directory). The game must be closed while copying, or the file may be locked.

## Configuring

On first run, a config file is created at `mods\configs\ArmorAngleHUD\config.json` (relative to
your WoT install directory), with the default settings commented inline. Edit it and reload with
**CTRL + P** in-game, or just restart the game.

There is no in-game settings page (no ModsSettingsAPI dependency) - the config file is the only way
to change settings.

## Adding vehicles / adjusting armor data

Edit `armor_data/vehicles.json` (per-vehicle plate data) or `armor_data/tier_thresholds.json`
(per-tier color thresholds), then rebuild - `build.bat` regenerates the Python armor database from
the JSON automatically. See the docstring at the top of `generate_armor_db.py` for the full JSON
schema and labeling conventions.

## Running alongside other armor-angle HUDs

If you also have a build of the DispersionReticle-based armor angle feature installed with its own
armor-angle setting enabled, you'll get two overlapping HUDs on screen at once - disable one before
testing the other.

## License

MIT - see `LICENSE`.
