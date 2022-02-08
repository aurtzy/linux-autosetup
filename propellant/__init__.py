import argparse
import logging

from .lib import logger, user_input, system, configparser

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
    autosetup_options.add_argument('-p', '--pack', nargs='+',
                                   help='Packs to use in the autosetup')

    interactive_options = parser.add_argument_group('interactive options')
    interactive_options.add_argument('--noconfirm', action='store_true',
                                     help='Assume default values for prompts.\n'
                                          'Requires all autosetup arguments to be defined')
    return parser.parse_args(*args)


def run_autosetup(**kwargs):
    """
    Start autosetup process.

    Prompt for missing arguments as needed. If noconfirm is True with needed but missing arguments,
    an error will be raised.
    """
    # Set path of config to be used
    config_path = system.Path('../sample-configs/config.yaml')

    # Parse config
    configparser.ConfigParser(config_path).start()


def run():
    """Entry point."""
    args = parse_args()

    # set up logger
    logger.init_stream(args.debug)
    if args.debug:
        logger.log('Enabled debug stream log.', logging.INFO)

    # noconfirm
    user_input.noconfirm = args.noconfirm
    if args.noconfirm:
        logger.log('Enabled noconfirm.', logging.DEBUG)

    # autosetup
    run_autosetup(**args.__dict__)
