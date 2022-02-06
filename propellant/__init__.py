import logging

from ruamel.yaml import YAML, YAMLError

from .lib.configparser import ConfigParser
from .lib.logger import log, set_stream
from .lib.system import Path
from .lib.user_input import get_setup_mode

__version__ = '0.0.0-dev'


def test():
    set_stream(debug=True)
    config_path = Path('../sample-configs/config.yaml')

    ConfigParser(config_path).start()

    print(__file__)


def run():
    test()
