import logging
import pathlib

from ruamel.yaml import YAML

from .logger import log


class ConfigParser:
    """
    Does config parsing.

    Class format hopefully makes it easy for those looking to swap out parsers for different config types.
    """

    parse = YAML(typ='safe').load

    MAIN_CFG = 'scriptman.yaml'
    MODULE_CFG = 'mod.yaml'

    @classmethod
    def load(cls, config_path) -> dict:
        """
        Loads and returns a dictionary of the configuration file from config_path.

        If parse returns a non-dict, an empty dict is returned.
        """
        try:
            config_path = pathlib.Path(config_path).absolute()
            with open(config_path, 'r') as file:
                config = cls.parse(file)
        except FileNotFoundError:
            log(logging.CRITICAL, f'No such file could be found: {config_path}')
            raise
        except Exception as error:
            log(logging.CRITICAL, f'Encountered an error while trying to read config:\n{error}')
            raise

        if not isinstance(config, dict):
            return {}
        return config
