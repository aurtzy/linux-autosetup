from abc import ABC
from dataclasses import dataclass, field
from os import PathLike


@dataclass
class BaseSettings(ABC):
    """Base settings class. Meant to be used for recognizing whether a class is a settings-related class."""
    pass


@dataclass
class GlobalSettings(BaseSettings):
    """
    Global settings.

    options:
        See Options docs.
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
    class Options(BaseSettings):
        """
        Options for the script.

        noconfirm:
            Indicates whether user should be prompted for input during the script.
        """
        noconfirm: bool = False

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
        validate_path:
            Used to confirm if a path exists to some file/directory.
        validate_dir:
            Used to confirm if a path exists to some directory.
        """
        superuser: str = 'sudo'
        cp: str = 'cp -at "$1" "${@:2}"'
        mv: str = 'mv -t "$1" "${@:2}"'
        mkdir: str = 'mkdir -p "$1"'
        validate_path: str = '[ -e "$1" ]'
        validate_dir: str = '[ -d "$1" ]'

    @dataclass
    class CustomModule(BaseSettings):
        """
        Designated settings for the custom module.

        cmd_presets:
            Dictionary of name -> CmdPreset pairs.
        """

        @dataclass
        class CmdPreset(BaseSettings):
            """
            A preset of shell commands.

            install_cmd:
                Meant to be run during pack installs.
            backup_cmd:
                Meant to be run during pack backups.
            """
            install_cmd: str = ''
            backup_cmd: str = ''

        cmd_presets: dict[str, 'GlobalSettings.CustomModule.CmdPreset'] = field(default_factory=dict)

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
        backup_dirs: dict[str, PathLike] = field(default_factory=dict)
        dump_dirs: dict[str, PathLike] = field(default_factory=dict)
        tmp_dirs: dict[str, PathLike] = field(default_factory=dict)

    options: Options = field(default_factory=lambda: GlobalSettings.Options())
    system_cmds: SystemCmds = field(default_factory=lambda: GlobalSettings.SystemCmds())
    custom_module: CustomModule = field(default_factory=lambda: GlobalSettings.CustomModule())
    apps_module: AppsModule = field(default_factory=lambda: GlobalSettings.AppsModule())
    files_module: FilesModule = field(default_factory=lambda: GlobalSettings.FilesModule())

    def __str__(self):
        return str(self.__dict__)


global_settings = GlobalSettings()
