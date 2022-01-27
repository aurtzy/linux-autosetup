import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, is_dataclass, field

from lib.logger import log


@dataclass
class Settings:

    class Nested(ABC):
        @staticmethod
        @abstractmethod
        def from_dict(d: dict):
            pass

    @dataclass
    class CmdPreset(Nested):
        install_cmd: str = ''
        backup_cmd: str = ''

        @staticmethod
        def from_dict(d: dict) -> 'Settings.CmdPreset':
            return Settings.CmdPreset(
                install_cmd=d.get('install_cmd', ''),
                backup_cmd=d.get('backup_cmd', '')
            )

    def update(self, new: dict):
        log(f'Updating {self.__class__.__name__} with:\n'
            f'{new}', logging.DEBUG)

        def log_update_error(s, ignored):
            log(f'Encountered an unexpected value for {s}:\n'
                f'Ignoring setting {ignored}', logging.ERROR)
        for setting, tp in self.__annotations__.items():
            if new.get(setting) is None:
                continue

            if tp.__subclasscheck__(dict):
                try:
                    dict_args: tuple = tp.__args__
                except AttributeError:
                    dict_args: tuple = ()
                log(f'dict_args: {dict_args}', logging.DEBUG)
                if isinstance(new.get(setting), dict):
                    log(f'Updating {setting}: {new.get(setting)}',logging.INFO)
                    for k, v in new.get(setting).items():
                        if len(dict_args) > 0:
                            k = dict_args[0](k)
                            if len(dict_args) > 1:
                                if is_dataclass(dict_args[1]):
                                    if isinstance(v, dict):
                                        v = dict_args[1].from_dict(v)
                                    else:
                                        log_update_error(setting, v)
                                else:
                                    v = dict_args[1](v)
                        self.__dict__[setting][k] = v
            elif is_dataclass(tp):
                if isinstance(new.get(setting), dict):
                    log(f'Updating {setting}...', logging.INFO)
                    self.__dict__[setting].update(new.get(setting))
                else:
                    log_update_error(setting, new.get(setting))
            else:
                if isinstance(new.get(setting), tp):
                    log(f'Updating {setting}: {new.get(setting)}', logging.INFO)
                    self.__dict__[setting] = new.get(setting)
                else:
                    log_update_error(setting, new.get(setting))


@dataclass
class GlobalSettings(Settings):

    @dataclass
    class CustomModule(Settings):
        cmd_presets: dict[str, Settings.CmdPreset] = field(default_factory=dict)

    @dataclass
    class AppsModule(CustomModule):
        pass

    @dataclass
    class FilesModule(CustomModule):
        pass

    @dataclass
    class SystemCmds(Settings):
        """
        Preconfigured to use POSIX-compatible GNU/Linux shell commands.
        """
        superuser: str
        cp: str
        mv: str
        mkdir: str
        validate_path: str
        validate_dir: str

    noconfirm: bool
    system_cmds: SystemCmds
    custom_module: CustomModule
    apps_module: AppsModule
    files_module: FilesModule

    def __str__(self):
        return str(self.__dict__)


global_settings = GlobalSettings(
    noconfirm=False,
    custom_module=GlobalSettings.CustomModule(cmd_presets={}),
    apps_module=GlobalSettings.AppsModule(
        cmd_presets={
            'flatpak': Settings.CmdPreset(
                install_cmd='flatpak install -y --noninteractive $@'
            ),
            'apt': Settings.CmdPreset(
                install_cmd='sudo apt --assume-yes install $@'
            ),
            'pacman': Settings.CmdPreset(
                install_cmd='sudo pacman -S --noconfirm --needed $@'
            ),
            'yay': Settings.CmdPreset(
                install_cmd='yay -S --noconfirm --needed $@'
            )
        }
    ),
    files_module=GlobalSettings.FilesModule(
        cmd_presets={
            'copy': Settings.CmdPreset(

            ),
            'hardlink': Settings.CmdPreset(

            ),
            'tar_copy': Settings.CmdPreset(
                install_cmd='tar -xPf "$1.tar"',
                backup_cmd='tar -cPf "$1.tar" "${@:2}"'
            ),
            'compress': Settings.CmdPreset(
                install_cmd='tar -xPf "$1.tar.xz"',
                backup_cmd='tar -cJPf "$1.tar.xz" "${@:2}"'
            ),
            'encrypt': Settings.CmdPreset(
                install_cmd='openssl enc -d -aes-256-cbc -md sha512 -pbkdf2 -salt -in "$1.tar.xz.enc" | tar -xPf -',
                backup_cmd='tar -cJPf - "${@:2}" | '
                            'openssl enc -e -aes-256-cbc -md sha512 -pbkdf2 -salt -out "$1.tar.xz.enc"'
            )
        }
    ),
    system_cmds=GlobalSettings.SystemCmds(
        superuser='sudo',
        cp='cp -at "$1" "${@:2}"',
        mv='mv -t "$1" "${@:2}"',
        mkdir='mkdir -p "$1"',
        validate_path='[ -e "$1" ]',
        validate_dir='[ -d "$1" ]'
    )
)
