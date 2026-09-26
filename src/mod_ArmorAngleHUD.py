import logging

logger = logging.getLogger(__name__)


def init():
    # try-except with logged exception here is more than important, because
    # when a mod is initialized and some incompatibility occurs, it may break
    # this (or other) mods - see it logged rather than silently corrupting
    # game state.
    try:
        logger.info("Initializing ArmorAngleHUD mod ...")

        # make sure to invoke the hooks
        import armorangle.hooks

        from armorangle.config import g_config
        g_config.reload()

        logger.info("ArmorAngleHUD mod initialized")
    except Exception:
        logger.error("Error occurred while initializing ArmorAngleHUD mod", exc_info=True)


def fini():
    pass
