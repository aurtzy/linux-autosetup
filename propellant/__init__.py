import argparse
import os

from .lib.logger import *
from .lib.user_input import *
from .lib.system import *
from .lib.configparser import *
from .lib.pack import *

__version__ = '0.0.0-dev'


def parse_args(*args) -> argparse.Namespace:
    """Parse arguments passed to the script or args if args is non-empty."""
    parser = argparse.ArgumentParser(description='Set options for this script to use.',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     add_help=False)

    parser.add_argument('-h', '--help', action='help', help=argparse.SUPPRESS)
    parser.add_argument('--debug', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--version', action='version', help=argparse.SUPPRESS,
                        version=f'v{__version__}\n'
                                f'Copyright (C) 2022 Aurtzy\n'
                                f'License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>\n'
                                f'This is free software: you are free to change and redistribute it.\n'
                                f'There is NO WARRANTY, to the extent permitted by law.')

    autosetup_options = parser.add_argument_group('autosetup options')
    autosetup_options.add_argument('-c', '--config', metavar='CONFIG_PATH', type=str,
                                   help='Configuration file to use')
    autosetup_options.add_argument('-m', '--mode', choices=['install', 'backup'],
                                   help='Autosetup mode to run')
    autosetup_options.add_argument('packs', nargs='*',
                                   help='Packs to use in the autosetup')

    interactive_options = parser.add_argument_group('interactive options')
    interactive_options.add_argument('--noconfirm', action='store_true',
                                     help='Assume default values for prompts.\n'
                                          'Requires all autosetup arguments to be defined')
    return parser.parse_args(*args)


def get_config_path(config_path) -> str:
    """
    Gets the config file path to load settings from.

    Will automatically detect .yaml files in the current directory,
    but users can optionally choose to input a relative/absolute path
    to the config instead.
    """
    return '../sample-configs/config.yaml'


def get_autosetup_mode() -> str:
    """Gets the autosetup mode."""
    mode = get_option_i([('install', 'Run the autosetup in installer mode'),
                         ('backup', 'Run the autosetup in backup mode')],
                        prompt='Choose an autosetup mode: ')
    if mode == 0:
        return 'install'
    elif mode == 1:
        return 'backup'


def get_packs(*args: str) -> list:
    """
    Gets the packs to run autosetup on.

    """
    pass  # todo


def run_autosetup(**kwargs):
    """
    Start autosetup process.

    Prompt for missing arguments as needed. If noconfirm is True with needed but missing arguments,
    an error will be raised.
    """
    # Get config file path to be used
    print(kwargs.get('config'))
    config_path: Path = Path(get_config_path(kwargs.get('config')))

    # Parse config
    ConfigParser(config_path).start()

    # Get autosetup mode
    mode = (kwargs.get('mode') if kwargs.get('mode')
            else get_autosetup_mode())

    # Get packs to do autosetup on
    packs = get_packs(kwargs.get('packs'))

    # If packs were passed as arguments, check if all are valid names
    if kwargs.get('packs'):
        for pack_name in kwargs.get('packs'):
            if not Pack.pack_exists(pack_name):
                packs = None
        if packs is None:
            raise LookupError

    # Run autosetup!
    if mode == 'install':
        for p in packs:
            p.install()
        # Check for bad installs

        all_success = True
        for p in Pack.packs:
            if not p.install_success:
                if all_success:
                    all_success = False
                    log('The following pack(s) failed to install:', logging.ERROR)
                log(p.name, logging.ERROR)
    elif mode == 'backup':
        for p in packs:
            p.backup()

        all_success = True
        for p in Pack.packs:
            if not p.install_success:
                if all_success:
                    all_success = False
                    log('The following pack(s) failed to be backed up:', logging.ERROR)
                log(p.name, logging.ERROR)


def run():
    """Entry point."""
    args = parse_args()

    # Set up logger
    init_stream(args.debug)

    # Set noconfirm
    set_noconfirm(args.noconfirm)

    # Check if script is being run as root
    if os.geteuid() == 0:
        log('Warning: It is not recommended to run this script as root '
                   'unless you know what you\'re doing.', logging.WARNING)

    # autosetup
    run_autosetup(**args.__dict__)
