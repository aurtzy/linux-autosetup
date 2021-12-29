import logging
import re
import typing
from typing import TypedDict
from aenum import Enum, extend_enum, auto

from lib.runner import Runner
from lib.logger import log


class Predefined:
    """
    Predefined modifiable values.

    To make it less confusing, when making use of files in shell arguments, follow this convention:
        $1 denotes the destination.
        ${2:@} denotes the source(s).

    alias_prefix: str
        Used as a prefix to alias names in strings. Indicates substitution with aliases.
    move_cmd: str
        Shell command used for moving files.
    copy_cmd: str
        Shell command used for copying files.
    AppInstallTypes: Enum
        Types of install commands that can be used.
    FilesBackupTypes: Enum
        Types of file install/backup commands that can be used.
    """
    alias_prefix: str

    move_cmd: str
    move_alt_cmd: str
    copy_cmd: str
    copy_alt_cmd: str

    class AppInstallTypes(Enum):
        def __str__(self):
            return self.name

    @classmethod
    def set_app_install_types(cls, new_install_types: dict[str, str]):
        """:param new_install_types: New dictionary to replace enum name-value pairs."""
        for k, v in new_install_types.items():
            extend_enum(cls.AppInstallTypes, k, v)

    class FileBackupTypes(Enum):
        def __str__(self):
            return self.name

    @classmethod
    def set_file_backup_types(cls, new_backup_types: dict[str, dict[str, str]]):
        """:param new_backup_types: New dictionary to replace enum name-value pairs."""
        for k, v in new_backup_types.items():
            extend_enum(cls.FileBackupTypes, k, v)


# TODO: REMOVE AND MOVE TO configparser.py when making - TEMPORARY PLACEMENT
Predefined.alias_prefix = '//'
Predefined.move_cmd = 'mv -t $1 ${@:2}'
Predefined.move_alt_cmd = 'sudo mv -t $1 ${@:2}'
Predefined.copy_cmd = 'cp -at $1 ${@:2}'
Predefined.copy_alt_cmd = 'sudo cp -at $1 ${@:2}'
Predefined.set_app_install_types({
    'FLATPAK': 'flatpak install -y --noninteractive $@'
})
Predefined.set_file_backup_types({
    'COPY': {
        # TODO
    },
    'HARDLINK': {
        # TODO
    },
    'TAR_COPY': {
        'EXTRACT': 'tar -xPf "$1.tar"',
        'CREATE': 'tar -cPf "$1.tar" "${@:2}"'
    },
    'COMPRESS': {
        'EXTRACT': 'tar -xPf "$1.tar.xz"',
        'CREATE': 'tar -cJPf "$1.tar.xz" "${@:2}"'
    },
    'ENCRYPT': {
        'EXTRACT': 'openssl enc -d -aes-256-cbc -md sha512 -pbkdf2 -salt -in "$1.tar.xz.enc" | '
                   'tar -xPf -',
        'CREATE': 'tar - cJPf - "${@:2}" | '
                  'openssl enc -e -aes-256-cbc -md sha512 -pbkdf2 -salt -out "$1.tar.xz.enc"'
    }
})


class AppSettings(TypedDict):
    """
    App-specific settings.

    install_type: Predefined.AppInstallTypes
        Indicates the type of install command to use.
    """
    install_type: Predefined.AppInstallTypes


class FileSettings(TypedDict):
    """
    File-specific settings.

    backup_type: Predefined.FileBackupTypes
        Indicates the type of backup performed on files.
    backup_paths: list[str]
        Denotes paths where backups are stored.
        Must have a length of at least one.
    backup_keep: int
        Number of old backups to keep before dumping.
        Must be at least zero.
    dump_dir: str
        Designated directory to dump any files to.
        Must not be an empty string.
    tmp_dir: str
        Designated directory to keep temporary files in.
        Must not be an empty string.
    """
    backup_type: Predefined.FileBackupTypes
    backup_paths: list[str]
    backup_keep: int
    dump_dir: str
    tmp_dir: str


class ErrorHandling(Enum):
    """
    Indicates how script should handle errors.

    PROMPT is the only option that facilitates user input.

    RETRY_PART and RETRY_FULL are meant for internal use with PROMPT as a default.
    They can technically be used, but unless the user is dealing
    with an extreme edge case that needs auto-retry functionalities, this is not recommended
    as it will most likely put the script in a loop.
    """
    PROMPT: int = auto()
    RETRY_PART: int = auto()
    RETRY_FULL: int = auto()
    SKIP_PART: int = auto()
    SKIP_FULL: int = auto()
    ABORT: int = auto()

    def __str__(self):
        return self.name


