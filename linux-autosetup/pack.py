from typing import TypedDict
from enum import Enum


class AppSettings(TypedDict):
    apps: list[str]
    install_type: str


class FileSettings(TypedDict):
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
    apps: AppSettings
        App-related settings.
    files: FileSettings
        File-related settings.
    error_handling: ErrorHandling
        Indicates how script will handle errors.
    """
    depends: list[str]
    apps: AppSettings
    files: FileSettings
    error_handling: ErrorHandling


class Pack:
    """Contains various settings and functions for installing and backing up stuff."""

    var_string = '//'

    fallback_settings = Settings(depends=[],
                                 apps=AppSettings(apps=[],
                                                  install_type=''),
                                 files=FileSettings(files=[],
                                                    backup_type='COPY',
                                                    backup_paths=['./backups'],
                                                    backup_keep=0,
                                                    dump_dir='./dump',
                                                    tmp_dir='./tmp'),
                                 error_handling=ErrorHandling.PROMPT)

    def __init__(self, settings: Settings):
        self.settings = settings

    def install(self) -> bool:
        """
        TODO: docs
        :return:
        """
        # TODO
        return True

    def backup(self) -> bool:
        """
        TODO: docs
        :return:
        """
        # TODO
        return True
