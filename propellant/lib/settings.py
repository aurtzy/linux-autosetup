import abc
import logging
import typing
from dataclasses import dataclass, field, MISSING, fields
from os import PathLike

from .logger import log


config: dict[str, dict] = {}


class Settings(abc.ABC):
    """
    This class provides a simple API for implementing user_config-to-script settings.

    Its purpose is to add an initialization period for additional actions to take place when
    translating from the configparser to settings that are to be used during runtime, as some
    data written to config files may have to be checked prematurely for the script to function as desired.

    The Settings class mainly provides the following:
        - A class argument "keys", which is used when creating subclasses to
          designate the location that settings for a particular class will be found in the
          user configuration file.

        - Hooks to this class for initialization that are automatically ordered
          based on the import sequence of Python modules.

        - An abstract method initialize_settings() that is called during the initialization period.
    """

    _keys: tuple[str] = ()

    hooks: list[typing.Type["Settings"]] = []

    def __init_subclass__(cls, keys: tuple[str] = (), **kwargs):
        """
        Assigns keys to the subclass of Settings
        and adds a hook to the list of hooks in Settings.
        """
        super().__init_subclass__(**kwargs)
        for hook in cls.hooks:
            if keys == hook._keys[0:len(keys)]:
                log(f'Overlap with existing keys {keys}! Is this intentional?', logging.DEBUG)
        cls._keys = cls._keys + keys
        cls.hooks.append(cls)

    @classmethod
    def get_key_config(cls, **settings) -> dict:
        """
        Gets the relevant key config from a given dictionary of settings.
        :return: A dict obtained from parsing through _keys levels of settings.
        """
        for key in cls._keys:
            settings = settings.get(key, {})
            if not isinstance(settings, dict):
                log(f'Expected a dict while retrieving the key {key} value from given settings.\n'
                    f'{settings}', logging.ERROR)
                raise ValueError
        return settings

    @classmethod
    @abc.abstractmethod
    def initialize_settings(cls, **new_settings):
        """Parses the new_settings argument and performs any initialization actions."""
        pass

    @staticmethod
    def assert_tp(item, tp):
        log(f'Asserting {item} is of type {tp}...', logging.DEBUG)
        assert isinstance(item, tp), f'{item} did not match the type {tp}.'
        return item


def initialize_settings(**new_config):
    """
    Initializes all settings for the subclasses that have hooks in the Settings class.
    """
    for hook in Settings.hooks:
        hook.initialize_settings(**hook.get_key_config(**new_config))


# TODO: EVERYTHING BELOW DEPRECATED. Begin refactoring and following todos.


@dataclass
class GlobalSettings(BaseSettings):
    """
    Global settings.

    system_cmds:
        See SystemCmds docs.
    custom_module:
        See CustomModule docs.
    apps_module:
        See AppsModule docs.
    files_module:
        See FilesModule docs.
    """

    @dataclass
    class SystemCmds(BaseSettings):
        """
        Miscellaneous shell commands used for interacting with the system.

        Preconfigured to use POSIX-compatible GNU/Linux commands.

        superuser:
            Used for elevating commands when appropriate (e.g. sudo).
        cp:
            Used to copy files from one path to another.
            Expects: $1 = target directory; ${@:2} = files to move to target directory
        mv:
            Used to move files from one path to another.
            Expects: $1 = target directory; ${@:2} = files to move to target directory
        mkdir:
            Used to create directories at specified paths.
            Expects: $1 = Path of directory to be made.
        check_path:
            Used to confirm if a path exists to some file/directory.
        check_dir:
            Used to confirm if a path exists to some directory.
        """
        # TODO: move to system module settings
        superuser: str = None
        cp: str = None
        mv: str = None
        mkdir: str = None
        check_path: str = None
        check_dir: str = None

    system_cmds: SystemCmds = field(default_factory=lambda: GlobalSettings.SystemCmds())

    def __str__(self):
        return str(self.__dict__)


global_settings = GlobalSettings()
