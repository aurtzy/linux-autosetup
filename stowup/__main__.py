import logging

import stowup
from stowup.lib.logger import log

if __name__ == '__main__':
    try:
        stowup.main()
    except Exception as error:
        log(logging.DEBUG, '', exc_info=True)
        log(logging.CRITICAL, str(error))
    except KeyboardInterrupt:
        exit()
