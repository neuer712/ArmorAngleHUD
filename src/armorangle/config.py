# -*- coding: utf-8 -*-
import json
import logging
import os
import re

logger = logging.getLogger(__name__)

CONFIG_FILE_DIR = os.path.join("mods", "configs", "ArmorAngleHUD")
CONFIG_FILE_PATH = os.path.join(CONFIG_FILE_DIR, "config.json")

DEFAULTS = {
    "enabled": False,
    "position-x": 0.0,
    "position-y": -0.1,
    "debug-mode": False
}

CONFIG_TEMPLATE = """{
    // Configs can be reloaded in game using hotkey: CTRL + P
    // To generate default config again, delete this file and reload with the hotkey above
    // (or just launch the game again).

    // ArmorAngleHUD (experimental, opt-in, whitelist-only)
    //
    // Shows a plain text HUD estimating, for a short whitelist of vehicles,
    // what your OWN hull's armor incidence angle would be if an enemy were
    // positioned along your current aim direction. Displayed as a grid of
    // up to 8 slots at a FIXED screen position (left/right side upper+lower,
    // left/right pike cheek, front upper+lower) - not dynamically tracking
    // the reticle, since the reticle itself is already at a fixed screen
    // spot in both sniper and arcade view.
    //
    // This is a rough approximation:
    // - only vehicles with hand-filled armor data in this mod's whitelist are supported;
    //   for any other vehicle, this HUD simply stays hidden
    // - "equivalent thickness" ignores shell normalization and 3x caliber overmatch,
    //   because the incoming shell's caliber is unknown
    // - ignores terrain pitch (uphill/downhill), tracks/spaced armor

    // Valid values: true/false (default: false)
    //
    // If true, displays this HUD for whitelisted vehicles.
    "enabled": %(enabled)s,

    // Valid values: number between -1.0 and 1.0 (default: 0.0)
    //
    // Horizontal position of the HUD grid's center column, in screen
    // clip space (-1 = left edge, 1 = right edge). 0 = horizontally centered.
    "position-x": %(position-x)s,

    // Valid values: number between -1.0 and 1.0 (default: -0.1)
    //
    // Vertical position of the HUD grid's row 1, in screen clip space
    // (-1 = bottom edge, 1 = top edge). Row 2 is drawn further below this.
    "position-y": %(position-y)s,

    // Valid values: true/false (default: false)
    //
    // If false (default), each slot only shows the incidence angle
    // number, or "RICOCHET" if it would ricochet.
    // If true, also shows PEN/RICOCHET status text and the approximate
    // effective thickness in mm - more detail, more clutter.
    "debug-mode": %(debug-mode)s
}"""


def _clamp(minValue, value, maxValue):
    return max(minValue, min(value, maxValue))


class ConfigException(Exception):
    pass


class Config(object):
    """
    Minimal standalone JSON config - no ModsSettingsAPI, no version
    migrations (this is a fresh v1 file). Missing/invalid keys just fall
    back to DEFAULTS. Reload is triggered by the CTRL+P hotkey, wired up
    in hooks.py, same convention as the DispersionReticle mod this feature
    was originally built on top of.
    """

    def __init__(self):
        self.enabled = DEFAULTS["enabled"]
        self.positionX = DEFAULTS["position-x"]
        self.positionY = DEFAULTS["position-y"]
        self.debugMode = DEFAULTS["debug-mode"]

        # plain callables, invoked with no arguments at the end of reload()
        self.onReload = []

    def reload(self):
        try:
            self._createDefaultFileIfMissing()
            configDict = self._loadConfigDict()

            self.enabled = bool(configDict.get("enabled", DEFAULTS["enabled"]))
            self.positionX = _clamp(-1.0, float(configDict.get("position-x", DEFAULTS["position-x"])), 1.0)
            self.positionY = _clamp(-1.0, float(configDict.get("position-y", DEFAULTS["position-y"])), 1.0)
            self.debugMode = bool(configDict.get("debug-mode", DEFAULTS["debug-mode"]))

            logger.info("[ArmorAngleHUD] Config loaded: enabled=%s position=(%.2f, %.2f) debug-mode=%s",
                        self.enabled, self.positionX, self.positionY, self.debugMode)
        except ConfigException as e:
            logger.error("[ArmorAngleHUD] %s", e.message)
        except Exception:
            logger.error("[ArmorAngleHUD] Failed to load (or create) config due to unknown error.", exc_info=True)

        for callback in self.onReload:
            callback()

    def _createDefaultFileIfMissing(self):
        if os.path.isfile(CONFIG_FILE_PATH):
            return

        if not os.path.isdir(CONFIG_FILE_DIR):
            os.makedirs(CONFIG_FILE_DIR)

        try:
            with open(CONFIG_FILE_PATH, "w") as configFile:
                configFile.write(CONFIG_TEMPLATE % {
                    "enabled": json.dumps(DEFAULTS["enabled"]),
                    "position-x": json.dumps(DEFAULTS["position-x"]),
                    "position-y": json.dumps(DEFAULTS["position-y"]),
                    "debug-mode": json.dumps(DEFAULTS["debug-mode"])
                })
            logger.info("[ArmorAngleHUD] Created default config file at %s", CONFIG_FILE_PATH)
        except Exception:
            raise ConfigException("Failed to write default config file to %s" % CONFIG_FILE_PATH)

    def _loadConfigDict(self):
        try:
            with open(CONFIG_FILE_PATH, "r") as configFile:
                jsonRawData = configFile.read()

            jsonData = re.sub(r"^ *//.*$", "", jsonRawData, flags=re.MULTILINE)
            return json.loads(jsonData, encoding="UTF-8")
        except ValueError as e:
            raise ConfigException("Failed to read config file (probably invalid JSON syntax): " + e.message)
        except Exception:
            raise ConfigException("Failed to read config file due to unknown error.")


g_config = Config()
