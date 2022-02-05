import logging
from dataclasses import is_dataclass, fields
from os import PathLike

from ruamel.yaml import YAML, YAMLError

from lib.logger import log
from lib.pack import Module, BaseModule
from lib.settings import global_settings, BaseSettings
from lib.system import Path


class ConfigParser:

    def __init__(self, config_path: PathLike):
        self.config_path = config_path

    @staticmethod
    def unexpected_val_error(setting: str, debug):
        log(f'Unexpected value given for {setting}:\n'
            f'{debug}\n'
            f'Exiting...', logging.ERROR)
        raise ValueError

    @staticmethod
    def convert_to_str_list(arg) -> list[str]:
        """
        Converts arg into list[str].

        If arg is a list, return a list with all of its elements passed through str().

        If str(arg) contains no newline characters, delimit into a list by spaces.

        Otherwise, delimit by newline characters.
        """
        log(f'Converting {arg} to list[str]...', logging.DEBUG)
        if arg is None:
            arg = []
        elif isinstance(arg, list):
            arg = [str(element) for element in arg]
        else:
            arg = str(arg)
            if '\n' in arg:
                arg = arg.split('\n')
            else:
                arg = arg.split(' ')
        log(str(arg), logging.DEBUG)
        return arg

    @classmethod
    def update_global_settings(cls, new_settings: dict):
        """Recursively parses s to update global_settings."""
        log('Updating global settings...', logging.INFO)
        log(str(new_settings), logging.DEBUG)

        def update_level(settings: BaseSettings, new: dict):
            for setting, tp in settings.__annotations__.items():
                if new.get(setting) is None:
                    log(f'No setting found for {setting}.', logging.DEBUG)
                    continue

                if is_dataclass(tp):
                    # Update dataclass
                    if isinstance(new.get(setting), dict):
                        log(f'Updating {setting}...', logging.INFO)
                        update_level(getattr(settings, setting), new.get(setting))
                    else:
                        cls.unexpected_val_error(setting, new.get(setting))
                elif tp.__subclasscheck__(dict):
                    # Update dictionary
                    try:
                        dict_args: tuple = tp.__args__
                    except AttributeError:
                        dict_args: tuple = ()
                    log(f'dict_args: {dict_args}', logging.DEBUG)
                    if isinstance(new.get(setting), dict):
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
                                            cls.unexpected_val_error(setting, f'{k}: {v}')
                                    elif dict_args[1] is PathLike:
                                        v = Path.valid_dir(str(v))
                                    else:
                                        v = dict_args[1](v)
                            getattr(settings, setting).update({k: v})
                            log(f'Updated {setting}:\n'
                                f'{k}: {v}', logging.INFO)
                    else:
                        cls.unexpected_val_error(setting, new.get(setting))
                elif tp.__subclasscheck__(list):
                    # Update list
                    try:
                        list_args: tuple = tp.__args__
                    except AttributeError:
                        list_args: tuple = ()
                    log(f'list_args: {list_args}', logging.DEBUG)
                    if list_args[0] is str:
                        setattr(settings, setting, cls.convert_to_str_list(new.get(setting)))
                        log(f'Updated {setting}:\n'
                            f'{getattr(settings, setting)}', logging.INFO)
                    else:
                        log(f'Support for global setting lists with types {tp} does not exist. '
                            f'Add it in the {__name__} module.', logging.ERROR)
                        raise NotImplementedError
                else:
                    # Update misc. types
                    if isinstance(new.get(setting), tp):
                        setattr(settings, setting, new.get(setting))
                        log(f'Updated {setting}:\n'
                            f'{getattr(settings, setting)}', logging.INFO)
                    else:
                        cls.unexpected_val_error(setting,
                                                 f'Expected {tp} but got {type(new.get(settings))}')
        update_level(global_settings, new_settings)
        log('Finished updating global settings.', logging.INFO)

    @classmethod
    def init_packs(cls, p: dict):
        """Specifically parses for and creates packs from the given dict p."""
        log('Initializing packs...', logging.INFO)
        log(str(p), logging.DEBUG)

        for name, pack_settings in p.items():
            if isinstance(pack_settings, dict) and pack_settings:
                # desc
                desc = str(pack_settings.get('desc'))

                # modules
                modules: list[BaseModule] = []
                for module in pack_settings.get('modules'):
                    if not isinstance(module, dict):
                        cls.unexpected_val_error(name,
                                                 f'Module settings were incorrectly formatted?')
                    elif not hasattr(Module, module.get('module')):
                        cls.unexpected_val_error(name,
                                                 f'Module {pack_settings.get("module")} could not be found.')
                    module_type: BaseModule = Module[module.get('module')].value

                    # todo: initialize module

                # pin
                if pack_settings.get('pin'):
                    if isinstance(pack_settings.get('pin'), int):
                        pin = pack_settings.get('pin')
                    else:
                        cls.unexpected_val_error(name,
                                                 f'Expected type {int} but got {pack_settings.get("pin")}.')
                else:
                    pin = 0
            else:
                cls.unexpected_val_error(name, 'Pack settings were incorrectly formatted?')
        log('Finished initializing packs.', logging.INFO)

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

        self.update_global_settings(config.get('global_settings'))

        self.init_packs(config.get('packs'))
