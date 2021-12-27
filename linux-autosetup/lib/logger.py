import logging

logger = logging.getLogger('linux-autosetup')
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_format = logging.Formatter('%(name)s:%(message)s')
stream_handler.setFormatter(stream_format)

logfile_handler = logging.FileHandler(filename='logfile')

logger.addHandler(stream_handler)


def log(msg: str, lvl: int):
    msg = msg.replace('\n', '\n\t')
    logger.log(lvl, f' {msg}')
