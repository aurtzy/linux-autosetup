import logging

logger = logging.getLogger('linux-autosetup')
logger.setLevel(logging.DEBUG)


def set_stream(debug: bool):
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter('[%(levelname)s]: %(message)s'))
    stream_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.addHandler(stream_handler)


def log(msg: str, lvl: int):
    # TODO: figure out stylizing text?

    msg = msg.replace('\n', '\n\t')
    logger.log(lvl, msg)
