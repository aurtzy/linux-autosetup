import typing
from typing import TypedDict
from enum import Enum
from runner import Runner
from dataclasses import dataclass


class Predefined:
    """
    Predefined values
    """
    backup_cmds: dict[str, dict[str, str]] = {
        'COPY': {
            'CREATE': 'COMMAND',
            'EXTRACT': 'COMMAND'
        },
        'COMPRESS': {
            'CREATE': 'COMMAND',
            'EXTRACT': 'COMMAND'
        },
        'ENCRYPT': {
            'CREATE': 'COMMAND',
            'EXTRACT': 'COMMAND'
        }
    }



        def __str__(self):
            return self.name

@dataclass
class Settings:
    """
    backup_types: dict[str, dict[str, str]]
        Holds all types of backup methods, including their 'CREATE' and 'EXTRACT' commands.
        Can be modified and added to.

    ErrorHandling: class(Enum)
        Enum class that denotes how errors should be handled.
    """
    # global_settings: dict[str, object] = {
    #     'backup_types': 'hi'
    # }
    #


    class Default(TypedDict):
        install_cmd: str
        backup_type: typing.Union[str, dict[str, str]]
        paths: list[str]
        keep_old: int
        dump_dir: str
        tmp_dir: str
        placeholder_str: str

    class Local(Default):
        apps: list[str]
        backup_sources: list[str]



