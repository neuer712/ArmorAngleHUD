import logging

import Keys
import game
from VehicleGunRotator import VehicleGunRotator

from armorangle.armor_angle_hud import g_armorAngleHud
from armorangle.config import g_config

logger = logging.getLogger(__name__)


###########################################################
# Only two things need hooking here, so this is two direct,
# explicit monkey-patches instead of a generic decorator -
# no debug-mode machinery, this feature never needed it.
###########################################################

_originalGunRotatorStart = VehicleGunRotator.start
_originalGunRotatorStop = VehicleGunRotator.stop


def _hookedGunRotatorStart(self):
    _originalGunRotatorStart(self)

    g_armorAngleHud.start()
    g_config.onReload.append(g_armorAngleHud.refreshFromConfigReload)


def _hookedGunRotatorStop(self):
    if g_armorAngleHud.refreshFromConfigReload in g_config.onReload:
        g_config.onReload.remove(g_armorAngleHud.refreshFromConfigReload)
    g_armorAngleHud.stop()

    _originalGunRotatorStop(self)


VehicleGunRotator.start = _hookedGunRotatorStart
VehicleGunRotator.stop = _hookedGunRotatorStop


###########################################################
# CTRL + P reloads config.json, same hotkey convention as the
# DispersionReticle mod this feature was originally built on top of.
###########################################################

_originalHandleKeyEvent = game.handleKeyEvent


def _hookedHandleKeyEvent(event):
    hotkeyPressed = event.isKeyDown() and event.isCtrlDown() and event.key == Keys.KEY_P

    if not hotkeyPressed:
        return _originalHandleKeyEvent(event)

    logger.info("[ArmorAngleHUD] Reloading config ...")
    g_config.reload()


game.handleKeyEvent = _hookedHandleKeyEvent
