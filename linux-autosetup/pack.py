import logging
import os.path
import re
from dataclasses import dataclass
from aenum import Enum, extend_enum, auto

from lib.prompter import get_input
from lib.system import run, Path
from lib.logger import log


# mainly for use with install_cmd and backup_cmd in packs when requiring substitution of commands.
# Uses '//' by default.
alias_prefix: str = '//'


class AppInstallType(Enum):
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


class FileBackupType(Enum):
    """
    Types of file backup commands that can be used.

    This enum class can be added to.
    """

    def __str__(self):
        return self.name

    @classmethod
    def add(cls, backup_types: dict[str, dict[str, str]]):
        """
        Adds the entries of the given dictionary of backup types to this enum class.

        Expects str -> dict[str, str] dict pairs, with the dict having both a 'CREATE' and 'EXTRACT' key.
        """
        for k, v in backup_types.items():
            extract = v.get('EXTRACT')
            create = v.get('CREATE')
            if not isinstance(extract, str):
                log(f'Potential error assigning {extract} to the FileBackupType {k}.', logging.WARNING)
            if not isinstance(create, str):
                log(f'Potential error assigning {create} to the FileBackupType {k}.', logging.WARNING)
            extend_enum(cls, k, dict(EXTRACT=extract, CREATE=create))


class FileBackupPath(Enum):
    """
    Backup paths that can be used.

    This enum class can be added to.
    """

    def __str__(self):
        return f'{self.name} - {self.value}'

    @classmethod
    def add(cls, backup_paths: dict[str, Path], no_confirm: bool = False):
        """
        Adds the entries of the given dictionary of backup paths to this enum class.

        Will perform checks on each path to confirm if they are valid, prompting the user to either create
        the backup directory or skip adding it if it doesn't exist.

        If the no_confirm param is True, no prompts will be made, and the script will automatically create
        backup paths if they are missing and add them to the enum class.
        """
        for k, v in backup_paths.items():
            while True:
                skip = False
                if not isinstance(v, str):
                    log(f'Potential error assigning {v} to the FileBackupPath {k}.', logging.WARNING)
                if not os.path.exists(v):
                    log(f'Could not find an existing backup path {v}.', logging.WARNING)
                    if no_confirm:
                        log(f'Creating new backup path {v}.', logging.INFO)
                        Path.mkdir(v)
                    else:
                        log('Prompting user to handle.', logging.DEBUG)
                        i = get_input([['Try to add it again? If it\'s on another drive, check if it is mounted.', 'T'],
                                       ['Create this backup path and add it?', 'C'],
                                       ['Skip adding this backup path?', 'S'],
                                       ['Abort script?', 'A']],
                                      pre_prompt='How do you want to handle this?')
                        match i:
                            case 0:
                                log('Trying again to add backup path.', logging.INFO)
                                continue
                            case 1:
                                log(f'Creating new backup path {v}.', logging.INFO)
                                Path.mkdir(v)
                            case 2:
                                log(f'Skipping this backup path - it will not be added.', logging.INFO)
                                skip = True
                                break
                            case _:
                                log('Aborting script.', logging.INFO)
                                exit(1)
                break
            if not skip:
                log(f'Adding FileBackupPath {k}: "{v}"', logging.DEBUG)
                extend_enum(cls, k, v)


