import logging

from lib.settings import global_settings

logger = logging.getLogger('linux-autosetup')


# TODO: move to main init area when ready
def init_settings():
    """Initialize logger settings. Should only be called once."""
    logger.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()
    stream_format = logging.Formatter('[%(levelname)s]: %(message)s')
    stream_handler.setFormatter(stream_format)
    stream_handler.setLevel(logging.DEBUG if global_settings.options.debug else logging.INFO)

    logger.addHandler(stream_handler)


init_settings()


def log(msg: str, lvl: int):
    # TODO: figure out stylizing text?
    msg = msg.replace('\n', '\n\t')
    logger.log(lvl, msg)
