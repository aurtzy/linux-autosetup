import argparse
import glob
import logging
import os
import sys

from .lib.logger import *
from .lib.cli import *
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
    parser.add_argument('-C', '--directory', metavar='DIRECTORY', type=str, default=sys.path[0],
                        help='Change the directory. By default, this is set to the script directory path.')

    autosetup_options = parser.add_argument_group('autosetup options')
    autosetup_options.add_argument('-c', '--config', metavar='CONFIG_PATH', type=str,
                                   help='Configuration file to use.')
    autosetup_options.add_argument('-m', '--mode', choices=['install', 'backup'],
                                   help='Autosetup mode to run.')
    autosetup_options.add_argument('PACKS', nargs='*',
                                   help='Packs to use in the autosetup.')

    interactive_options = parser.add_argument_group('interactive options')
    interactive_options.add_argument('--noconfirm', action='store_true',
                                     help='Assume default values for prompts.'
                                          ' Requires all autosetup arguments to be defined.')
    return parser.parse_args(*args)


arguments = parse_args()


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

    config_path = os.path.abspath(config_path)
    if not os.path.isfile(config_path):
        if arguments.noconfirm:
            log(f'Could not find a config file from the specified path: {config_path}', logging.ERROR)
            raise FileNotFoundError
        else:
            print('Please select a config file.')
            while not os.path.exists(config_path):
                log(f'Encountered an error trying to read {config_path}.', logging.ERROR)
                config_path = get_input('Please input a valid directory/file to read config from.\n: ')
            if os.path.isdir(config_path):
                config_paths = glob.glob('*.yaml', root_dir=config_path)
                i = get_option_i(
                    ('manual', 'Manually input a path'),
                    *((path.removesuffix('.yaml'), path) for path in config_paths),
                    prompt='Select a config path option: '
                )
                match i:
                    case 0:
                        print('Entering file system navigator.\n'
                              'An empty input will print all files in the current directory.')
                        while not os.path.isfile(config_path):
                            new_path = get_input(f'[{config_path}] ')
                            if not new_path:
                                for path in glob.iglob('*', root_dir=config_path):
                                    print(path)
                            else:
                                new_path = os.path.join(config_path, new_path)
                                if os.path.isfile(new_path):
                                    config_path = new_path
                                    break
                                elif os.path.exists(new_path):
                                    config_path = os.path.abspath(new_path)
                                else:
                                    log(f'Invalid path: {new_path}', logging.ERROR)
                    case _:
                        config_path = os.path.join(config_path, config_paths[i - 1])

    log(config_path, logging.DEBUG)
    return config_path


def get_autosetup_mode(mode: str = None) -> str:
    """Gets the autosetup mode."""
    log('Getting autosetup mode...', logging.DEBUG)
    if not mode:
        match get_option_i(('install', 'Run the autosetup in installer mode'),
                           ('backup', 'Run the autosetup in backup mode'),
                           prompt='Choose an autosetup mode: '):
            case 0:
                mode = 'install'
            case 1:
                mode = 'backup'
    elif mode not in {'install', 'backup'}:
        log(f'Could not match "{mode}" with any known autosetup option.', logging.ERROR)
        raise LookupError

    return mode


def get_packs(pack_names: list[str] = None) -> list:
    """Gets the packs to run autosetup on."""
    log('Getting packs for autosetup...', logging.DEBUG)
    if not pack_names:
        #todo
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


def run_autosetup():
    """
    Start autosetup process.

    Prompt for missing arguments as needed. If noconfirm is True with needed but missing arguments,
    an error will be raised.
    """
    # Change working directory
    os.chdir(arguments.directory)

    # Get config file path to be used
    config_path = get_config_path(arguments.config)

    # Initialize settings from user config
    initialize_settings(**ConfigParser(config_path).load())

    # Get autosetup mode
    mode = get_autosetup_mode(arguments.mode)

    # Get packs to do autosetup on
    packs: list = get_packs(arguments.packs)

    # todo: Run sudoloop

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

    # Set up logger
    init_stream(arguments.debug)

    # Set noconfirm
    CLI.noconfirm = arguments.noconfirm

    # Check if script is being run as root
    if os.geteuid() == 0:
        log('Warning: It is not recommended to run this script as root '
            'unless you know what you\'re doing.', logging.WARNING)

    # autosetup
    run_autosetup()
