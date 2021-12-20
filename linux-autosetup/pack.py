from enum import Enum
from runner import Runner


class Pack:
    """Contains various settings and functions for installing and backing up stuff."""

    class Settings:
        """
        Configurable global settings for packs, which can be overridden in instances.

        Certain strings - mainly commands - are unformatted, and are not injected with substitutions.

        All global settings should be set prior to creating any Pack objects.

        backup_types: dict[str, dict[str, str]]
            Holds all types of backups, including their 'CREATE' and 'EXTRACT' commands.
            Can be modified and added to.

        SETTINGS:
            app_install_cmd : str
                Default install command used when apps in pack exist. May require formatting.

            Custom commands :
                More flexible string commands that allow for substitution of other commands like app_install_cmd

                custom_install_cmd : str
                    When exists, will run in place of app_install_cmd. May require formatting.

                custom_backup_cmd : dict[str, str]
                    When exists, are run in place of normal backup commands. May require formatting.

            backup_paths : list[str]
                List of paths to back up. This should take in already formatted path strings that work in a shell.
                backup_paths[0] will be used as the target path for moving a created backup from tmp_dir,
                so it is recommended that backup_paths[0] be on the same partition as tmp_dir.

            backup_type : str
                A key to backup_types. Indicates what type of backup is performed,
                which also obtains its corresponding 'CREATE' and 'EXTRACT' commands from backup_types.
                These commands may require formatting.

            backup_keep : int
                Must be a natural number. Denotes how many old backups should be kept.

            backup_errors_handle : BackupErrorsHandle
                Determines how backup errors should be handled.

            dump_dir : str
                Directory to dump old backups to when exceeding backup_keep.

            tmp_dir : str
                Temporary directory for creating backups.
        """

        backup_types: dict[str, dict[str, str]] = {
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

        class ErrorHandling(Enum):
            """
            Determines how errors should be handled.

            PROMPT : Prompt users with options to handle errors.

            IGNORE : Ignore errors and continue working on pack.

            ABORT : Abort and skip this pack.
            """
            PROMPT = 1
            IGNORE = 2
            ABORT = 3

        app_install_cmd: str = None
        custom_install_cmd: str = None
        custom_backup_cmd: dict[str, str] = None
        backup_paths: list[str] = None
        backup_type: str = None
        backup_keep: int = None
        error_handling: ErrorHandling = None
        dump_dir: str = None
        tmp_dir: str = None

        def __init__(self, app_install_cmd: str = None,
                     custom_install_cmd: str = None, custom_backup_cmd: dict[str, str] = None,
                     backup_paths: list[str] = None, backup_type: str = None,
                     backup_keep: int = None, error_handling: ErrorHandling = None,
                     dump_dir: str = None, tmp_dir: str = None):
            if app_install_cmd:
                self.app_install_cmd = app_install_cmd
            if custom_install_cmd:
                self.custom_install_cmd = custom_install_cmd
            if custom_backup_cmd:
                self.custom_backup_cmd = custom_backup_cmd
            if backup_paths:
                self.backup_paths = backup_paths
            if backup_type:
                if backup_type not in self.backup_types:
                    raise Exception('Unable to find backup_type "%s".' % backup_type)
                self.backup_type = backup_type
            if backup_keep:
                if backup_keep < 0:
                    raise Exception('You may not have %s (backup_keep) backups.' % backup_keep)
                self.backup_keep = backup_keep
            if error_handling:
                self.error_handling = error_handling
            if dump_dir:
                self.dump_dir = dump_dir
            if tmp_dir:
                self.tmp_dir = tmp_dir

    packs = []

    def __init__(self, name: str, apps: list[str] = None, backup_sources: list[str] = None, settings: Settings = None):
        """
        :param name: str Name of the pack.
        :param apps: list[str] Apps that are substituted in app_install_cmd.
        :param backup_sources: list[str] Paths to back up, substituted in backup_cmd.
        :param settings: Settings
        """
        self.name = name
        self.apps = apps if apps else []
        self.backup_sources = backup_sources if backup_sources else []
        self.settings = settings if settings is not None else self.Settings()

        self.substitutions: dict[str, str] = {
            'apps': self.apps,
            'backup_sources': self.backup_sources,
            'app_install_cmd': self.settings.app_install_cmd,
            'create_backup_cmd': self.settings.backup_types[self.settings.backup_type]['CREATE'],
            'extract_backup_cmd': self.settings.backup_types[self.settings.backup_type]['EXTRACT'],
            'backup_paths': ' '.join(self.settings.backup_paths)
        }
        Pack.packs.append(self)

    def install(self, runner: Runner) -> bool:
        """
        Install pack, running any existing install_cmd and installing backups to appropriate paths

        :return: True if install completed successfully; False otherwise
        """
        return_code = None
        if self.settings.custom_install_cmd:
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

    def backup_sources_exist(self) -> (bool, list[str]):
        """

        :return: (True, None) if all backup sources exist. If they do not, return (False, nonexistent sources)
        """
        return True, []

