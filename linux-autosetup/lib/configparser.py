import logging
from os import PathLike

from ruamel.yaml import YAML, YAMLError

from lib.logger import log
from lib.settings import global_settings


class ConfigParser:

    def __init__(self, config_path: PathLike):
        self.config_path = config_path

    def start(self, option_overrides: dict = None):
        """
        Starts the parsing process.

        :param option_overrides: Dictionary of "overrides." This will match against any setting keys in
                                 global_settings['options'] and override the original value from the config file.
                                 This lets the script prefer script arguments over config settings.
        """
        if option_overrides is None:
            option_overrides = {}

        yaml = YAML(typ='safe')
        log('Reading config file...', logging.DEBUG)
        try:
            with open(self.config_path, 'r') as file:
                config: dict = yaml.load(file)
                file.close()
        except YAMLError as error:
            log('Encountered an error reading config.', logging.CRITICAL)
            log(str(error), logging.CRITICAL)
            exit(1)
        log(str(config), logging.DEBUG)

        try:
            assert isinstance(config, dict)
        except AssertionError:
            if config is None:
                log(f'Could not find anything in {self.config_path}. Exiting...',
                    logging.ERROR)
            else:
                log(f'Encountered an unexpected error trying to parse {self.config_path}. Exiting...',
                    logging.ERROR)
            exit(1)

        log('Parsing global settings...', logging.DEBUG)
        self.parse_settings(config.get('global_settings'))

        log('Checking for any global options to override...', logging.DEBUG)
        global_settings.options.__dict__.update(option_overrides)
        for option, val in option_overrides.items():
            log(f'Overriding {option}: {val}', logging.INFO)

        log('Parsing packs...', logging.DEBUG)
        self.parse_packs(config.get('packs'))

    def parse_settings(self, s: dict):
        """Specifically parses for and updates global_settings from the given dict s."""
        # TODO: parse given dictionary of global settings
        pass

    def parse_packs(self, p: dict):
        """Specifically parses for and creates packs from the given dict p."""
        # TODO: parse given dictionary of packs
        pass
