import enum
import re
import typing
from typing import TypedDict
from aenum import Enum, extend_enum

from runner import Runner


class Predefined:
    """
    Predefined modifiable values.

    alias_prefix: str
        Used as a prefix to alias names in strings. Indicates substitution with aliases.
    AppInstallTypes: Enum
        Types of install commands that can be used.
    FilesBackupTypes: Enum
        Types of file install/backup commands that can be used.
    """
    alias_prefix = '//'

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

    install_type: str
        Indicates type of install command to use.
        Key to Predefined.app_install_types dictionary.
    """
    install_type: Predefined.AppInstallTypes


class FileSettings(TypedDict):
    """
    File-specific settings.

    backup_type: str
        Indicates type of backup is performed.
        A str represents a key to Predefined.file_backup_types dictionary.
    backup_keep: int
        Number of old backups to keep before dumping.
    dump_dir: str
        Designated directory to dump any files to.
    tmp_dir: str
        Designated directory to keep temporary files in.
    """
    backup_type: Predefined.FileBackupTypes
    backup_paths: list[str]
    backup_keep: int
    dump_dir: str
    tmp_dir: str


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
    app_settings: typing.Union[AppSettings, None]
    files: list[str]
    file_settings: typing.Union[FileSettings, None]
    install_cmd: str
    backup_cmd: str
    error_handling: ErrorHandling


class Predefined:
    """
    Predefined modifiable values.

    alias_prefix: str
        Used as a prefix to alias names in strings. Indicates substitution with aliases.
    app_install_types: dict[str, str]
        Types of install commands that can be used.
    file_backup_types: dict[str, dict[str, str]]
        Types of file install/backup commands that can be used.
    fallback_settings: Settings
        Fallback settings for use with a config parser.
        Some default values are meant to raise errors since they may
        not have a sane default that can be set without user intervention.
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

    fallback_settings: Settings = Settings(depends=[],
                                           apps=[],
                                           app_settings=AppSettings(
                                               install_type=''),
                                           files=[],
                                           file_settings=FileSettings(
                                               backup_type='',
                                               backup_paths=['./backups'],
                                               backup_keep=1,
                                               dump_dir='/tmp/linux-autosetup-dump',
                                               tmp_dir='/tmp/linux-autosetup'),
                                           install_cmd='',
                                           backup_cmd='',
                                           error_handling=ErrorHandling.PROMPT
                                           )


class Pack:
    """Contains various settings and functions for installing and backing up stuff."""

    def __init__(self, name: str, settings: Settings):
        self.name = name
        self.settings = settings

        # TODO: set up aliases here?
        self.is_installed = False
        self.is_backed_up = False
        packs.append(self)


    def install(self, runner: Runner) -> bool:
        """
        Performs an installation of the pack.

        Command subprocesses are separated by delimiters "\n\n" or " \\\n".

        Makes use of aliases, which are defined by appending Pack.alias_prefix to the alias name
        (e.g. INSTALL_APPS alias would be defined as "//INSTALL_APPS" in cmds.

        Substitutes the following aliases:
            INSTALL_APPS : App install command designated by apps['install_type']
            INSTALL_FILES : File install command designated by files['backup_type']['EXTRACT']

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
                    rtn.append(('\t' * lvl) + f'{key}: ' + (f'\n{val}'.replace('\n', '\n' + '\t' * (lvl + 1))
                                                            if isinstance(val, str) and '\n' in val else
                                                            val.name if issubclass(type(val), Enum) else str(val)))

        rtn += [f'name: {self.name}',
                f'apps: {self.settings["apps"]}',
                f'files: {self.settings["files"]}']
        if verbose:
            append_dict(self.settings, 0)

        return '\n'.join(rtn)


packs: list[Pack] = []
