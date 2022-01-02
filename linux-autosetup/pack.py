import logging
import os.path
import re
import typing
from typing import TypedDict
from aenum import Enum, extend_enum, auto

from lib.runner import run
from lib.logger import log
from lib.configurable import *


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
            while True:
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
                        log(f'Attempting failed command again.', logging.ERROR)
                        return ErrorHandling.RETRY_PART
                    case '2' | 'RF':
                        log(f'Rerunning {fun_name}.', logging.ERROR)
                        return ErrorHandling.RETRY_FULL
                    case '3' | 'SP':
                        log(f'Skipping this failed command in particular.', logging.ERROR)
                        return ErrorHandling.SKIP_PART
                    case '4' | 'SF':
                        log(f'Skipping {self.name} {fun_name}.', logging.ERROR)
                        return ErrorHandling.SKIP_FULL
                    case '5' | 'AB':
                        log('Aborting script. See log for more information.', logging.ERROR)
                        exit(1)
                log(f'Could not match {user_in} with anything. Re-prompting...', logging.DEBUG)
        elif error_handling == ErrorHandling.RETRY_PART:
            log('Attempting failed command again.', logging.ERROR)
            return ErrorHandling.RETRY_PART
        elif error_handling == ErrorHandling.RETRY_FULL:
            log(f'Rerunning {self.name} {fun_name}.', logging.ERROR)
            return ErrorHandling.RETRY_FULL
        elif error_handling == ErrorHandling.SKIP_PART:
            log(f'Skipping the failed command.', logging.ERROR)
            return ErrorHandling.SKIP_PART
        elif error_handling == ErrorHandling.SKIP_FULL:
            log(f'Skipping {self.name} {fun_name}.', logging.ERROR)
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