class Settings(TypedDict):
    """
    Main Pack class settings.

    depends: list[str]
        List of pack object names that a pack depends on, which should be installed first.
        Relevant when calling install().
        Implementations may want to check whether all depends names are valid.
    apps: list[str]
        Apps to be assigned to the pack.
    app_settings: AppSettings | NoneType
        Custom app-related settings. Set to None when apps is an empty list.
    files: list[str]
        Files to be assigned to the pack.
    file_settings: FileSettings | NoneType
        Custom file-related settings. Set to None when files is an empty list.
    install_cmd: str
        Custom string of command(s) that will be run when calling install method.
    backup_cmd: str
        Custom string of command(s) that will be run when calling backup method.
    error_handling: ErrorHandling
        Indicates how script will handle errors.
    """
    depends: list[str]
    apps: list[str]
    files: list[str]
    app_settings: typing.Union[AppSettings, None]
    file_settings: typing.Union[FileSettings, None]
    install_cmd: str
    backup_cmd: str
    error_handling: ErrorHandling


# TODO: put this in configparser.py instead of pack.py
fallback_settings: Settings = Settings(depends=[],
                                       apps=[],
                                       files=[],
                                       app_settings=AppSettings(
                                           install_type=None),
                                       file_settings=FileSettings(
                                           backup_type=None,
                                           backup_paths=['./backups'],
                                           backup_keep=1,
                                           dump_dir='/tmp/linux-autosetup-dump',
                                           tmp_dir='/tmp/linux-autosetup'),
                                       install_cmd='',
                                       backup_cmd='',
                                       error_handling=ErrorHandling['PROMPT']
                                       )


