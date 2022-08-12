from .commands import *
from .lib.command import *
from .lib.logger import *
from .lib.store import *


__version__ = 'dev'

commands: list[typing.Type[Command]] = [Test]


def define_args():
    parser = argparse.ArgumentParser(
        description='Run <command> --help to see more information about an command.',
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False,
        usage='%(prog)s <command> [...]')
    parser.add_argument('--help', '-h', action='help', help=argparse.SUPPRESS)
    parser.add_argument('--version', action='version', help=argparse.SUPPRESS,
                        version=f'v{__version__}\n'
                                f'Copyright (C) 2022 Aurtzy\n'
                                f'License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>\n'
                                f'This is free software: you are free to change and redistribute it.\n'
                                f'There is NO WARRANTY, to the extent permitted by law.')
    parser.add_argument('--debug', action='store_true', help=argparse.SUPPRESS)

    cmd_subparsers = parser.add_subparsers(title='commands', required=True, dest='cmd')

    for command in commands:
        command.define_args(cmd_subparsers)  # todo: placeholder, but may be sufficient

    return parser


def parse_args(parser: argparse.ArgumentParser, namespace: argparse.Namespace = None) -> argparse.Namespace:
    if len(sys.argv) == 1:
        parser.print_help()
        exit(0)
    return parser.parse_args(namespace=namespace)


def init_log_handlers(args: argparse.Namespace):
    """Initialize logger levels and handlers."""
    logger.setLevel(logging.DEBUG)

    # Log file handler
    # if args.logfile:
    #     file_handler = logging.FileHandler(args.logfile)
    #     file_handler.setLevel(logging.DEBUG)
    #     file_handler.setFormatter(logging.Formatter('[%(levelname)s]: %(message)s'))
    #     logger.addHandler(file_handler)

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

    args = argparse.Namespace()
    parse_args(define_args(), namespace=args)

    # Initialize and parse args. Common options should be processed here, while command-specific
    # stuff can be handled in respective command classes which are called afterwards.
    init_log_handlers(args)
    print(args.__dict__)
    print(dataclasses.fields(Test))
    # to match more commands, supposed to be something like `match args.cmd: 'test': ...  'other_cmd': ...`
    Test.from_args(args).run()
