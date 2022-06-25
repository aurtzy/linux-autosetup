import argparse
import platform
import sys

from .lib.configparser import *
from .lib.logger import *
from .lib.module import *


__version__ = '4.0.0-dev'

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
    universal.add_argument('--logfile', action='store', metavar='<path>',
                           help='Enable logging to a specified filepath')

    # Modules
    modules = argparse.ArgumentParser(add_help=False)
    modules.add_argument('--dir', action='store', default='.',
                         help='Directory to search for scriptman config', metavar='<path>')
    modules.add_argument('modules', action='store', nargs='*',
                         help='List modules for operation\n'
                              'Trailing slashes are ignored')

    # Info options
    info_opts = argparse.ArgumentParser(parents=[modules], add_help=False)

    # Runtype options
    runtype_opts = argparse.ArgumentParser(parents=[modules], add_help=False)
    build_config_flags(runtype_opts, 'deps', True,
                       flag_help='Include running module dependencies\n'
                                 'Enabled by default',
                       noflag_help='Only run modules that are specified')
    build_config_flags(runtype_opts, 'sudoloop', (True if platform.system() in ['Linux', 'Darwin'] else False),
                       flag_help='Loop sudo in the background to prevent authentication timeout\n'
                                 'Enabled by default on Linux systems',
                       noflag_help='Disable looping sudo in the background')
    build_config_flags(runtype_opts, 'confirm', True,
                       flag_help='Prompt the user for confirmations\n'
                                 'Enabled by default',
                       noflag_help='Skip confirmation prompts')
    build_config_flags(runtype_opts, 'strict', True,
                       flag_help='Skips prompts to handle errors when noconfirm is enabled\n'
                                 'This and nostrict flags do not have any effect when confirm is enabled\n'
                                 'Enabled by default',
                       noflag_help='When noconfirm is enabled, ignore errors where possible')

    # Operations
    operations = parser.add_subparsers(title='operations', required=True, dest='op')
    build_op = (lambda opcmd, parents, ophelp: operations.add_parser(
        opcmd, formatter_class=argparse.RawTextHelpFormatter, add_help=False,
        parents=[universal, *parents], usage=f'{prog} {opcmd} [options] [module(s)]', help=ophelp
    ))
    build_op('info', [info_opts], 'Query for information on modules')
    for runtype in Module.RUNTYPES:
        build_op(runtype, [runtype_opts], f'Executes {runtype} scripts for modules')


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
        if getattr(args, flag, None) is UNASSIGNED:
            setattr(args, flag, default)


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


def do_operation():
    if args.op == 'info':
        coll = ModuleCollection()
        for module in map(coll.get, args.modules):
            print(module.info(verbose=True), '\n')
    elif args.op in Module.RUNTYPES:
        runner = ModuleRunner(ModuleCollection(), args.op, *map(ModuleID, args.modules),
                              confirm=args.confirm, withdeps=args.deps)
        runner.run()
    else:
        raise NotImplementedError(f'Unrecognized operation {args.op}.')


def run_module():
    # Fixes https://github.com/indygreg/PyOxidizer/issues/307
    if getattr(sys, 'oxidized', False):
        sys.argv[0] = sys.executable

    define_args()
    if len(sys.argv) == 1:
        parser.print_help()
        exit(0)
    parser.parse_args(namespace=args)

    os.chdir(args.dir)

    initialize_logger()

    try:
        parse_config(ConfigParser.load(ConfigParser.MAIN_CFG))
    except FileNotFoundError:
        log(logging.ERROR, 'Main config is missing!')
        raise

    post_parse_args()
    log(logging.DEBUG, f'Script settings: {args}')

    do_operation()
