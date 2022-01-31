import logging
from dataclasses import dataclass, fields, field, MISSING
from enum import Enum

from lib.logger import log


@dataclass
class BaseModule:
    """
    Base module, which provides a set of optionally overridable methods that are used in packs.

    In order to reserve keywords that specify navigational settings (e.g. what module to use),
    implementations should avoid using all-uppercase property names.
    """

    def __post_init__(self):
        # Assign fields to their default if field is None and a default(_factory) exists
        for field in fields(self):
            if getattr(self, field.name) is None:
                log(f'? {field}', logging.DEBUG)
                if field.default is not MISSING:
                    setattr(self, field.name, field.default)
                elif field.default_factory is not MISSING:
                    setattr(self, field.name, field.default_factory())
                else:
                    log(f'There was a problem assigning a default to {field.name}.\n'
                        f'This may produce unexpected results.', logging.WARNING)

    # TODO: move to configparser
    # @staticmethod
    # def convert_to_str_list(arg) -> list[str]:
    #     """
    #     Converts the given arg into a str list.
    #
    #     If arg is a list, pass each element through str() and return that;
    #     otherwise, perform the following on str(arg):
    #         If arg contains no newline characters, delimit into a list by spaces.
    #         Otherwise, delimit by newline characters.
    #     """
    #     log(f'Got {str(arg)} as arg to convert.', logging.DEBUG)
    #     if arg is None:
    #         log('Arg is NoneType - setting to empty list.', logging.DEBUG)
    #         arg = []
    #     elif isinstance(arg, list):
    #         log('Arg is a list - converting any elements to str if not already str.', logging.DEBUG)
    #         arg = [str(element) for element in arg]
    #     else:
    #         arg = str(arg)
    #         if '\n' in arg:
    #             arg = arg.split('\n')
    #         else:
    #             arg = arg.split(' ')
    #     log(f'Returning {arg}', logging.DEBUG)
    #     return arg

    def install(self):
        """
        Install method, called when performing a pack install.
        """
        log('Nothing to do here in install()...', logging.DEBUG)

    def backup(self):
        """
        Backup method, called when performing a pack backup.
        """
        log('Nothing to do here in backup()...', logging.DEBUG)


@dataclass
class PacksModule(BaseModule):
    """
    Calls install and backup methods from other packs as specified.

    packs:
        List of packs to call.
    """

    packs: list['Pack'] = field(default_factory=list)

    def __post_init__(self):
        super()
        if not self.packs:
            log(f'This {self.__class__.__name__} has no packs. Is this intentional?', logging.WARNING)

    def install(self):
        for pack in self.packs:
            pack.install()

    def backup(self):
        for pack in self.packs:
            pack.backup()


@dataclass
class CustomModule(BaseModule):
    """
    Handles running custom commands.

    install_cmd:

    install_args:

    backup_cmd:

    backup_args:

    """

    install_cmd: str = ''
    install_args: list[str] = field(default_factory=list)
    backup_cmd: str = ''
    backup_args: list[str] = field(default_factory=list)

    def install(self):
        pass

    def backup(self):
        pass


@dataclass
class AppsModule(CustomModule):
    """
    Handles installation of apps.

    apps:
        List of apps to
    install_cmd, install_args, backup_cmd, backup_args:
        See CustomModule.
    """

    apps: list[str] = field(default_factory=list)

    def install(self):
        pass

    def backup(self):
        pass


class FilesModule(CustomModule):
    """
    Handles installation and backing up of files.

    fil

    # TODO: below is temp old docs
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
    """

    # def __init__(self, settings: dict):
    #     # TODO: remove; transfer some of this stuff to configparser if it's useful?
    #     log('Initializing files module...', logging.INFO)
    #     log(str(settings), logging.DEBUG)
    #
    #     # files_location
    #     self.files_location = settings.get('files_location')
    #     if not isinstance(self.files_location, str):
    #         log('Expected files_location to be a string, but it was not. Is this intentional?', logging.WARNING)
    #     log('Expanding any variables in files_location', logging.DEBUG)
    #     self.files_location = os.path.expandvars(str(self.files_location))
    #     log(self.files_location, logging.DEBUG)
    #
    #     # files
    #     self.files = self.convert_to_str_list(settings.get('files'))
    #     if not self.files:
    #         log('Initializing with an empty list of files. Is this intentional?', logging.WARNING)

    def install(self):
        pass

    def backup(self):
        pass

    # @staticmethod
    # def get_sorted_backups(backup_dir: str) -> list[str]:
    #     """
    #     Returns a list of paths to existing backups in the specified backup_dir for this pack,
    #     sorted from oldest to newest.
    #     """
    #     log(f'Attempting to find any directories that exist in {backup_dir}...', logging.DEBUG)
    #     # TODO: case where dir doesn't exist, causing StopIteration error
    #
    #     return sorted(
    #         filter(lambda path: re.match('^\\d$', path, flags=re.ASCII) is not None,
    #                next(os.walk(backup_dir))[1]))


class Module(Enum):
    packs = PacksModule
    custom = CustomModule
    apps = AppsModule
    files = FilesModule


class Pack:
    """Glues modules together which can be collectively installed/backed up."""

    packs: list['Pack'] = []
    pinned_packs: list['Pack'] = []

    def __init__(self, name: str, desc: str, modules: list[BaseModule], pin: int):
        # name
        self.name = name
        if self.name == '':
            log('Cannot assign empty names to packs. Please check config.', logging.ERROR)
            raise ValueError
        else:
            for pack in self.packs:
                if self.name == pack.name:
                    log(f'Pack {self.name} already exists, causing a name overlap.', logging.ERROR)
                    raise ValueError

        self.pin = pin
        if self.pin:
            for i, pack in enumerate(self.pinned_packs):
                if self.pin < pack.pin:
                    self.pinned_packs.insert(i, self)

        # modules
        self.modules = modules
        if not self.modules:
            log(f'Modules list for {self.name} is empty. Is this intentional?', logging.WARNING)

        # desc
        self.desc = desc

        self.attempted_install = False
        self.attempted_backup = False
        self.packs.append(self)
        log(f'Initialized pack {self.name}.', logging.INFO)
        log(f'{self}', logging.DEBUG)

    def install(self):
        """Performs an installation of the pack."""
        if self.attempted_install:
            log(f'Install was run already for {self.name}. Skipping...', logging.INFO)
            return

        log(f'Installing {self.name}...', logging.INFO)
        for module in self.modules:
            log(f'Running {module.__class__.__name__}...', logging.INFO)
            module.install()

        log(f'Installed {self.name}!', logging.INFO)

    def backup(self):
        """Performs a backup of the pack."""
        if self.attempted_backup:
            log(f'Backup was run already for {self.name}. Skipping...', logging.INFO)
            return

        log(f'Backing up {self.name}...', logging.INFO)
        for module in self.modules:
            module.backup()

        log(f'Backed up {self.name}!', logging.INFO)

    def __str__(self, verbose=True):
        string = f'Pack Name: {self.name}\n' \
                 f'{self.desc}'
        if verbose and self.modules:
            string += f'\n' \
                      f'Modules:'
            for module in self.modules:
                string += f'\n\n' \
                          f'{module}'
        return string
