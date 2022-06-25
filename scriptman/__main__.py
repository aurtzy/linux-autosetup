import logging

import scriptman
from scriptman import log

if __name__ == '__main__':
    try:
        scriptman.run_module()
    except Exception as error:
        log(logging.DEBUG, '', exc_info=True)
        log(logging.CRITICAL, str(error))
    except KeyboardInterrupt:
        exit()
