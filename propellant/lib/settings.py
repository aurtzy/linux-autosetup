import abc
import logging
from dataclasses import dataclass, field, MISSING, fields
from os import PathLike

from .logger import log


config: dict[str, dict]


class Settings(abc.ABC):
    """
    Implementing this Settings class:
        - Settings must be a direct superclass in order for the initializing hooks to work. Inheritance
          of other Settings subclasses is not a problem as long as Settings is also directly inherited from.

        - The "category" argument keyword must be given a value,
          which will indicate the category of settings it will belong to.

        - Subclasses of Settings can be of the same category, however an error will occur if the elements
          within these categories overlap.

        - The initialize method must be implemented, which should parse the given dictionary
          of values, performing any necessary extra checks and actions,
          and return the desired format of setting-value pairs in a dictionary.
    """

    __settings_category__: str

    def __init_subclass__(cls, category, **kwargs):
        """
        Assigns a config category to the subclass of settings.
        """
        super().__init_subclass__(**kwargs)
        cls.__settings_category__ = category

    @classmethod
    def initialize(cls, config_dict):
        """
        Initializes settings for all subclasses of Settings
        and adds each configuration to the corresponding category in config.

        Categories may overlap and will simply combine, however elements within categories are not permitted.

        :raises AssertionError: if there is an overlap with elements in the categories.
        """
        for subclass in cls.__subclasses__():
            subclass_settings = subclass.initialize_settings(config_dict.get(subclass.__settings_category__, {}))
            if config.get(subclass.category) is not None:
                assert (key not in config[subclass.__settings_category__].keys() for key in subclass_settings.keys())
                config[subclass.__settings_category__].update(subclass_settings)
            else:
                config[subclass.__settings_category__] = subclass_settings

    @classmethod
    @abc.abstractmethod
    def initialize_settings(cls, category_dict) -> dict:
        """
        Parses the given category dict and performs any necessary initialization actions.
        :return: A formatted dictionary to be added to config.
        """
        pass


# TODO: EVERYTHING BELOW DEPRECATED. Begin refactoring and following todos.

@dataclass
class BaseSettings(ABC):
    """Base settings class."""
    def __post_init__(self):
        """Assign fields to their default if fld is None and a default(_factory) exists."""
        for fld in fields(self):
            if getattr(self, fld.name) is None:
                if fld.default is not MISSING:
                    setattr(self, fld.name, fld.default)
                elif fld.default_factory is not MISSING:
                    setattr(self, fld.name, fld.default_factory())
                else:
                    log(f'There was a problem assigning a default to {fld.name}.\n'
                        f'This may produce unexpected results.', logging.WARNING)


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
