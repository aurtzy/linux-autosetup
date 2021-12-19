from enum import Enum
from Runner import get_passwd, run

class BackupType(Enum):
    """
    Backup method used.

    COPY: Copy files

    COMPRESS: Compress files

    ENCRYPT: Encrypt files
    """
    COPY = 1
    COMPRESS = 2
    ENCRYPT = 3


class HandleBackupErrors(Enum):
    """
    How backup errors should be handled.

    PROMPT: Prompt users to handle errors

    IGNORE: Ignore errors and continue with backup

    ABORT: Abort and skip backups that have errors
    """
    PROMPT = 1
    IGNORE = 2
    SKIP = 3


class Pack:
    """
    Contains installation and backup functions.



    Pack global settings: class variables that are used by default if not overridden by constructor
        install_cmd: str
            Command(s) that are run through shell when calling install()

        backup_type: BackupType
            Type of backup to perform

        backup_keep: int
            How many old backups to keep - 0 = single backup; 3 = 4 backups, with 3 old saved

        dump_dir: str
            Directory to dump old backups to

        tmp_dir: str
            Temporary directory for creating backups


    """
    packs = []
    backup_paths: list[str] = None
    install_cmd: str = None
    backup_type: BackupType = None
    backup_keep: int = None
    dump_dir: str = None
    tmp_dir: str = None

    def __init__(self,
                 apps: list[str] = None, backup_sources: list[str] = None, backup_paths: list[str] = None,
                 install_cmd: str = install_cmd, backup_type: BackupType = backup_type, backup_keep: int = backup_keep,
                 dump_dir: str = dump_dir, tmp_dir: str = tmp_dir):
        self.apps = [] if apps is None else apps
        self.backup_sources = [] if backup_sources is None else backup_sources
        self.backup_paths = [] if backup_paths is None else backup_paths
        self.install_cmd = install_cmd
        self.backup_type = backup_type
        self.backup_keep = backup_keep
        self.dump_dir = dump_dir
        self.tmp_dir = tmp_dir
        Pack.packs.append(self)

    def install(self) -> int:
        get_passwd()
        return_code = run(self.install_cmd)
        if return_code != 0:
            return return_code
