import abc
import logging
import typing
from dataclasses import dataclass, field, MISSING, fields
from os import PathLike

from .logger import log


config: dict[str, dict]


class Settings(abc.ABC):
    """
    Implementing this Settings class:
        - The "category" argument keyword must be given a value,
          which will indicate the category of settings it will belong to.

        - Subclasses of Settings can be of the same category, however an error will occur if the elements
          within these categories overlap.

        - The initialize method must be implemented, which should parse the given dictionary
          of values, performing any necessary extra checks and actions,
          and return the desired format of setting-value pairs in a dictionary.
    """

    __hooks__: list[typing.Type["Settings"]] = []

    __category__: str

    def __init_subclass__(cls, category, **kwargs):
        """
        Assigns a config category to the subclass of settings
        and adds a hook to the Settings hooks list.
        """
        super().__init_subclass__(**kwargs)
        cls.__category__ = category
        cls.__hooks__ += cls

    @classmethod
    def initialize(cls, config_dict: dict):
        """
        Initializes settings for all Settings hooks and adds
        each configuration dictionary to the corresponding category in config.

        Categories may overlap and will simply combine, however
        overlapping elements within categories are not permitted.

        :raises AssertionError: if there is an overlap with elements in the categories.
        """
        for hook in cls.__hooks__:
            new_settings = hook.initialize_settings(config_dict.get(hook.__category__, {}))
            if config.get(hook.category) is not None:
                for key in new_settings.keys():
                    assert key not in config[hook.__category__].keys(), (f'Tried to update config with {hook.__name__}'
                                                                         f' settings, but there was an overlap with'
                                                                         f' the key {key}.')
                config[hook.__category__].update(new_settings)
            else:
                config[hook.__category__] = new_settings

    @classmethod
    @abc.abstractmethod
    def initialize_settings(cls, category_dict: dict) -> dict:
        """
        Parses the given category dict and performs any necessary initialization actions.
        :return: A formatted dictionary to be added to config.
        """
        pass


# TODO: EVERYTHING BELOW DEPRECATED. Begin refactoring and following todos.

@dataclass
class CmdPreset(BaseSettings):
    """
    A preset of shell commands.

    pipe:
        Indicates that data should be piped into the shell.
        If True, then the user will be prompted for what will be piped.
        If pipe is a str, then this string will always be piped into the commands.
    install_cmd:
        Meant to be run during pack installs.
    backup_cmd:
        Meant to be run during pack backups.
    """
    # TODO: merge with pack module as part of the Basic Pack Module settings (renamed commands module)
    pipe: bool | str = False
    install_cmd: str = ''
    backup_cmd: str = ''


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
