import logging
import typing

from . import system
from .settings import Settings
from .logger import log


class PackModule(Settings, keys=('pack_modules',)):
    """
    Base class for creating pack modules.

    Provides:
        - an automatic hook that sets the pack module name
        based off the last string in the keys parameter.
        - various implementable methods that will be called
        when appropriate during an autosetup.
    """

    pack_modules: dict = {}

    def __init_subclass__(cls, keys: tuple[str] = (), **kwargs):
        super().__init_subclass__(keys, **kwargs)
        cls.pack_modules.update({keys[-1]: cls})

    @classmethod
    def initialize_settings(cls, **key_config):
        pass

    def __init__(self, **module_settings):
        pass

    def pre_install(self):
        """This method is called immediately before the script begins installing packs."""
        pass

    def pre_backup(self):
        """This method is called immediately before the script begins backing up packs."""
        pass

    def install(self):
        """This method is called when installing packs."""
        pass

    def backup(self):
        """This method is called when backing up backs."""
        pass


class BasicPackModule(PackModule, keys=('basic',)):
    """

    Settings:
        cmd_presets: dict
            Presets of shell commands.

            pipe: str | bool
                Indicates whether data should be piped into the shell.
                If pipe is a str, then this string will always be piped into the commands.
                If True, then the user will be prompted for what will be piped. Otherwise, pipe is ignored.
            install_cmd: str
                Commands to run during pack installs.
            backup_cmd: str
                Commands to run during pack backups.
    
    """

    cmd_presets: dict = {}

    @classmethod
    def initialize_settings(cls, **key_config):

        # cmd_presets
        cmd_presets: dict = cls.assert_tp(key_config, 'cmd_presets', dict, default={})
        for cmd_preset in cmd_presets.keys():
            settings: dict = cls.assert_tp(cmd_presets, cmd_preset, dict)
            cls.cmd_presets[cmd_preset] = {
                'pipe': cls.assert_tp(settings, 'pipe', typing.Union[str, bool], default='pipe'),
                'install_cmd': cls.assert_tp(settings, 'install_cmd', str, default=''),
                'backup_cmd': cls.assert_tp(settings, 'backup_cmd', str, default='')
            }

    def __init__(self, **module_settings):
        super().__init__(**module_settings)
        # cmd_preset

        # pipe

        # install_cmd

        # backup_cmd

        # install_args

        # backup_args

        # todo
        # cmd_preset: str = None
        # pipe: str | bool = False
        # install_cmd: str = ''
        # backup_cmd: str = ''
        # install_args: list[str] = field(default_factory=list)
        # backup_args: list[str] = field(default_factory=list)


class FilesPackModule(BasicPackModule, keys=('files',)):
    """

    Settings:
        cmd_presets: dict
            See BasicPackModule.
        backup_dirs: dict
            todo
        dump_dirs: dict
            todo
        tmp_dirs: dict
            todo
    """

    backup_dirs: dict = {}
    dump_dirs: dict = {}
    tmp_dirs: dict = {}

    @classmethod
    def initialize_settings(cls, **key_config):
        super().initialize_settings(**key_config)

        def assert_dirs(dirs) -> dict:
            dirs: dict = cls.assert_tp(key_config, dirs, dict, default={})
            result = {}
            for dir_name, dir_path in dirs.items():
                result[dir_name] = system.Path.valid_dir(str(dir_path))
            return result

        # backup_dirs
        cls.backup_dirs.update(assert_dirs('backup_dirs'))

        # dump_dirs
        cls.dump_dirs.update(assert_dirs('dump_dirs'))

        # tmp_dirs
        cls.tmp_dirs.update(assert_dirs('tmp_dirs'))

    def __init__(self, **module_settings):
        super().__init__(**module_settings)
        # todo
        pass


#@dataclass
class PacksModule:
    """ TODO: OLD
    Calls install and backup methods from other packs as specified.

    packs:
        List of packs to call.
    """

#    packs: list[str] = field(default_factory=list)

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


#@dataclass
class FilesModule:
    """ TODO: OLD
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


class Pack(Settings, keys=('packs',)):
    """
    Glues modules together which can be collectively installed/backed up.

    Settings:
        packs: list[Pack]
            A list of all initialized Pack objects.
    """

    packs: list['Pack'] = []

    @classmethod
    def initialize_settings(cls, **key_config):
        # Initialize packs
        for pack_name, pack_settings in cls.assert_tp(key_config, 'packs', dict, default={}):
            Pack(pack_name, **pack_settings)

    @classmethod
    def pack_exists(cls, pack_name: str):
        """Checks if the given pack name exists matches any packs in cls.packs"""
        for p in cls.packs:
            if p.name == pack_name:
                return True
        else:
            log(f'Could not find any packs with the name {pack_name}.', logging.ERROR)
            return False

    def __init__(self, name: str, **pack_settings):
        log(f'Initializing pack {name}...', logging.DEBUG)
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

        # desc
        self.desc: str = pack_settings.get('desc', '')

        # modules
        self.modules: list[PackModule] = []
        for module_settings in self.assert_tp(pack_settings.get('modules', []), list):
            module_settings: dict = self.assert_tp(module_settings, dict)
            module_tp = self.assert_tp(PackModule.pack_modules.get(module_settings.get('module')), PackModule)
            self.modules.append(module_tp(**module_settings))
        if not self.modules:
            log(f'Modules list for {self.name} is empty. Is this intentional?', logging.WARNING)

        # install_success - indicates success of install; None means install has not been run.
        self.install_success: typing.Union[bool, None] = None

        # backup_success - indicates success of backup; None means backup has not been run.
        self.backup_success: typing.Union[bool, None] = None

        self.packs.append(self)
        log(f'{self}', logging.DEBUG)

    # TODO: implement install/backup success detection - success = False at start of method; success = True only at end
    #  ALSO: add pre_install and pre_backup method calls
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
