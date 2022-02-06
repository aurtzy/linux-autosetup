# import logging

from ruamel.yaml import YAML, YAMLError

from .lib.configparser import ConfigParser
from .lib.logger import log, set_stream
from .lib.system import Path
from .lib.user_input import get_setup_mode


def run():
    set_stream(debug=True)
    config_path = Path('sample-configs/config.yaml')

    config_parser = ConfigParser(config_path)
    config_parser.start()

    print(get_setup_mode())
