import logging
from collections.abc import Mapping
from typing import TypedDict

from lib.logger import log


class AppsModuleSettings(TypedDict):
    install_cmd_types: dict[str, str]


class FilesModuleSettings(TypedDict):
    install_cmd_types: dict[str, str]
    backup_cmd_types: dict[str, str]


class SystemCmdsSettings(TypedDict):
    superuser: str
    cp: str
    mv: str
    mkdir: str
    validate_path: str
    validate_dir: str


class GlobalSettings(TypedDict):
    noconfirm: bool
    apps_module: AppsModuleSettings
    files_module: FilesModuleSettings
    system_cmds: SystemCmdsSettings


global_settings: GlobalSettings = {
    'noconfirm': False,
    'apps_module': {
        'install_cmd_types': {
            'flatpak': 'flatpak install -y --noninteractive $@',
            'apt': 'sudo apt --assume-yes install $@',
            'pacman': 'sudo pacman -S --noconfirm --needed $@',
            'yay': 'yay -S --noconfirm --needed $@'
        }
    },
    'files_module': {
        'install_cmd_types': {
            'copy': '',
            'hardlink': '',
            'tar_copy': 'tar -xPf "$1.tar"',
            'compress': 'tar -xPf "$1.tar.xz"',
            'encrypt': 'openssl enc -d -aes-256-cbc -md sha512 -pbkdf2 -salt -in "$1.tar.xz.enc" | tar -xPf -'
        },
        'backup_cmd_types': {
            'copy': '',
            'hardlink': '',
            'tar_copy': 'tar -cPf "$1.tar" "${@:2}"',
            'compress': 'tar -cJPf "$1.tar.xz" "${@:2}"',
            'encrypt': 'tar -cJPf - "${@:2}" | '
                       'openssl enc -e -aes-256-cbc -md sha512 -pbkdf2 -salt -out "$1.tar.xz.enc"'
        }
    },
    'system_cmds': {
        'superuser': 'sudo',
        'cp': 'cp -at "$1" "${@:2}"',
        'mv': 'mv -t "$1" "${@:2}"',
        'mkdir': 'mkdir -p "$1"',
        'validate_path': '[ -e "$1" ]',
        'validate_dir': '[ -d "$1" ]'
    }
}


def update_global_settings(new: dict):
    """
    Preferred over using something like dict's update() which may undesirably remove predefined settings as
    a result of its shallow updating.

    Manually updates each setting in global_settings individually in order to accurately filter
    user-typed configurations and make sure no significant errors are present before
    the script uses them.
    """

    def update(*args, t):
        """
        Updates the given setting. Each arg represents one level into the settings.

        If the type is dict,
        """
        setting = args[-1]
        log(f'Attempting to update {setting}.', logging.DEBUG)

        g_s = global_settings
        for arg in args[:-1]:
            g_s = g_s[arg]
        n = new
        for arg in args[:-1]:
            if not isinstance(n.get(arg), Mapping):
                log(f'Could not find path to {setting}. Nothing to change here.', logging.INFO)
                return
            n = n[arg]

        if n.get(setting) is None:
            log(f'{setting} is not present. Nothing to change here.', logging.INFO)
        else:
            if isinstance(n[setting], t):
                if t is dict:
                    g_s[setting].update(n[setting])
                else:
                    g_s[setting] = n.get(setting)
                log(f'Updating {setting} to be {g_s[setting]}.', logging.INFO)

            else:
                log(f'Could not match {n[setting]} with {setting}\'s type. This setting will be ignored.',
                    logging.WARNING)

    # noconfirm
    update('noconfirm', t=bool)

    # apps_module
    update('apps_module', 'install_cmd_types', t=dict)

    # files_module
    update('files_module', 'install_cmd_types', t=dict)
    update('files_module', 'backup_cmd_types', t=dict)

    # path_ops
    update('path_ops', t=dict)
