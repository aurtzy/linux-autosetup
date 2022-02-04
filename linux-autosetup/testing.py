import logging

from ruamel.yaml import YAML, YAMLError

from lib.configparser import ConfigParser
from lib.logger import log
from lib.system import Path

if __name__ == '__main__':

    config_path = Path('sample-configs/config.yaml')

    config_parser = ConfigParser(config_path)

    config_parser.start()
