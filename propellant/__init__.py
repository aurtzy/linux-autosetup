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


def get_config_path(config_path: str = None) -> str:
    """
    Gets the config file path to load settings from.

    If the path given is a directory, show all .yaml files in that directory as options to choose.
    An additional option also lets the user manually input a config path.
    """
    log('Getting config path for autosetup...', logging.DEBUG)
    if not config_path:
        # Default to current directory
        config_path = '.'

    # then from here on, config_path is treated the same regardless of whether it was passed.
    # loop/while
    # if config_path is a file
    #  return that
    # else if config_path is a directory
    #  prompt with .yaml files in directory or input manual path
    #  set that to config_path if valid and try again

    # todo: TEMP
    return '../sample-configs/config.yaml'


def get_autosetup_mode(mode: str = None) -> str:
    """Gets the autosetup mode."""
    log('Getting autosetup mode...', logging.DEBUG)
    if not mode:
        match get_option_i([('install', 'Run the autosetup in installer mode'),
                             ('backup', 'Run the autosetup in backup mode')],
                            prompt='Choose an autosetup mode: '):
            case 0: mode = 'install'
            case 1: mode = 'backup'
    elif mode not in {'install', 'backup'}:
        log(f'Could not match "{mode}" with any known autosetup option.', logging.ERROR)
        raise LookupError

    return mode


def get_packs(pack_names: list[str] = None) -> list:
    """Gets the packs to run autosetup on."""
    log('Getting packs for autosetup...', logging.DEBUG)
    if not pack_names:
        # prompt for packs from Pack.packs names
        # write generic, decent looping prompting system similar to bash version's pack prompting
        pass
    else:
        # If packs were passed as arguments, check if all are valid names
        all_valid = True
        for pack_name in pack_names:
            if not Pack.pack_exists(pack_name):
                all_valid = False
        if not all_valid:
            raise LookupError

    return pack_names


def run_autosetup(**kwargs):
    """
    Start autosetup process.

    Prompt for missing arguments as needed. If noconfirm is True with needed but missing arguments,
    an error will be raised.
    """
    # Get config file path to be used
    config_path = Path(get_config_path(kwargs.get('config')))

    # Parse config
    ConfigParser(config_path).start()

    # Get autosetup mode
    mode = (get_autosetup_mode(kwargs.get('mode')))

    # Get packs to do autosetup on
    packs: list = get_packs(kwargs.get('packs'))

    # Run autosetup!
    match mode:
        case 'install':
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
        case 'backup':
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
