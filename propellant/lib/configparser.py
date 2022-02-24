import logging
from dataclasses import is_dataclass, fields
from os import PathLike, path, fspath, environ

from ruamel.yaml import YAML, YAMLError

from .logger import log
from .pack import Module, BaseModule, Pack
from .settings import global_settings, BaseSettings
from .system import Path


environ.update({'DOLLARSIGN': '$'})


class ConfigParser:

    def __init__(self, config_path: PathLike | str):
        self.config_path = config_path

    @staticmethod
    def unexpected_val_error(setting: str, debug):
        log(f'Unexpected value given for {setting}:\n'
            f'{debug}', logging.ERROR)
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
        """
        Recursively parses the passed dictionary to update global_settings.

        In the case that a setting is not present, but is set to None,
        a warning will be logged.
        """
        log('Parsing global settings...', logging.INFO)
        log(str(new_settings), logging.DEBUG)

        def update_level(settings: BaseSettings, new: dict):
            for setting, tp in settings.__annotations__.items():
                if new.get(setting) is None:
                    if getattr(settings, setting) is None:
                        log(f'The {setting} setting does not any setting.\n'
                            f'This may or may not result in issues.', logging.WARNING)
                    else:
                        log(f'No setting found for {setting}.', logging.DEBUG)
                    continue

                if is_dataclass(tp):
                    # Update dataclass
                    if isinstance(new.get(setting), dict):
                        log(f'Updating {setting}...', logging.DEBUG)
                        update_level(getattr(settings, setting), new.get(setting))
                    else:
                        cls.unexpected_val_error(setting, new.get(setting))
                elif tp.__subclasscheck__(dict):
                    # Update dictionary
                    try:
                        dict_args: tuple = tp.__args__
                    except AttributeError:
                        dict_args: tuple = ()
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
                                            v = dict_args[1](**{fld.name: v.get(fld.name)
                                                                for fld in fields(dict_args[1])})
                                        else:
                                            cls.unexpected_val_error(setting, f'{k}: {v}')
                                    elif dict_args[1] is PathLike:
                                        v = Path.valid_dir(path.expandvars(fspath(v)))
                                    else:
                                        v = dict_args[1](v)
                            getattr(settings, setting).update({k: v})
                            log(f'Updated {setting}:\n'
                                f'{k}: {v}', logging.DEBUG)
                    else:
                        cls.unexpected_val_error(setting, new.get(setting))
                elif tp.__subclasscheck__(list):
                    # Update list
                    try:
                        list_args: tuple = tp.__args__
                    except AttributeError:
                        list_args: tuple = ()
                    if list_args[0] is str:
                        setattr(settings, setting, cls.convert_to_str_list(new.get(setting)))
                        log(f'Updated {setting}:\n'
                            f'{getattr(settings, setting)}', logging.DEBUG)
                    else:
                        log(f'Support for global setting lists with types {tp} is not implemented. '
                            f'Implement in {__name__}.', logging.ERROR)
                        raise NotImplementedError
                else:
                    # Update misc. types
                    if isinstance(new.get(setting), tp):
                        setattr(settings, setting, new.get(setting))
                        log(f'Updated {setting}:\n'
                            f'{getattr(settings, setting)}', logging.DEBUG)
                    else:
                        cls.unexpected_val_error(setting,
                                                 f'Expected {tp} but got {type(new.get(settings))}')
        update_level(global_settings, new_settings)
        log('Finished updating global settings.', logging.INFO)

    @classmethod
    def init_packs(cls, p: dict):
        """Specifically parses for and creates packs from the given dict."""
        log('Initializing packs...', logging.INFO)
        log(str(p), logging.DEBUG)

        for name, pack_settings in p.items():
            if isinstance(pack_settings, dict) and pack_settings:
                log(f'Initializing pack {name}...', logging.DEBUG)
                # desc
                desc = str(pack_settings.get('desc'))

                # modules
                modules: list[BaseModule] = []
                for module_settings in pack_settings.get('modules'):
                    if not isinstance(module_settings, dict):
                        cls.unexpected_val_error(name,
                                                 f'Module settings were incorrectly formatted?')
                    elif not hasattr(Module, module_settings.get('module')):
                        cls.unexpected_val_error(name,
                                                 f'Module {pack_settings.get("module")} could not be found.')
                    module_tp: BaseModule.__class__ = getattr(Module, module_settings.get('module')).value

                    module_fields: dict = {}
                    for setting, tp in module_tp.__annotations__.items():
                        if tp.__subclasscheck__(list):
                            # list types
                            try:
                                list_args: tuple = tp.__args__
                            except AttributeError:
                                list_args: tuple = ()
                            if len(list_args) > 0:
                                if list_args[0] is str:  # TODO: bug; arguments aren't being correctly assigned; also **module_fields instead
                                    module_fields.update(
                                        {setting: cls.convert_to_str_list(module_settings.get(setting))})
                                else:
                                    log(f'Converting to list with type {list_args[0]} is not implemented.\n'
                                        f'Implement in {__name__}.', logging.ERROR)
                                    raise NotImplementedError
                            else:
                                module_fields.update({setting: list(module_settings.get(setting))})
                        else:
                            # misc. types
                            module_fields.update({setting: tp(module_settings.get(setting))})
                    module: BaseModule = module_tp(**module_fields)
                    log(f'Initialized {module.__class__.__name__} for {name}:\n'
                        f'{module}', logging.DEBUG)
                    modules.append(module)

                # pin
                if pack_settings.get('pin'):
                    if not isinstance(pack_settings.get('pin'), int):
                        cls.unexpected_val_error(name,
                                                 f'Expected type {int} but got {pack_settings.get("pin")}.')
                    pin = pack_settings.get('pin')
                else:
                    pin = 0

                Pack(name=name, desc=desc, modules=modules, pin=pin)
            else:
                cls.unexpected_val_error(name, 'Pack settings were incorrectly formatted?')

        log(f'Finishing up initializing packs...', logging.INFO)
        for pack in Pack.packs:
            pack.__post_packs_init__()
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
            raise

        try:
            assert isinstance(config, dict)
        except AssertionError:
            if config is None:
                log(f'Could not find anything in {self.config_path}.',
                    logging.ERROR)
            else:
                log(f'Encountered an unexpected error trying to parse {self.config_path}.',
                    logging.ERROR)
            raise

        self.update_global_settings(config.get('global_settings'))

        self.init_packs(config.get('packs'))