class Pack:
    """Contains various settings and functions for installing and backing up stuff."""

    def __init__(self, name: str, settings: Settings):
        """
        This constructor will perform checks on values according to their respective docs,
        if any such prerequisites exist.

        :param name: Name of the pack.
        :param settings: Pack settings. If None, fallback_settings will be used.
        """
        log(f'Initializing Pack object for {name}.', logging.INFO)
        self.name = name
        if settings['apps']:
            app_settings: AppSettings = settings['app_settings']
            try:
                assert app_settings
            except AssertionError:
                log(f'Unable to initialize {self.name}. Setting app_settings to None '
                    f'when apps is non-empty is not allowed.', logging.ERROR)
                raise
        else:
            settings['app_settings'] = None
        if settings['files']:
            file_settings: FileSettings = settings['file_settings']
            try:
                assert file_settings
            except AssertionError:
                log(f'Unable to initialize {self.name}. Setting file_settings to None '
                    f'when files is non-empty is not allowed.', logging.ERROR)
                exit('Aborting.')
            try:
                assert len(file_settings['backup_paths']) != 0
            except AssertionError:
                log(f'Unable to initialize {self.name}. Setting an empty backup_paths list when '
                    f'files is non-empty is not allowed.', logging.ERROR)
                exit('Aborting.')
            try:
                assert file_settings['backup_keep'] >= 0
            except AssertionError:
                log(f'Unable to initialized {self.name}. Setting a negative backup_keep count '
                    f'is not allowed.', logging.ERROR)
                exit('Aborting.')
            try:
                assert file_settings['dump_dir']
            except AssertionError:
                log('Packs must be initialized with a dump directory '
                    'that is not an empty string.', logging.ERROR)
                exit('Aborting.')
            try:
                assert file_settings['tmp_dir']
            except AssertionError:
                log('Packs must be initialized with a temporary directory '
                    'that is not an empty string.', logging.ERROR)
                exit('Aborting.')
        else:
            settings['file_settings'] = None
        self.settings = settings
        self.attempted_install = False
        self.attempted_backup = False
        packs.append(self)
        log(f'Initialized pack {self.name} with the following settings:\n{str(self)}', logging.DEBUG)

    def handle_error(self, function) -> int:
        """
        Handles errors that occur when installing or backing up packs.

        :param function: Function where the error occurred.
        :return: ErrorHandling enum that is not PROMPT, so the caller can take further action.
        """
        fun_name = function.__name__
        log(f'Encountered error doing {fun_name} for {self.name}.\n'
            f'Attempting to handle...', logging.DEBUG)
        error_handling = self.settings['error_handling']
        if error_handling == ErrorHandling.PROMPT:
            user_in = None
            while True:
                # TODO: fix changed error_handling names
                log('Prompting user to handle error.', logging.DEBUG)
                user_in = input(f'An error occurred doing {self.name} {fun_name}. Do you want to:\n'
                                f'1 [RP]: Try running the command again?\n'
                                f'2 [RF]: Restart {fun_name} and try again?\n'
                                f'3 [SP]: Skip just this failed command?\n'
                                f'4 [SF]: Skip {fun_name} for this pack?\n'
                                f'5 [AB]: Abort this script?\n'
                                f'  [#/RP/RF/SP/SF/AB] ')
                log(f'User chose {user_in}.', logging.DEBUG)
                if not user_in:
                    log('Empty user input. Re-prompting...', logging.DEBUG)
                    continue
                match user_in.upper():
                    case '1' | 'RP':
                        log(f'Attempting failed command again.', logging.INFO)
                        return ErrorHandling.RETRY_PART
                    case '2' | 'RF':
                        log(f'Rerunning {fun_name}.', logging.INFO)
                        return ErrorHandling.RETRY_FULL
                    case '3' | 'SP':
                        log(f'Skipping this failed command in particular.', logging.INFO)
                        return ErrorHandling.SKIP_PART
                    case '4' | 'SF':
                        log(f'Skipping {self.name} {fun_name}.', logging.INFO)
                        return ErrorHandling.SKIP_FULL
                    case '5' | 'AB':
                        log('Aborting script. See log for more information.', logging.INFO)
                        exit(1)
                log(f'Could not match {user_in} with anything. Re-prompting...', logging.DEBUG)
        elif error_handling == ErrorHandling.RETRY_PART:
            log('Attempting failed command again.', logging.INFO)
            return ErrorHandling.RETRY_PART
        elif error_handling == ErrorHandling.RETRY_FULL:
            log(f'Rerunning {self.name} {fun_name}.', logging.INFO)
            return ErrorHandling.RETRY_FULL
        elif error_handling == ErrorHandling.SKIP_PART:
            log(f'Skipping the failed command.', logging.INFO)
            return ErrorHandling.SKIP_PART
        elif error_handling == ErrorHandling.SKIP_FULL:
            log(f'Skipping {self.name} {fun_name}.', logging.INFO)
            return ErrorHandling.SKIP_FULL
        else:
            log(f'Aborting due to error doing {fun_name} on {self.name}.\n'
                f'See log for more information.', logging.ERROR)
            exit(1)

    def install(self, runner: Runner):
        """
        Performs an installation of the pack.

        Command subprocesses are separated by delimiter "\n\n".

        Defines the following aliases (detected by alias_prefix followed by the alias name):
            INSTALL_APPS : App install command designated by apps['install_type']
            INSTALL_FILES : File install command designated by files['backup_type']['EXTRACT']

        If settings['install_cmd'] is an empty string, automatically append aliases at end.
        This will only happen if install_cmd is empty.

        :param runner: Runner object to run commands from.
        """
        if self.is_installed:
            return True

        if self.settings['depends']:
            for pack in packs:
                if pack.name in self.settings['depends']:
                    pack.install(runner)

        alias_prefix = Predefined.alias_prefix
        apps = self.settings['apps']['apps'] if self.settings['apps'] else None
        install_apps_cmd = Predefined.app_install_types[self.settings['apps']['install_type']] \
                           if apps is not None else ''
        files = self.settings['files']['files'] if self.settings['files'] else None
        install_files_cmd = Predefined.file_backup_types[self.settings['files']['backup_type']]['EXTRACT'] \
                            if files is not None else ''

        cmds = self.settings['custom']['install_cmd'] if self.settings['custom'] \
            else f'{alias_prefix}INSTALL_APPS\n\n{alias_prefix}INSTALL_FILES'

        cmd_list = re.split('|'.join(map(re.escape, ['\n\n', ' \\\n'])), cmds)
        for cmd in cmd_list:
            if f'{alias_prefix}INSTALL_APPS' in cmd:
                success = runner.run(cmd.replace(f'{alias_prefix}INSTALL_APPS', install_apps_cmd), apps)
            elif f'{alias_prefix}INSTALL_FILES' in cmd:
                success = runner.run(cmd.replace(f'{alias_prefix}INSTALL_FILES', install_files_cmd), files)
            else:
                success = runner.run(cmd)
            if not success:
                # TODO: error handling
                return False
        return True

    def backup(self) -> bool:
        """
        Performs a backup on the pack.

        BACKUP_FILES : files backup command designated by files['backup_type']

        :param runner: Runner object to run commands from.
        :return: True if any errors occurred; False otherwise.
        """
        # TODO
        return True

    def __str__(self, verbose=True):
        rtn = []

        def append_dict(a_dict: dict, lvl: int):
            for key, val in a_dict.items():
                if isinstance(val, dict):
                    rtn.append("\t" * lvl + f'{key}:')
                    append_dict(val, lvl + 1)
                else:
                    rtn.append(('\t' * lvl) + f'{key}: ' +
                               (f'\n{val}'.replace('\n', '\n' + '\t' * (lvl + 1))
                                if isinstance(val, str) and '\n' in val else
                                val.name if issubclass(type(val), Enum) else str(val)))

        rtn += [f'name: {self.name}']
        if verbose:
            append_dict(self.settings, 0)
        else:
            rtn += [f'apps: {self.settings["apps"]}',
                    f'files: {self.settings["files"]}']

        return '\n'.join(rtn)


packs: list[Pack] = []
