import logging
import os
import pathlib

from ruamel.yaml import YAML

from .logger import log


class ConfigParser:
    """
    Does config parsing.

    Class format hopefully makes it easy for those looking to swap out parsers for different config types.
    """

    parse = YAML(typ='safe').load

    def __init__(self, config_path: os.PathLike | str):
        self.config_path = config_path

    def load(self) -> dict:
        """
        Loads and returns a dictionary of the configuration file from config_path.

        If parse returns a non-dict, an empty dict is returned.
        """
        try:
            config_path = pathlib.Path(self.config_path).absolute()
            with open(config_path, 'r') as file:
                config = self.parse(file)
        except Exception:
            log(logging.ERROR, f'Encountered an error while trying to read config!')
            raise

        if not isinstance(config, dict):
            return {}
        return config
