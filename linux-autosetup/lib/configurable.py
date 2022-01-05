import logging

from aenum import Enum, extend_enum


# Superuser command, used to run things as root if needed.
# Uses 'sudo' by default.
from lib.logger import log

su_cmd: str = 'sudo'

# Copy command, used for copying files to locations.
cp_cmd: str = 'cp -at "$1" "${@:2}"'

# Move command, used for moving files to locations.
mv_cmd: str = 'mv -t "$1" "${@:2}'

# Command for creating directories.
mkdir_cmd: str = 'mkdir -p $1'

# TODO: still unsure about if this is necessary; marking for now
# set_file_perms =

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


# TODO: REMOVE AND MOVE TO configparser.py when making - TEMPORARY PLACEMENT
AppInstallType.add({
    'FLATPAK': 'flatpak install -y --noninteractive $@'
})

FileBackupType.add({
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
