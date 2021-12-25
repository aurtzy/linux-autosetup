import typing
from typing import TypedDict
from enum import Enum

from runner import Runner


class Predefined:
    """
    Predefined modifiable values.

    alias_prefix: str
        Used as a prefix to alias names in strings. Indicates substitution with aliases.
    app_install_types: dict[str, str]
        Types of install commands that can be used.
    file_backup_types: dict[str, dict[str, str]]
        Types of file install/backup commands that can be used.
    """
    alias_prefix = '//'

    app_install_types: dict[str, str] = {
        'FLATPAK': 'flatpak install -y --noninteractive $@'
    }
    file_backup_types: dict[str, dict[str, str]] = {
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
    }


class AppSettings(TypedDict):
    """
    App-specific settings.

    apps: list[str]
        List of apps.
    install_type: str
        Indicates type of install command to use. Key to Predefined.app_install_types dictionary.
    """
    apps: list[str]
    install_type: str


class FileSettings(TypedDict):
    """
    File-specific settings.

    files: list[str]
        List of files.
    backup_type: str | dict[str, str]
        Indicates type of backup is performed.
        A str represents a key to Predefined.file_backup_types dictionary.
        A dict[str, str] denotes a custom-defined backup type.
    backup_keep: int
        Number of old backups to keep before dumping.
    dump_dir: str
        Designated directory to dump any files to.
    tmp_dir: str
        Designated directory to keep temporary files in.
    """
    files: list[str]
    backup_type: str
    backup_paths: list[str]
    backup_keep: int
    dump_dir: str
    tmp_dir: str


class CustomSettings(TypedDict):
    """
    Custom install/backup commands that allow wider flexibility with
    running commands.

    Can make use of aliases, which are defined by appending Pack.var_string to the var name
    (e.g. INSTALL_APPS alias would be defined as "//INSTALL_APPS" in install_cmd.

    install_cmd: str
        Command(s) that will be run when calling install() after substituting aliases.
        Defines the following aliases:
            INSTALL_APPS : app install command designated by apps['install_type']
            INSTALL_FILES : files install command designated by files['backup_type']
    backup_cmd: str
        Command(s) that will be run when calling backup() after substituting aliases.
        Defines the following aliases:
            BACKUP_FILES : files backup command designated by files['backup_type']
    """
    install_cmd: str
    backup_cmd: str


class ErrorHandling(Enum):
    """Indicates how script should handle errors."""
    PROMPT = 1
    SKIP = 2
    ABORT = 3

    def __str__(self):
        return self.name


class Settings(TypedDict):
    """
    Main Pack class settings.

    depends: list[str]
        List of pack names that the pack depends on, which should be installed first.
        Relevant when calling install().
    apps: AppSettings | NoneType
        App-related settings.
    files: FileSettings | NoneType
        File-related settings.
    error_handling: ErrorHandling
        Indicates how script will handle errors.
    """
    depends: list[str]
    apps: typing.Union[AppSettings, None]
    files: typing.Union[FileSettings, None]
    custom: typing.Union[CustomSettings, None]
    error_handling: ErrorHandling


class Pack:
    """Contains various settings and functions for installing and backing up stuff."""

    def __init__(self, name: str, settings: Settings):
        self.name = name
        self.settings = settings
        self.is_installed = False
        self.is_backed_up = False
        packs.append(self)

    def install(self, runner: Runner) -> bool:
        """
        Performs an installation of the pack.

        :param runner: Runner object to run commands from.
        :return: True if any errors occurred; False otherwise.
        """
        if self.is_installed:
            return True

        if self.settings['depends']:
            for pack in packs:
                if pack.name in self.settings['depends']:
                    pack.install(runner)

        alias_prefix = Predefined.alias_prefix

        install_cmd = self.settings['custom']['install_cmd'] if self.settings['custom'] else ''

        if '%sINSTALL_APPS' % alias_prefix not in install_cmd:
            install_cmd += '\n%sINSTALL_APPS' % alias_prefix
        if '%sINSTALL_FILES' % alias_prefix not in install_cmd:
            install_cmd += '\n%sINSTALL_FILES' % alias_prefix

        if self.settings['apps']:
            app_settings: AppSettings = self.settings['apps']
            install_cmd.replace('%sINSTALL_APPS' % alias_prefix,
                                Predefined.app_install_types[app_settings['install_type']])
            apps = app_settings['apps']
        else:
            install_cmd.replace('%sINSTALL_APPS' % alias_prefix, '')
            apps = []

        if self.settings['files']:
            file_settings: FileSettings = self.settings['files']
            install_cmd.replace('%sINSTALL_FILES' % alias_prefix,
                                Predefined.file_backup_types[file_settings['backup_type']]['EXTRACT'])
        else:
            install_cmd.replace('%sINSTALL_FILES' % alias_prefix, '')

        success = runner.run(install_cmd, apps)
        if success:
            self.is_installed = True
            return True
        else:
            return False

    def backup(self) -> bool:
        """
        Performs a backup on the pack.

        :param runner: Runner object to run commands from.
        :return: True if any errors occurred; False otherwise.
        """
        # TODO
        return True


packs: list[Pack] = []
