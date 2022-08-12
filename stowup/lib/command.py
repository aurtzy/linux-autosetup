import abc
import argparse
import dataclasses
import pathlib
import sys
import typing


@dataclasses.dataclass
class Command(abc.ABC):
    """Abstract dataclass for implementing commands. Dataclass fields are used to indicate script arguments."""

    prog: typing.ClassVar = pathlib.Path(sys.argv[0]).name

    def __init__(self, **kwargs):
        ...

    @abc.abstractmethod
    def run(self):
        """Main function for doing whatever the command is intended to do."""
        ...

    @classmethod
    @abc.abstractmethod
    def define_args(cls, subparsers) -> argparse.ArgumentParser:
        """
        Defines and returns command-specific ArgumentParser in a given subparsers group.

        These arguments *must* be reflected in the dataclass fields to work without potentially missing arguments
        or unexpected issues if from_args is to be used.

        The _add_subparser method can be used as a starting point for getting an ArgumentParser to work with.
        """
        ...

    @classmethod
    def from_args(cls, args: argparse.Namespace):
        """
        Initializes and returns an instance of this class from the given args.

        Expects args to contain the results of define_args.
        """
        return cls(**{arg.name: args.__dict__.get(arg.name) for arg in dataclasses.fields(cls)})

    @classmethod
    def _add_subparser(cls,
                       subparsers,
                       name: str,
                       help: str = '',
                       formatter_class: argparse.HelpFormatter = argparse.RawTextHelpFormatter,
                       add_help: bool = False,
                       **kwargs) -> argparse.ArgumentParser:
        """
        Creates a subparser with properties defined with the '_cmd_' prefix (prefix is automatically removed in kwargs).
        This return value can be used by subclasses as a base for adding arguments more simply.
        """
        return subparsers.add_parser(name=name,
                                     usage=f'{cls.prog}, {name} [options]',
                                     help=help,
                                     formatter_class=formatter_class,
                                     add_help=add_help,
                                     **kwargs)

