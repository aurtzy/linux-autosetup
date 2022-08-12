import abc
import argparse
import dataclasses
import logging
import os
import typing

from pathlib import Path
from string import Template

from .lib.logger import log
from .lib.command import Command
from .lib.configparser import ConfigParser
from .lib.store import Setting, Settings, Store


class Source(Setting):
    """
    Path part that will be joined with source path instead of the config key value.
    This does not apply to repository paths.

    Additionally, parse makes use of environment variable expansion.
    """

    value: Path

    _environ = os.environ.copy()

    def fold(self, path_part: Path, setting: typing.Optional['Setting']) -> 'Setting':
        return setting if setting else Source(path_part)

    @classmethod
    def parse(cls, value) -> 'Setting':
        value = cls.assert_tp(value, str, err_msg=f'Setting for src value was not a str: {value}')
        try:
            return Setting(Path(Template(str(value)).substitute(cls._environ)))
        except KeyError as key:
            log(logging.ERROR, f"The following environment variable does not exist: {key}")


class Common(Command, abc.ABC):

    @classmethod
    def run(cls, args: argparse.Namespace):
        pass

    @classmethod
    def define_args(cls, subparsers) -> argparse.ArgumentParser:
        pass


@dataclasses.dataclass
class TestSetting(Setting):

    test: int

    def fold(self, path_part: Path, setting: typing.Optional['Setting']) -> 'Setting':
        if setting is None:
            return TestSetting(0)
        return setting

    @classmethod
    def parse(cls, value) -> 'Setting':
        return TestSetting(cls.assert_tp(value, int, err_msg=f'Test setting is not an int!'))


@dataclasses.dataclass
class TestSettings(Settings):
    test: TestSetting


@dataclasses.dataclass
class Test(Command):

    test: bool

    def run(self):
        store = Store(Path('.'), ConfigParser('./samples/test.yaml').load(), TestSettings(test=TestSetting(1)))
        print(self.test)

    @classmethod
    def define_args(cls, subparsers) -> argparse.ArgumentParser:
        parser = cls._add_subparser(subparsers,
                                    'test',
                                    help='Testing\n'
                                         'command')

        parser.add_argument('--test', action='store_true')
        return parser


class Init(Command):

    def run(self):
        # iteration 1 of psuedocode test:
        # receive whatever options init may have defined
        # parse config
        # store init-specific config stuff for now
        # initialize stowup store with parsed relevant config settings
        # get ALL repos
        # run `borg init` with repositories. things to consider: chdir, root, encryption
        pass

    @classmethod
    def _cmd(cls) -> str:
        pass

    @classmethod
    def define_args(cls, subparsers):
        parser = super().define_args(subparsers)
        ...
        return parser
    