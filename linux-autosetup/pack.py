import logging
import os.path
import re
from abc import abstractmethod, ABC
from dataclasses import dataclass
from aenum import Enum, extend_enum

from lib.configurable import configurable
from lib.prompter import get_input
from lib.system import run, PathOps
from lib.logger import log


class BaseModule(ABC):
    """
    Abstract method for creating new modules.

    The labels "module" and "alt" are reserved for use with configs, and are not recommended
    as property names.
    """

    @staticmethod
    def convert_to_str_list(arg) -> list[str]:
        """
        Converts the given arg into a str list.

        If arg is a list, pass each element through str() and return that;
        otherwise, perform the following on str(arg):
            If arg contains no newline characters, delimit into a list by spaces.
            Otherwise, delimit by newline characters.
        """
        log(f'Got {str(arg)} as arg to convert.', logging.DEBUG)
        if arg is None:
            log('Arg is NoneType - setting to empty list.', logging.DEBUG)
            arg = []
        elif isinstance(arg, list):
            log('Arg is a list - converting any elements to str if not already str.', logging.DEBUG)
            arg = [str(element) for element in arg]
        else:
            arg = str(arg)
            if '\n' in arg:
                arg = arg.split('\n')
            else:
                arg = arg.split(' ')
        log(f'Returning {arg}', logging.DEBUG)
        return arg

    @abstractmethod
    def __init__(self, settings: dict):
        pass

    @abstractmethod
    def install(self, no_confirm: bool = False):
        pass

    @abstractmethod
    def backup(self, no_confirm: bool = False):
        pass


class DependenciesModule(BaseModule):
    """Handles installation of pack dependencies."""

    def __init__(self, settings: dict):
        log('Initializing dependencies module...', logging.DEBUG)
        log(str(settings), logging.DEBUG)

        # dependencies
        self.dependencies = self.convert_to_str_list(settings.get('dependencies'))
        if not self.dependencies:
            log('This DependenciesModule has no dependencies. Is this intentional?', logging.WARNING)

    def install(self, no_confirm: bool = False):
        pass

    def backup(self, no_confirm: bool = False):
        pass


class CustomCmdsModule(BaseModule):
    """Handles running custom commands."""

    def __init__(self, settings: dict):
        # cmd
        self.cmd: str = settings.get('cmd')

        # args
        self.args: list[str]

    def install(self, no_confirm: bool = False):
        pass

    def backup(self, no_confirm: bool = False):
        pass


class AppCmdsModule(CustomCmdsModule):
    """Handles installation of apps."""

    install_cmds: dict[str, str] = {}

    def __init__(self, settings: dict):
        log('Initializing apps module...', logging.INFO)
        log(str(settings), logging.DEBUG)

        # apps
        self.apps = self.convert_to_str_list(settings.get('apps'))
        if not self.apps:
            log('Initializing with no apps. Is this intentional?', logging.WARNING)

        # install_cmd
        self.install_cmd = settings.get('install_cmd')
        if self.install_cmd not in configurable['INSTALL_CMDS'].keys():
            log(f'Could not match {self.install_cmd} with anything in INSTALL_CMDS - Please fix.', logging.ERROR)
            exit(1)

    def install(self, no_confirm: bool = False):
        # todo: log('install app . . .)
        super(no_confirm)

    def backup(self, no_confirm: bool = False):
        pass


class FileCmdsModule(CustomCmdsModule):
    """Handles installation and backing up of files."""

    def __init__(self, settings: dict):
        log('Initializing files module...', logging.INFO)
        log(str(settings), logging.DEBUG)

        # files_location
        self.files_location = settings.get('files_location')
        if not isinstance(self.files_location, str):
            log('Expected files_location to be a string, but it was not. Is this intentional?', logging.WARNING)
        log('Expanding any variables in files_location', logging.DEBUG)
        self.files_location = os.path.expandvars(str(self.files_location))
        log(self.files_location, logging.DEBUG)

        # files
        self.files = self.convert_to_str_list(settings.get('files'))
        if not self.files:
            log('Initializing with an empty list of files. Is this intentional?', logging.WARNING)

        #

    def install(self, no_confirm: bool = False):
        pass

    def backup(self, no_confirm: bool = False):
        pass


class Module(Enum):
    dependencies = DependenciesModule
    custom = CustomCmdsModule
    apps = AppCmdsModule
    files = FileCmdsModule


@dataclass
class AppSettings:
    """
    App-specific settings.

    apps: list[str]
        List of app names used in installation.
    install_type: InstallType
        Indicates the type of install command to use.

    Implements __iter__, which iterates through the apps list.
    """

    class InstallType(Enum):
        """
        Types of install commands that can be used.

        This enum class can be added to.
        """

        def __str__(self):
            return self.name

        @classmethod
        def add(cls, install_types: dict[str, str]):
            """
            Adds the entries of the given dictionary of install types to this enum class.

            Expects str -> str pairs.
            """
            for k, v in install_types.items():
                if not isinstance(v, str):
                    log(f'Potential error assigning {v} as the AppInstallType {k}.',
                        logging.WARNING)
                extend_enum(cls, k, v)

    apps: list[str]
    install_type: InstallType

    def __iter__(self):
        for app in self.apps:
            yield app


