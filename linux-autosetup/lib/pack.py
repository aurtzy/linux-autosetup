import logging
from dataclasses import dataclass, field
from enum import Enum

from lib.settings import BaseSettings
from lib.logger import log


@dataclass
class BaseModule(BaseSettings):
    """
    Base module, which provides a set of optionally overridable methods that are used in packs.

    The property name "module" should be reserved for config parsers, so they can properly discern
    which modules should be initialized.
    """

    def __post_packs_init__(self, owner: 'Pack'):
        """Method that is called after all packs have been initialized."""
        pass

    def install(self):
        """Install method, called when performing a pack install."""
        pass

    def backup(self):
        """Backup method, called when performing a pack backup."""
        pass


@dataclass
class PacksModule(BaseModule):
    """
    Calls install and backup methods from other packs as specified.

    packs:
        List of packs to call.
    """

    packs: list[str] = field(default_factory=list)

    def __post_init__(self):
        super()
        if not self.packs:
            log(f'{self.__class__.__name__} has no packs. Is this intentional?', logging.WARNING)

    def __post_packs_init__(self, owner: 'Pack'):
        log(f'Error-checking packs in PacksModule from {owner.name}...', logging.DEBUG)
        for pack_name in self.packs:
            # Check if pack name can be found/exists in Pack.packs
            for pack in Pack.packs:
                if pack.name == pack_name:
                    # Check if any pack modules from these packs reference the owner pack
                    # which may cause an infinite loop
                    for module in pack.modules:
                        if isinstance(module, PacksModule):
                            for other_pack_name in module.packs:
                                if other_pack_name == owner.name:
                                    log(f'Encountered a potential infinite loop that may occur '
                                        f'with {owner.name} and {pack.name}.', logging.CRITICAL)
                                    raise RecursionError
                    break
            else:
                log(f'Could not match the pack name {pack_name} with any existing packs.', logging.ERROR)
                raise LookupError

    def install(self):
        for pack_name in self.packs:
            for pack in Pack.packs:
                if pack.name == pack_name:
                    pack.install()

    def backup(self):
        for pack_name in self.packs:
            for pack in Pack.packs:
                if pack.name == pack_name:
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


@dataclass
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

    def __init__(self, name: str, desc: str, modules: list[BaseModule], pin: int = 0):
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

        # pin
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
        self.desc: str = desc

        # install_success - indicates success of install; None means install has not been run.
        self.install_success: bool | None = None

        # backup_success - indicates success of backup; None means backup has not been run.
        self.backup_success: bool | None = None

        self.packs.append(self)
        log(f'Initialized pack {self.name}.', logging.INFO)
        log(f'{self}', logging.DEBUG)

    def __post_packs_init__(self):
        """Method called after all packs are initialized, which does miscellaneous things."""
        log(f'Running post initializations method for {self.name}...', logging.DEBUG)
        for module in self.modules:
            module.__post_packs_init__(self)

    # TODO: implement install/backup success detection - success = False at start of method; success = True only at end
    def install(self):
        """Performs an installation of the pack."""
        if self.install_success is not None:
            log(f'Install was run already for {self.name}. Skipping...', logging.INFO)
            return

        log(f'Installing {self.name}...', logging.INFO)
        for module in self.modules:
            module.install()

    def backup(self):
        """Performs a backup of the pack."""
        if self.backup_success is not None:
            log(f'Backup was run already for {self.name}. Skipping...', logging.INFO)
            return

        log(f'Backing up {self.name}...', logging.INFO)
        for module in self.modules:
            module.backup()

    def __str__(self, verbose=True):
        string = f'Pack Name: {self.name}\n' \
                 f'Desc: {self.desc}'
        if verbose and self.modules:
            string += f'\n' \
                      f'Modules:'
            for module in self.modules:
                string += f'\n\t' \
                          f'{module}'
        return string
