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
        except Exception:
            log(logging.ERROR, f'Encountered an error while trying to read config!')
            raise

        if not isinstance(config, dict):
            return {}
        return config

    @staticmethod
    def assert_tp(mapping: dict, key: str, tp, default=None):
        """
        Asserts that a setting is of some type and return it, or a default value if it does not exist.

        Written to work mainly with basic config value types like str, int, and dict (non-exhaustive).
        More complex types may not behave as expected.
        """
        if default is None:
            default = tp()
        val: tp = mapping.get(key, default)
        if isinstance(val, tp):
            val: tp
            return val
        else:
            log(logging.ERROR, f'Unexpected type given for settings. Expected {key} value to be of type {tp}, '
                                 f'but got {val.__class__.__name__}')
            raise TypeError
