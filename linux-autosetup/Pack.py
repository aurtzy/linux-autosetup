from enum import Enum
from Runner import get_passwd, run


class BackupType(Enum):
    """
    Backup method used.

    COPY : Copy files

    COMPRESS : Compress files

    ENCRYPT : Encrypt files
    """
    COPY = 1
    COMPRESS = 2
    ENCRYPT = 3


class HandleBackupErrors(Enum):
    """
    How backup errors should be handled.

    PROMPT : Prompt users to handle errors

    IGNORE : Ignore errors and continue with backup

    ABORT : Abort and skip backups that have errors
    """
    PROMPT = 1
    IGNORE = 2
    SKIP = 3


class Pack:
    """
    Contains installation and backup functions.

    "GLOBAL" class variables that are used by default if not overridden by constructor
        install_cmd : str
            Command(s) that are run through shell when calling install()

        backup_paths : list[str]
            List of paths to back up

        backup_type : BackupType
            Type of backup to perform

        backup_keep : int
            How many old backups to keep - 0 = single backup; 3 = 4 backups, with 3 old backups saved

        dump_dir : str
            Directory to dump old backups to

        tmp_dir : str
            Temporary directory for creating backups

    Pack-specific variables:
        apps : list[str]
            App names that are substituted with $apps in install_cmd

        backup_sources : list[str]
            Paths to files that should be backed up

    """
    packs = []
    install_cmd: str = None
    backup_paths: list[str] = None
    backup_type: BackupType = None
    backup_keep: int = None
    dump_dir: str = None
    tmp_dir: str = None

    def __init__(self,
                 apps: list[str] = None, install_cmd: str = install_cmd, backup_sources: list[str] = None,
                 backup_paths: list[str] = None, backup_type: BackupType = backup_type, backup_keep: int = backup_keep,
                 dump_dir: str = dump_dir, tmp_dir: str = tmp_dir):
        self.apps = apps if apps else []
        self.install_cmd = install_cmd
        self.backup_sources = backup_sources if backup_sources else []
        self.backup_paths = backup_paths if backup_paths else []
        self.backup_type = backup_type
        self.backup_keep = backup_keep
        self.dump_dir = dump_dir
        self.tmp_dir = tmp_dir
        Pack.packs.append(self)

    def install(self) -> bool:
        """
        Install pack, running any existing install_cmd and installing backups to appropriate paths

        :return: True if install completed successfully; False otherwise
        """
        get_passwd()
        return_code = run(self.install_cmd)
        if return_code != 0:
            return False

        return True

    def backup(self) -> bool:
        """
        Back up pack, using appropriate backup type to create new backups to store in backup_paths

        :return: True if backup completed successfully; False otherwise
        """
        return True
