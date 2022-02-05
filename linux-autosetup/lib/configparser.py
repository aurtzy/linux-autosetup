import logging
from dataclasses import is_dataclass, fields
from os import PathLike

from ruamel.yaml import YAML, YAMLError

from lib.logger import log
from lib.settings import global_settings, BaseSettings
from lib.system import Path


class ConfigParser:

    def __init__(self, config_path: PathLike):
        self.config_path = config_path

    @staticmethod
    def update_global_settings(new_settings: dict):
        """Recursively parses s to update global_settings."""
        def update_level(settings: BaseSettings, new: dict):
            for setting, tp in settings.__annotations__.items():
                log(f'LEVEL:\n'
                    f'{setting}: {new.get(setting)}', logging.DEBUG)
                if new.get(setting) is None:
                    log(f'No setting found for {setting}.', logging.DEBUG)
                    continue

                if tp.__subclasscheck__(dict):
                    try:
                        dict_args: tuple = tp.__args__
                    except AttributeError:
                        dict_args: tuple = ()
                    log(f'dict_args: {dict_args}', logging.DEBUG)
                    if isinstance(new.get(setting), dict):
                        # Update dictionary
                        log(f'Updating {setting} dictionary...', logging.DEBUG)
                        for k, v in new.get(setting).items():
                            if len(dict_args) > 0:
                                log(f'Converting {k} to {dict_args[0]}...', logging.DEBUG)
                                k = dict_args[0](k)  # Converts k into correct type
                                if len(dict_args) > 1:
                                    # Assign v depending on desired type. Add elifs for specific types here
                                    # if a more tuned value is desired.
                                    log(f'Converting {v} to {dict_args[1]}...', logging.DEBUG)
                                    if is_dataclass(dict_args[1]):
                                        if isinstance(v, dict):
                                            v = dict_args[1](*(v.get(fld.name) for fld in fields(dict_args[1])))
                                        else:
                                            log(f'Unexpected value given for {setting}:\n'
                                                f'({k}, {v}).\n'
                                                f'Ignoring...', logging.ERROR)
                                    elif dict_args[1] is PathLike:
                                        v = Path.valid_dir(str(v))
                                    else:
                                        v = dict_args[1](v)
                            getattr(settings, setting).update({k: v})
                            log(f'Updated {setting}:\n'
                                f'{k}: {v}', logging.INFO)
                elif is_dataclass(tp):
                    # Update dataclass
                    if isinstance(new.get(setting), dict):
                        log(f'Updating {setting}...', logging.INFO)
                        update_level(getattr(settings, setting), new.get(setting))
                    else:
                        log(f'Unexpected value given for {setting}:\n'
                            f'{new.get(setting)}\n'
                            f'Ignoring...', logging.ERROR)
                else:
                    # Update misc. types
                    if isinstance(new.get(setting), tp):
                        setattr(settings, setting, new.get(setting))
                        log(f'Updated {setting}:\n'
                            f'{getattr(settings, setting)}', logging.INFO)
                    else:
                        log(f'Unexpected value given for {setting}; expected {tp} but got {type(new.get(setting))}:\n'
                            f'{new.get(setting)}\n'
                            f'Ignoring...', logging.ERROR)
        update_level(global_settings, new_settings)

    @staticmethod
    def init_packs(p: dict):
        """Specifically parses for and creates packs from the given dict p."""
        # TODO: parse given dictionary of packs
        pass

    def start(self):
        """
        Starts the parsing process.

        Due to needing to be run very early in the script, global options should not be
        """

        yaml = YAML(typ='safe')
        log(f'Reading from config: {self.config_path}', logging.INFO)
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
                log(f'Could not find anything in {self.config_path}.',
                    logging.ERROR)
            else:
                log(f'Encountered an unexpected error trying to parse {self.config_path}.',
                    logging.ERROR)
            exit(1)

        log('Registering global settings...', logging.DEBUG)
        self.update_global_settings(config.get('global_settings'))

        log('Parsing packs...', logging.DEBUG)
        self.init_packs(config.get('packs'))
