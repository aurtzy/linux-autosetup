from dataclasses import dataclass
from os import PathLike


@dataclass
class BaseSettings:
    """Base settings class. Meant to be used for recognizing whether a class is a settings-related class."""
    pass

    # TODO: move EVERYTHING to configparser
    # @staticmethod
    # def log_update_error(attr, new):
    #     """Logs update error for the given attr and new setting which will be ignored."""
    #     log(f'Encountered error trying to set {attr} with {new}; ignoring this setting.', logging.ERROR)

    # def update(self, new: dict):
    #     log(f'Updating {self.__class__.__name__} with:\n'
    #         f'{new}', logging.DEBUG)
    #
    #     def log_update_error(s, ignored):
    #         log(f'Encountered an unexpected value for {s}:\n'
    #             f'Ignoring setting {ignored}', logging.ERROR)
    #     for setting, tp in self.__annotations__.items():
    #         if new.get(setting) is None:
    #             continue
    #
    #         if tp.__subclasscheck__(dict):
    #             try:
    #                 dict_args: tuple = tp.__args__
    #             except AttributeError:
    #                 dict_args: tuple = ()
    #             log(f'dict_args: {dict_args}', logging.DEBUG)
    #             if isinstance(new.get(setting), dict):
    #                 log(f'Updating {setting}: {new.get(setting)}',logging.INFO)
    #                 for k, v in new.get(setting).items():
    #                     if len(dict_args) > 0:
    #                         k = dict_args[0](k)
    #                         if len(dict_args) > 1:
    #                             if is_dataclass(dict_args[1]):
    #                                 if isinstance(v, dict):
    #                                     v = dict_args[1].from_dict(v)
    #                                 else:
    #                                     log_update_error(setting, v)
    #                             else:
    #                                 v = dict_args[1](v)
    #                     self.__dict__[setting][k] = v
    #         elif is_dataclass(tp):
    #             if isinstance(new.get(setting), dict):
    #                 log(f'Updating {setting}...', logging.INFO)
    #                 self.__dict__[setting].update(new.get(setting))
    #             else:
    #                 log_update_error(setting, new.get(setting))
    #         else:
    #             if isinstance(new.get(setting), tp):
    #                 log(f'Updating {setting}: {new.get(setting)}', logging.INFO)
    #                 self.__dict__[setting] = new.get(setting)
    #             else:
    #                 log_update_error(setting, new.get(setting))


@dataclass
class GlobalSettings(BaseSettings):
    """
    Global settings.

    noconfirm:
        Indicates whether user should be prompted for input during the script.
    system_cmds:
        See SystemCmds docs.
    custom_module:
        See CustomModule docs.
    apps_module:
        See AppsModule docs.
    files_module:
        See FilesModule docs.
    """

    @dataclass
    class CmdPreset(BaseSettings):
        """
        A preset of shell commands.

        install_cmd:
            Meant to be run during pack installs.
        backup_cmd:
            Meant to be run during pack backups.
        """
        install_cmd: str = ''
        backup_cmd: str = ''

    @dataclass
    class SystemCmds(BaseSettings):
        """
        Miscellaneous shell commands used for interacting with the system.

        superuser:
            Used for elevating commands when appropriate (e.g. sudo).
        cp:
            Used to copy files from one path to another.
            Expects: $1 = target directory; ${@:2} = files to move to target directory
        mv:
            Used to move files from one path to another.
            Expects: $1 = target directory; ${@:2} = files to move to target directory
        mkdir:
            Used to create directories at specified paths.
            Expects: $1 = Path of directory to be made.
        validate_path:
            Used to confirm if a path exists to some file/directory.
        validate_dir:
            Used to confirm if a path exists to some directory.
        """
        superuser: str
        cp: str
        mv: str
        mkdir: str
        validate_path: str
        validate_dir: str

    @dataclass
    class CustomModule(BaseSettings):
        """
        Designated settings for the custom module.

        cmd_presets:
            Dictionary of keys -> CmdPreset objects.
        """
        cmd_presets: dict[str, 'GlobalSettings.CmdPreset']

    @dataclass
    class AppsModule(CustomModule):
        """
        Designated settings for the apps module.
        """
        pass

    @dataclass
    class FilesModule(CustomModule):
        """
        Designated settings for the files module.

        backup_paths:

        """
        backup_paths: dict[str, PathLike]
        dump_dirs: dict[str, PathLike]
        tmp_dirs: dict[str, PathLike]

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
            'flatpak': GlobalSettings.CmdPreset(install_cmd='flatpak install -y --noninteractive $@'),
            'apt': GlobalSettings.CmdPreset(install_cmd='sudo apt --assume-yes install $@'),
            'pacman': GlobalSettings.CmdPreset(install_cmd='sudo pacman -S --noconfirm --needed $@'),
            'yay': GlobalSettings.CmdPreset(install_cmd='yay -S --noconfirm --needed $@')
        }
    ),
    files_module=GlobalSettings.FilesModule(
        cmd_presets={
            'copy': GlobalSettings.CmdPreset(

            ),
            'hardlink': GlobalSettings.CmdPreset(

            ),
            'tar_copy': GlobalSettings.CmdPreset(
                install_cmd='tar -xPf "$1.tar"',
                backup_cmd='tar -cPf "$1.tar" "${@:2}"'
            ),
            'compress': GlobalSettings.CmdPreset(
                install_cmd='tar -xPf "$1.tar.xz"',
                backup_cmd='tar -cJPf "$1.tar.xz" "${@:2}"'
            ),
            'encrypt': GlobalSettings.CmdPreset(
                install_cmd='openssl enc -d -aes-256-cbc -md sha512 -pbkdf2 -salt -in "$1.tar.xz.enc" | tar -xPf -',
                backup_cmd='tar -cJPf - "${@:2}" | '
                            'openssl enc -e -aes-256-cbc -md sha512 -pbkdf2 -salt -out "$1.tar.xz.enc"'
            )
        },
        backup_paths={},
        dump_dirs={},
        tmp_dirs={}
    ),
    # Preconfigured to use GNU/Linux and POSIX-compatible commands.
    system_cmds=GlobalSettings.SystemCmds(
        superuser='sudo',
        cp='cp -at "$1" "${@:2}"',
        mv='mv -t "$1" "${@:2}"',
        mkdir='mkdir -p "$1"',
        validate_path='[ -e "$1" ]',
        validate_dir='[ -d "$1" ]'
    )
)