class Pack:
    """Contains various settings and functions for installing and backing up stuff."""

    class AppSettings(TypedDict):


    class BackupSettings(TypedDict):
        """
        Configurable backup-specific settings.

        paths: str
            Denotes locations for created backups. Paths should be formatted to work in a shell.

        backup_type
        """
        backup_type: typing.Union[str, dict[str, str]]
        paths: list[str]
        keep_old: int
        dump_dir: str
        tmp_dir: str


    class SettingsTEMP(TypedDict, total=False):
        """
        Configurable global settings for packs, which can be overridden in instances.

        SETTINGS:
            app_install_cmd : str
                Default install command used when apps in pack exist. May require formatting.

            Custom commands :
                More flexible string commands that allow for substitution of other commands like app_install_cmd

                custom_install_cmd : str
                    When exists, will run in place of app_install_cmd.
                    Will be run through substitution.

                custom_backup_cmd : dict[str, str]
                    When exists, are run in place of normal backup commands.
                    Will be run through substitution.

            backup_paths : list[str]
                List of paths to back up. This should take in already formatted path strings that work in a shell.
                backup_paths[0] will be used as the target path for moving a created backup from tmp_dir,
                so it is recommended that backup_paths[0] be on the same partition as tmp_dir.
                Will be run through substitution.

            backup_type : str
                A key to backup_types. Indicates what type of backup is performed,
                which also obtains its corresponding 'CREATE' and 'EXTRACT' commands from backup_types.
                These commands may require formatting.

            backup_keep : int
                Must be a natural number. Denotes how many old backups should be kept.

            dump_dir : str
                Directory to dump old backups to when exceeding backup_keep.

            tmp_dir : str
                Temporary directory for creating backups.


        """
        install_cmd: str
        error_handling: Predefined.ErrorHandling



    packs = []

    placeholder_str = '$%s$'

    global_settings: Settings = Settings(
        install_cmd='',
        create_backup_cmd='',
        extract_backup_cmd='',
        backup_paths=[],
        backup_type='COPY',
        backup_keep=0,
        dump_dir='./dump',
        tmp_dir='./tmp',
        error_handling=Predefined.ErrorHandling.PROMPT
    )

    def __init__(self, pack_name: str, apps: list[str] = None, backup_sources: list[str] = None
                 , settings: Settings = None,
                 substitutions: dict[str, str] = None):
        """
        Will perform checking on some settings and throw an error if an invalid value is found.

        Initialize 'substitutions' dictionary, which can be used to

        :param pack_name: str                   Name of the pack.
        :param apps: list[str]                  App names assigned to this pack meant to be paired with installing.
        :param backup_sources: list[str]        Paths assigned to this pack which denote backup sources.
        :param enable_backups: bool             Enables/disables backup functionalities.
        :param settings: Settings               Dictionary of pack-specific settings to set locally.
                                                If a key-value pair is present, override the global setting.
        :param substitutions: dict[str, str]    Dictionary of keywords that can be used to substitute strings.
        """
        self.pack_name: str = pack_name
        self.apps: list[str] = apps if apps else []
        self.backup_sources: list[str] = backup_sources if backup_sources else []

        self.settings: Pack.Settings = self.global_settings
        if settings is not None:
            self.settings.update(settings.copy())

        if self.settings['backup_type'] not in Predefined.backup_types.keys():
            raise Exception('Unable to find backup_type "%s".' % settings['backup_type'])
        if self.settings['backup_keep'] < 0:
            raise Exception('Having %s backups is not allowed.' % settings['backup_keep'])

        self.substitutions: dict[str, str] = {
            'apps': ' '.join(self.apps),
            'backup_sources': ' '.join(self.backup_sources),
            'install_cmd': self.settings['install_cmd'] if self.settings['install_cmd'] else '',
            'create_backup_cmd': Predefined.backup_types[self.settings['backup_type']]['CREATE'],
            'extract_backup_cmd': Predefined.backup_types[self.settings['backup_type']]['EXTRACT'],
            'backup_paths': ' '.join(list(self.settings['backup_paths'])) if self.settings['backup_paths'] else ''

        }
        if substitutions:
            self.substitutions.update(substitutions)
        for key, val in self.substitutions.items():
            old_value = ''
            while old_value != val:
                old_value = val
                self.substitutions[key] = self.substitute(val)
                if self.placeholder_str % key in val:
                    raise Exception('Script will loop infinitely trying to substitute %s.' % key)

        for key, val in self.settings.items():
            if isinstance(val, str):
                print(val)
                self.settings[key] = self.substitute(val)

        Pack.packs.append(self)

    def substitute(self, string: str) -> str:
        """
        Perform substitution on a given string using the substitutions dictionary.

        Uses $var$ in order to find keywords.
        """
        for var, replacement in self.substitutions.items():
            string = string.replace(self.placeholder_str % var, replacement)
        return string

    def backup_sources_exist(self) -> (bool, list[str]):
        """

        :return: (True, []) if all backup sources exist. Otherwise, return (False, nonexistent sources)
        """
        return True, []

    def install(self, runner: Runner) -> bool:
        """
        Install pack, running any existing install_cmd and installing backups to appropriate paths

        :return: True if install completed successfully; False otherwise
        """
        return_code = None
        if self.settings['install_cmd']:
            # perform substitution
            return_code = runner.run('echo thy command shall be executed')
        elif len(self.apps) == 0:
            # perform substitution on app_install_cmd
            return_code = runner.run('echo THY COMMAND SHALL BE EXECUTED')
        if return_code != 0 and return_code is not None:
            return False

        return True

    def backup(self, runner: Runner) -> bool:
        """
        Back up pack, using appropriate backup type to create new backups to store in backup_paths

        :return: True if backup completed successfully; False otherwise
        """
        return True

    def __str__(self, verbose: bool = False) -> str:
        """
        Returns a string with the format:
            pack_name: $name
            apps: $apps
            backup_sources: $backup_sources
            Settings:
                $settings

        $var represents str(var), where var is the label.

        :param verbose: bool    Whether returned string should show all settings.
        """
        return 'pack_name: %s\napps: %s\nbackup_sources: %s\nSettings:\n%s' % (
            self.pack_name,
            self.apps,
            self.backup_sources,
            '\n'.join(list(map(lambda pair: '    %s: %s' % (pair[0], pair[1]),
                               self.settings.items())))
        )
