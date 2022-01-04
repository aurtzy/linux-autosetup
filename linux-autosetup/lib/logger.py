import logging


logger = logging.getLogger('linux-autosetup')


# TODO: move to main init area when ready
def init_settings(debug_mode: bool = False):
    """Initialize logger settings. Should only be called once."""
    logger.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()
    stream_format = logging.Formatter('%(message)s')
    stream_handler.setFormatter(stream_format)
    stream_handler.setLevel(logging.DEBUG if debug_mode else logging.ERROR)

    logfile_handler = logging.FileHandler(filename='logfile', mode='w')
    logfile_format = logging.Formatter('%(levelname)s: %(message)s')
    logfile_handler.setFormatter(logfile_format)

    logger.addHandler(stream_handler)
    logger.addHandler(logfile_handler)


init_settings(True)


def log(msg: str, lvl: int):
    # TODO: figure out stylizing text?
    msg = msg.replace('\n', '\n\t')
    logger.log(lvl, msg)