@dataclass
class FileSettings:
    """
    File-specific settings.
    # TODO: what if we combined files_dir and files, and made it "backup_args"? better name?
       install_args for both AppSettings and FileSettings; backup_args for FileSettings too
    files_dir: str
        Optional path that denotes the working directory of the BackupType command, notably used with tar's -C switch.
        Useful for potentially variable directory names like user home folders - substituting variables through
        the files list makes it only work for that variable after it is substituted, which may result in unintended
        behavior.
    files: list[str]
        List of file paths that are or will be backed up.

    install_args
    archive_cmds: ArchiveCmds
        Indicates the type of commands used to create and extract archived files.
    backup_dirs: list[BackupDir]
        Denotes directories where archives are stored.
        Must have a length of at least one.
    backup_keep: int
        Number of old backups to keep before dumping.
        If set to -1, script will keep all backups made and not dump old ones.
        If set to 0, only the most recent made one in a backup path is kept.

    Implements __iter__, which iterates through the files list.
    """

    class ArchiveCmds(Enum):
        """
        Types of file archive commands that can be used.

        This enum class can be added to.
        """

        def __str__(self):
            return self.name

        @classmethod
        def add(cls, archive_cmds: dict[str, dict[str, str]]):
            """
            Adds the entries of the given dictionary of backup types to this enum class.

            Expects str -> dict[str, str] dict pairs, with the dict having both a 'CREATE' and 'EXTRACT' key.
            """
            for k, v in archive_cmds.items():
                extract = v.get('EXTRACT')
                create = v.get('CREATE')
                if not isinstance(extract, str):
                    log(f'Potential error assigning {extract} as the {k} EXTRACT command(s).', logging.WARNING)
                if not isinstance(create, str):
                    log(f'Potential error assigning {create} as the {k} CREATE command(s).', logging.WARNING)
                extend_enum(cls, k, dict(EXTRACT=extract, CREATE=create))

    class BackupDir(Enum):
        """
        Backup directories that can be used.

        This enum class can be added to.
        """

        def __str__(self):
            return f'{self.name} - {self.value}'

        @classmethod
        def add(cls, backup_dirs: dict[str, str], no_confirm: bool = False):
            """
            Adds the entries of the given dictionary of backup directories to this enum class.

            Will perform checks on each path to confirm if they are valid, prompting the user to either create
            the backup directory or skip adding it if it doesn't exist.

            If the no_confirm param is True, no prompts will be made, and the script will automatically create
            backup paths if they are missing and add them to the enum class.
            """
            for k, dir_path in backup_dirs.items():
                if PathOps.dir_valid(dir_path):
                    log(f'Adding FileBackupPath {k}: "{dir_path}"', logging.DEBUG)
                    extend_enum(cls, k, dir_path)

    files_location: str
    files: list[str]
    archive_cmds: ArchiveCmds
    backup_dirs: list[BackupDir]
    backup_keep: int
    tmp_dir: str = ''

    def __iter__(self):
        for file in self.files:
            yield file


class Pack:
    """Glues modules together which can be collectively installed/backed up."""

    packs: list["Pack"] = []

    def __init__(self, name: str, modules: list[Module], desc: str = ''):
        log(f'Initializing pack "{name}"...', logging.INFO)

        # name
        self.name = name
        if self.name == '':
            log('Pack names cannot be empty. Please check config.', logging.ERROR)
            exit(1)
        elif self.name in self.packs:
            log(f'Pack name {self.name} already exists, which is causing an overlap.', logging.ERROR)
            exit(1)

        # modules
        self.modules = modules
        if not self.modules:
            log(f'Modules list for {self.name} is empty. Is this intentional?', logging.WARNING)

        # desc
        self.desc = desc

        self.attempted_install = False
        self.attempted_backup = False
        self.packs.append(self)
        log(f'Initialized {self.name} with the following settings:\n{str(self)}', logging.DEBUG)

    @staticmethod
    def get_sorted_backups(backup_dir: str) -> list[str]:
        """
        Returns a list of paths to existing backups in the specified backup_dir for this pack,
        sorted from oldest to newest.
        """
        log(f'Attempting to find any directories that exist in {backup_dir}...', logging.DEBUG)
        # TODO: case where dir doesn't exist, causing StopIteration error

        return sorted(
            filter(lambda path: re.match('^\\d$', path, flags=re.ASCII) is not None,
                   next(os.walk(backup_dir))[1]))

    def install(self):
        """Performs an installation of the pack."""
        if self.attempted_install:
            return

        log(f'Successfully installed {self.name}!', logging.INFO)

    def backup(self):
        """Performs a backup of the pack."""
        # TODO
        return True

    def __str__(self, verbose=True):
        # TODO
        pass
