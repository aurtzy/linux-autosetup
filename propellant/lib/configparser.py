import logging
import typing
from os import PathLike

from ruamel.yaml import YAML, YAMLError

from .logger import log


class ConfigParser:

    def __init__(self, config_path: typing.Union[str, PathLike]):
        self.config_path = config_path

    def load(self) -> dict:
        """Loads the configuration file from config_path.
        """
        yaml = YAML(typ='safe')

        log(f'Reading from config: {self.config_path}', logging.INFO)
        try:
            with open(self.config_path, 'r') as file:
                config: dict = yaml.load(file)

            assert isinstance(config, dict)

            return config
        except FileNotFoundError:
            log('File could not be found at:\n'
                f'{self.config_path}', logging.CRITICAL)
            raise
        except AssertionError:
            log('Looks like the configuration file might be empty?', logging.CRITICAL)
        except YAMLError as error:
            log('Encountered an error reading config:\n'
                f'{error}', logging.CRITICAL)
            raise
