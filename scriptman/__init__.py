import argparse
import os
import platform
import sys

from .lib.configparser import *
from .lib.logger import *


__version__ = '4.0.0-dev'

# Generic runtypes. Can be anything as long as
RUNTYPES = {
    'install': 'Executes install scripts for modules',
    'backup': 'Executes backup scripts for modules',
    'run': 'Executes run scripts for modules'
}
UNASSIGNED = object()  # For indicating unassigned args that require post-parse processing
UNASSIGNED_DEFAULTS = {}  # Dynamically set defaults for potentially unassigned arguments

args = argparse.Namespace()
parser = argparse.ArgumentParser(description='Run <operation> --help to see more information about an operation.',
                                 formatter_class=argparse.RawTextHelpFormatter,
                                 add_help=False, usage='%(prog)s <operation> [...]')


def define_args():
    prog = pathlib.Path(sys.argv[0]).name
    parser.add_argument('--help', '-h', action='help', help=argparse.SUPPRESS)
    parser.add_argument('--version', action='version', help=argparse.SUPPRESS,
                        version=f'v{__version__}\n'
                                f'Copyright (C) 2022 Aurtzy\n'
                                f'License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>\n'
                                f'This is free software: you are free to change and redistribute it.\n'
                                f'There is NO WARRANTY, to the extent permitted by law.')

    def build_config_flags(argparser: argparse.ArgumentParser, flag: str, default: bool,
                           flag_help: str = '', noflag_help: str = ''):
        """Shortcut method for building flags that require post-processing after parsing config."""
        UNASSIGNED_DEFAULTS[flag] = default
        flag_group = argparser.add_mutually_exclusive_group()
        flag_group.add_argument(f'--{flag}', action='store_true', default=UNASSIGNED, dest=flag,
                                help=flag_help)
        flag_group.add_argument(f'--no{flag}', action='store_false', default=UNASSIGNED, dest=flag,
                                help=noflag_help)

    universal = argparse.ArgumentParser(add_help=False)
    universal.add_argument('--help', '-h', action='help', help=argparse.SUPPRESS)
    universal.add_argument('--debug', action='store_true',
                           help='Enable the debug log in the terminal')
    universal.add_argument('--logfile', action='store', type=pathlib.Path, metavar='<path>',
                           help='Enable logging to a specified filepath')

    # Modules
    modules = argparse.ArgumentParser(add_help=False)
    modules.add_argument('--dir', action='store', type=pathlib.Path, default='.',
                         help='Directory to search for scriptman config', metavar='<path>')
    modules.add_argument('modules', action='store', nargs='*',
                         help='List modules for operation\n'
                              'Trailing slashes are ignored')

    # Query options
    query_opts = argparse.ArgumentParser(parents=[modules], add_help=False)

    # Runtype options
    runtype_opts = argparse.ArgumentParser(parents=[modules], add_help=False)
    build_config_flags(runtype_opts, 'deps', True,
                       flag_help='Include running module dependencies',
                       noflag_help='Only run modules that are specified')
    build_config_flags(runtype_opts, 'confirm', True,
                       flag_help='Prompt the user for confirmations',
                       noflag_help='Skip confirmation prompts')
    build_config_flags(runtype_opts, 'sudoloop', (True if platform.system() in ['Linux', 'Darwin'] else False),
                       flag_help='Loop sudo in the background to prevent authentication timeout',
                       noflag_help='Disable looping sudo in the background')

    # Operations
    operations = parser.add_subparsers(title='operations', required=True, dest='op')
    build_op = (lambda opcmd, parents, ophelp: operations.add_parser(
        opcmd, formatter_class=argparse.RawTextHelpFormatter, add_help=False,
        parents=[universal, *parents], usage=f'{prog} {opcmd} [options] [module(s)]', help=ophelp
    ))
    build_op('query', [query_opts], 'Query for information on modules')
    for runtype, helpdesc in RUNTYPES.items():
        build_op(runtype, [runtype_opts], helpdesc)


def parse_config(config: dict):
    """Parse the given config."""
    def check_is(key, typ):
        val = config.get(key, None)
        if isinstance(val, typ):
            return val
        elif val is not None:
            log(logging.WARNING, f'Expected "{key}" config value to be [{typ}], but it was '
                                 f'[{typ.__name__}]')
        return None

    # Parse flags
    if new_defaults := check_is('flags', list):
        new_defaults: list
        for flag in UNASSIGNED_DEFAULTS.keys():
            if flag in new_defaults:
                UNASSIGNED_DEFAULTS[flag] = True
            elif f'no{flag}' in new_defaults:
                UNASSIGNED_DEFAULTS[flag] = False
    # Parse environment variables
    # note: there's no support for substituting environment variables with the reason being it would be redundant
    # for the complexity needed to implement since module scripts will have access to them regardless.
    if env_vars := check_is('env', dict):
        env_vars: dict
        os.environ.update(env_vars)


def post_parse_args():
    """Process arguments that may require assignments after the config is parsed."""
    for flag, default in UNASSIGNED_DEFAULTS.items():
        try:
            if getattr(args, flag) == UNASSIGNED:
                setattr(args, flag, default)
        except AttributeError:
            pass


def initialize_logger():
    """Initialize logger levels and handlers."""
    logger.setLevel(logging.DEBUG)

    # Log file handler
    if args.logfile:
        file_handler = logging.FileHandler(args.logfile)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter('[%(levelname)s]: %(message)s'))
        logger.addHandler(file_handler)

    # Stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG if args.debug else logging.INFO)
    logger.addHandler(stream_handler)
    if args.debug:
        log(logging.DEBUG, 'Enabled debug log!')


def main():
    # Fixes https://github.com/indygreg/PyOxidizer/issues/307
    if getattr(sys, 'oxidized', False):
        sys.argv[0] = sys.executable

    define_args()
    if len(sys.argv) == 1:
        parser.print_help()
        exit(0)
    parser.parse_args(namespace=args)

    initialize_logger()

    parse_config(ConfigParser.load(args.dir.joinpath(ConfigParser.MAIN)))

    post_parse_args()
    log(logging.DEBUG, f'args: {args}')

    # todo initialization of stuff like module registration can happen here

    # todo run operation here
