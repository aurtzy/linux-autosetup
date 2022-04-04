import abc
import logging
import typing
from dataclasses import dataclass, field, MISSING, fields
from os import PathLike

from .logger import log


config: dict[str, dict] = {}


class Settings(abc.ABC):
    """
    This class provides an API for using settings with the script.

    It is meant to allow an initialization period for additional actions to take place when
    translating from the configparser to settings that are to be used during runtime,
    as some data written to config files should and have to be checked in order for other things to function.

    The Settings class mainly provides the following:
        - A class argument "keys", which can be used when creating subclasses to
          easily designate the location that settings for a particular class will be found.

        - Hooks to this class for initialization that are automatically ordered
          based on which subclass is imported first from modules.

        - An implementable initialize_settings method that is to be called during the initialization period.

    Subclasses of Settings can have the same key configuration; however
    an error will occur if the elements within these key configs overlap.
    """

    __keys__: tuple[str] = tuple()

    __hooks__: list[typing.Type["Settings"]] = []

    def __init_subclass__(cls, keys: tuple[str], **kwargs):
        """
        Assigns keys to the subclass of Settings
        and adds a hook to the list of hooks in Settings.
        """
        super().__init_subclass__(**kwargs)
        cls.__keys__ = keys
        cls.__hooks__.append(cls)

    @classmethod
    def __initialize__(cls, new_config: dict):
        """
        Initializes settings for all Settings hooks and adds
        each configuration dictionary to the corresponding key config in config.

        Settings may be part of the same key configs and will simply combine; however
        overlapping elements within key configs are not permitted.

        :raises AssertionError: if there is an overlap of elements in at least one key config.
        """
        for hook in cls.__hooks__:
            key_config = hook.get_key_config()

            new_key_config = hook.initialize_settings(hook.get_key_config(new_config))
            if key_config:
                for key in new_key_config.keys():
                    assert key not in key_config.keys(), (
                            f'Tried to update config with {hook.__name__} settings, '
                            f'but there was an overlap with the key {key}.')
            key_config.update(new_key_config)

    @classmethod
    def get_key_config(cls, settings: dict = None) -> dict:
        """
        Gets the relevant key config from a dictionary of settings, returning the dict result
        of parsing through __keys__ levels of settings.

        If the settings argument is not specified, global config will be used.
        """
        if settings is None:
            settings = config

        for key in cls.__keys__:
            settings = settings.setdefault(key, {})
            if not isinstance(settings, dict):
                log(f'Expected a dict while retrieving the key {key} value from given settings.\n'
                    f'{settings}', logging.ERROR)
                raise ValueError
        return settings

    @classmethod
    @abc.abstractmethod
    def initialize_settings(cls, new_settings: dict) -> dict:
        """
        Parses the given dict of new settings and performs any necessary initialization actions.
        :return: A formatted dictionary to be added to config.
        """
        pass


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

    @dataclass
    class CustomModule(BaseSettings):
        """
        Designated settings for the custom module.

        cmd_presets:
            Dictionary of name -> CmdPreset pairs.
        """
        # TODO: move to Basic Pack Module settings
        cmd_presets: dict[str, CmdPreset] = field(default_factory=dict)

    @dataclass
    class AppsModule(CustomModule):
        """
        Designated settings for the apps module.
        """
        pass

    @dataclass
    class FilesModule(CustomModule):
        """
        Designated settings for the files module.

        backup_dirs:
            Directories that are used for creating and extracting backups from.
            Dictionary of name -> PathLike pairs.
        dump_dirs:
            Directories that can be used for dumping old backups.
            Dictionary of name -> PathLike pairs.
        tmp_dirs:
            Directories that can be used for storing backups that are in the process of being created.
            Dictionary of name -> PathLike pairs.
        """
        # TODO: move to Files Pack Module settings
        backup_dirs: dict[str, PathLike] = field(default_factory=dict)
        dump_dirs: dict[str, PathLike] = field(default_factory=dict)
        tmp_dirs: dict[str, PathLike] = field(default_factory=dict)

    system_cmds: SystemCmds = field(default_factory=lambda: GlobalSettings.SystemCmds())
    custom_module: CustomModule = field(default_factory=lambda: GlobalSettings.CustomModule())
    apps_module: AppsModule = field(default_factory=lambda: GlobalSettings.AppsModule())
    files_module: FilesModule = field(default_factory=lambda: GlobalSettings.FilesModule())

    def __str__(self):
        return str(self.__dict__)


global_settings = GlobalSettings()