class ErrorHandling(Enum):
    """
    Indicates how script should handle errors.

    PROMPT is the only option that should facilitate user input.

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


@dataclass
class Settings:
    """
    pack_name: str
        Name of the pack these settings will be assigned to.
    error_handling: ErrorHandling
        Indicates how script will handle errors.
    depends: list[str]
        List of pack object names that a pack depends on, which should be installed first.
        Relevant when calling install().
        Implementations may want to check whether all names are valid before using.
    apps: Apps
        Contains all app-related settings for the pack.
    files: Files
        Contains all file-related settings for the pack.
    install_cmd: str
        Command to run in a shell when the pack install method is called.
        Makes use of aliases specified in the install method.
        Empty by default, but can be assigned custom commands.
    backup_cmd: str
        Command to run in a shell when the pack backup method is called.
        Makes use of aliases specified in the backup method.
        Empty by default, but can be assigned custom commands.
    """

    @dataclass
    class Apps:
        """
        App-specific settings.

        apps: list[str]
            List of app names used in installation.
        install_type: AppInstallTypes
            Indicates the type of install command to use.

        Implements __iter__, which iterates through the apps list.
        """
        apps: list[str]
        install_type: AppInstallType

        def __iter__(self):
            for app in self.apps:
                yield app

    @dataclass
    class Files:
        """
        File-specific settings.

        files: list[str]
            List of file paths that are or will be backed up.
        backup_type: FileBackupTypes
            Indicates the type of backup performed on files.
        backup_paths: list[FileBackupPath]
            Denotes paths where backups are stored.
            Must have a length of at least one.
        backup_keep: int
            Number of old backups to keep before dumping.
            If set to -1, script will keep all backups made and not dump old ones.
            If set to 0, only the most recent made one in a backup path is kept.

        Implements __iter__, which iterates through the files list.
        """
        files: list[str]
        backup_type: FileBackupType
        backup_paths: list[FileBackupPath]
        backup_keep: int

        def __iter__(self):
            for file in self.files:
                yield file

    pack_name: str
    error_handling: ErrorHandling
    depends: list[str] | None = None
    apps: Apps | None = None
    files: Files | None = None
    install_cmd: str = ''
    backup_cmd: str = ''

    def __post_init__(self):
        """
        Checks validity of given settings.

        apps:
            If apps exists and apps.apps is empty, log a warning and set apps to None. This is because app
            settings only have an effect on the apps in the list, but if it is empty, the user must have
            set it without giving a list of apps which may be an error.
        files:
            Similarly to checking apps, if files is not None and files.files is empty, log a warning
            and set files to None.
        files.backup_paths:
            Raise an AssertionError if the list is empty.
        files.backup_keep:
            Can never be less than zero. This is impossible. Raises AssertionError.
            Excludes -1, because that is a special number.
        """
        if self.apps is not None and len(self.apps.apps) == 0:
            log(f'App settings were set for {self.pack_name}, but the apps list is empty. These settings '
                f'will be ignored.', logging.WARNING)
            self.apps = None
        if self.files is not None and len(self.files.files) == 0:
            log(f'File settings were set for {self.files}, but the files list is empty. These settings '
                f'will be ignored.', logging.WARNING)
            self.files = None

        try:
            assert len(self.files.backup_paths) > 0
        except AssertionError:
            log(f'The pack {self.pack_name} was initialized without any backup paths. The script cannot function\n'
                f'without at least one set; please fix.', logging.CRITICAL)
            raise
        try:
            assert self.files.backup_keep >= -1
        except AssertionError:
            log(f'No, you may not have a negative number of backups for {self.pack_name}. Pls fix.', logging.CRITICAL)
            raise


class Pack:
    """Contains various settings and functions for installing and backing up stuff."""

    alias_install_apps: str = f'{alias_prefix}INSTALL_APPS'
    alias_install_files: str = f'{alias_prefix}INSTALL_FILES'
    alias_backup_files: str = f'{alias_prefix}BACKUP_FILES'

    def __init__(self, settings: Settings):
        """
        This constructor will perform checks on values according to their respective docs,
        if any such prerequisites exist.

        :param settings: Pack settings.
        """
        log(f'Initializing Pack object for {settings.pack_name}.', logging.INFO)
        self.settings = settings
        self.attempted_install = False
        self.attempted_backup = False
        packs.append(self)
        log(f'Initialized pack {self.settings.pack_name} with the following settings:\n{str(self)}', logging.DEBUG)

    def get_cmd_error_handler(self, failed_cmd: str) -> int:
        """
        Called when there is an error running some cmd.

        Gets the desired error handler based on the error_handling pack setting.

        :param failed_cmd: Command that failed.
        :return: ErrorHandling enum that is not PROMPT, so the caller can take further action.
        """
        pack_name = self.settings.pack_name

        log(f'Attempting to handle command error...', logging.DEBUG)
        error_handling = self.settings.error_handling
        if error_handling == ErrorHandling.PROMPT:
            while True:
                log('Prompting user to handle error.', logging.DEBUG)
                user_in = input(f'Encountered an error while running commands for {pack_name}. Do you want to:\n'
                                f'1 [RP]: Try running the failed command again?\n'
                                f'2 [RF]: Restart commands from {pack_name}?\n'
                                f'3 [SP]: Skip just this failed command?\n'
                                f'4 [SF]: Skip {pack_name}?\n'
                                f'5 [AB]: Abort this script?\n'
                                f'  [#/RP/RF/SP/SF/AB] ')
                log(f'User chose {user_in}.', logging.DEBUG)
                match user_in.upper():
                    case '1' | 'RP':
                        log(f'Attempting failed command again.', logging.ERROR)
                        return ErrorHandling.RETRY_PART
                    case '2' | 'RF':
                        log(f'Restarting commands for {pack_name}.', logging.ERROR)
                        return ErrorHandling.RETRY_FULL
                    case '3' | 'SP':
                        log(f'Skipping this failed command in particular.', logging.ERROR)
                        return ErrorHandling.SKIP_PART
                    case '4' | 'SF':
                        log(f'Skipping {pack_name}.', logging.ERROR)
                        return ErrorHandling.SKIP_FULL
                    case '5' | 'AB':
                        log('Aborting script.', logging.ERROR)
                        exit(1)
                log(f'Could not match "{user_in}" with anything. Re-prompting...', logging.DEBUG)
        elif error_handling == ErrorHandling.RETRY_PART:
            log('Attempting failed command again.', logging.ERROR)
            return ErrorHandling.RETRY_PART
        elif error_handling == ErrorHandling.RETRY_FULL:
            log(f'Restarting commands for {pack_name}.', logging.ERROR)
            return ErrorHandling.RETRY_FULL
        elif error_handling == ErrorHandling.SKIP_PART:
            log(f'Skipping the failed command.', logging.ERROR)
            return ErrorHandling.SKIP_PART
        elif error_handling == ErrorHandling.SKIP_FULL:
            log(f'Skipping {pack_name}.', logging.ERROR)
            return ErrorHandling.SKIP_FULL
        else:
            log(f'Aborting due to an error running a command for {pack_name}.', logging.ERROR)
            exit(1)



    def install(self, runner: Runner):
        """
        Performs an installation of the pack.

        Command subprocesses are separated by delimiter "\n\n".

        Defines the following aliases (detected by alias_prefix followed by the alias name):
            INSTALL_APPS : App install command designated by apps['install_type']
            INSTALL_FILES : File install command designated by files['backup_type']['EXTRACT']

        Automatically append aliases at end if they are not found and apps/files lists in that
        order if they are not empty.

        :param runner: Runner object to run commands from.
        """
        if self.attempted_install:
            return
        if self.settings['depends']:
            for pack in packs:
                if pack.name in self.settings['depends'] and pack.name != self.name:
                    pack.install(runner)

        log(f'Installing {self.name}.', logging.INFO)

        alias_prefix = Predefined.alias_prefix

        apps = self.settings['apps']
        app_settings: AppSettings = self.settings['app_settings']
        install_apps_alias = f'{alias_prefix}INSTALL_APPS'

        files = self.settings['files']
        file_settings: FileSettings = self.settings['file_settings']
        install_files_alias = f'{alias_prefix}INSTALL_FILES'

        install_cmd = self.settings['install_cmd']

        if apps and install_apps_alias not in install_cmd:
            install_cmd += f'\n{install_apps_alias}'
            installed_apps = False
        else:
            installed_apps = True
        if files and install_files_alias not in install_cmd:
            install_cmd += f'\n{install_files_alias}'
            installed_files = False
        else:
            installed_files = True

        cmd_list = re.split(re.escape('\n\n'), install_cmd)
        cmd_list.reverse()
        log(f'Setting the following cmd_list stack to run: {cmd_list}', logging.DEBUG)

        while cmd_list:
            cmd = cmd_list.pop()
            if installed_apps is False and install_apps_alias in cmd:
                cmd = Predefined.AppInstallTypes[app_settings['install_type']] if apps else ''
                returncode = runner.run(cmd, apps)
                if returncode:
                    # TODO: implement handling what is done with commands after return
                    #       of handle_error in app and file install
                    self.handle_error(self.install)
                installed_apps = True
            elif installed_files is False and install_apps_alias in cmd:
                cmd = Predefined.FileBackupTypes[file_settings['backup_type']]['EXTRACT'] if files else ''
                # Assumes backup_paths setting is not empty because of init checking
                backup_paths = file_settings['backup_paths'].copy()
                backup_paths.reverse()
                log(f'Searching through the following backup_paths stack: {backup_paths}', logging.DEBUG)
                backup_path: str = ''

                def get_latest_backup():
                    # TODO: find the most recent backup and perform install with that
                    # can use os.path.getmtime(path) to retrieve last modified path, which actually
                    # might even be better
                    pass

                while backup_paths:
                    backup_path = backup_paths.pop() + f'/{self.name}'
                    log(f'Checking if {backup_path} exists...', logging.INFO)
                    if os.path.exists(backup_path):
                        log(f'Discovered {backup_path}.', logging.INFO)
                        break
                    else:
                        log(f'{backup_path} does not exist.', logging.INFO)
                    if not backup_paths:
                        # TODO
                        log(f'No existing backup path exists in the following list: ', logging.WARNING)
                        # TODO: handle error
                        error_handling = self.settings['error_handling']
                        if error_handling == ErrorHandling.PROMPT:
                            while True:
                                log('Prompting user to handle error.', logging.DEBUG)
                                user_in = input(f'No:\n'
                                                f'1 [RP]: Try running the command again?\n'
                                                f'2 [RF]: Restart {fun_name} and try again?\n'
                                                f'3 [SP]: Skip just this failed command?\n'
                                                f'4 [SF]: Skip {fun_name} for this pack?\n'
                                                f'5 [AB]: Abort this script?\n'
                                                f'  [#/RP/RF/SP/SF/AB] ')
                                log(f'User chose {user_in}.', logging.DEBUG)
                        elif error_handling <= ErrorHandling.RETRY_FULL:
                            pass
                        elif error_handling <= ErrorHandling.SKIP_FULL:
                            pass
                        else:
                            log('Aborting script.', logging.ERROR)
                            exit(1)
                backup_path = f'{backup_path}/{self.name}'
                returncode = runner.run(cmd, [backup_path])
                if returncode:
                    # TODO: see above in INSTALL_APPS
                    self.handle_error(self.install)
                installed_files = True
            else:
                returncode = runner.run(cmd)
                # TODO: handle error

        log(f'Successfully installed {self.name}!', logging.INFO)

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
