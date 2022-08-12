import abc
import dataclasses
import logging
import typing
from pathlib import Path

from .logger import log

_T = typing.TypeVar('_T')


@dataclasses.dataclass
class Setting(abc.ABC):
    """
    Abstract wrapper class for a setting value. Describes inheritance and config value conversion functions.
    """

    @abc.abstractmethod
    def fold(self, path_part: Path, setting: typing.Optional['Setting']) -> 'Setting':
        """
        Folds the current Setting onto a path part and an associated setting (which may or may not exist)
        and returns another instance of Setting.
        """
        ...

    @classmethod
    @abc.abstractmethod
    def parse(cls, value) -> 'Setting':
        """Parses the given arbitrary value and returns a Setting instance from it."""
        ...

    @staticmethod
    def assert_tp(val, tp: typing.Type[_T], err_msg: str) -> _T:
        """
        Asserts that a value is of some type and return it.

        Otherwise, raises a TypeError and logs an error message.
        """
        if isinstance(val, tp):
            return val
        else:
            log(logging.ERROR, err_msg)
            raise TypeError


class _Settings:
    _settings: dict[str, Setting]
    _setting_types: dict[str, typing.Type[Setting]]


@dataclasses.dataclass
class Settings(abc.ABC, _Settings):
    """Base dataclasses.dataclass for storing Setting instances. All fields should be a subtype of Setting."""

    def __init__(self, **kwargs):
        ...

    def __init_subclass__(cls, **kwargs):
        """Enforce that all fields are some subtype of Setting and yield field name -> type dict elements."""

        def parse_fields():
            for field in dataclasses.fields(cls):
                if not (offender := field.type) is Setting:
                    log(logging.CRITICAL, f'{offender} Settings field is not a Setting! '
                                          f'All fields of a Settings subclass must be a Setting subtype.')
                    raise NotImplementedError
                yield field.name, field.type
        cls._setting_types = dict(parse_fields())

    @classmethod
    def parse(cls, config) -> dict[str, typing.Optional[Setting]]:
        """
        Parses an arbitrary config and returns a dictionary of Optional[Setting] instances from it corresponding
        to the class, some of which may or may not be None.
        """
        config: dict = Setting.assert_tp(config, dict, err_msg='Settings config is not a dictionary - unable to parse.')
        return {key: (setting_type.parse(config[key]) if key in config else None)
                for key, setting_type in cls._setting_types.items()}

    def __post_init__(self):
        self._settings = {field.name: getattr(self, field.name) for field in dataclasses.fields(self)}

    def fold(self, path_part: Path, **settings: typing.Optional[Setting]) -> 'Settings':
        """
        Folds the Settings instance onto a path part and its associated dictionary of settings
        and returns another instance of Settings.
        """
        return self.__class__(**{key: setting.fold(path_part, settings.get(key))
                                 for key, setting in self._settings.items()})


_SettingsT = typing.TypeVar('_SettingsT', bound=Settings)


@dataclasses.dataclass
class Repository(typing.Generic[_SettingsT]):
    """Dataclass that stores a repository's path and its settings."""
    repo_path: Path
    settings: _SettingsT


class Store(typing.Generic[_SettingsT]):
    """
    Stores a mapping of path parts to repositories and their settings.
    """

    def __init__(self, store_path: Path, config: dict, root_settings: _SettingsT):

        self.store: dict[Path, dict | Repository[_SettingsT]] = {}

        def parse_store(full_path: Path, subconfig: dict, config_settings: _SettingsT, store_subconfig: dict):
            for child_key, child_config in subconfig.items():

                child_key: str = Setting.assert_tp(child_key, str, err_msg=f'Key value {child_key} should be a string!')
                child_path_part = Path(child_key)

                if '/' == child_path_part.parts[0]:
                    log(logging.ERROR, f'The key {child_key} is invalid! Keys cannot start with "/".')
                if '..' in child_path_part.parts:
                    log(logging.ERROR, f'The key {child_key} is invalid! ".." is not a valid key.')
                    raise KeyError

                is_dir = child_key.endswith('/')

                # Allow conversion to {} in the case that value is None
                child_settings = child_config.pop('.', {}) if is_dir else child_config
                child_settings = config_settings.fold(child_path_part, **Setting.assert_tp(
                    child_settings if child_settings else {}, dict,
                    err_msg=f'Settings for "{full_path / child_key}" in config is not a dictionary! Cannot parse...'))

                if is_dir:
                    parse_store(full_path / child_path_part, child_config, child_settings,
                                store_subconfig.setdefault(child_path_part, {}))
                else:
                    if child_path_part in store_subconfig:
                        log(logging.ERROR, f'Discovered a duplicate repository entry at {full_path / child_path_part}!')
                        raise KeyError
                    store_subconfig[child_path_part] = Repository[_SettingsT](full_path, child_settings)

        # Allow conversion to {} in the case that value is None
        root_overrides = config.pop('.', {})
        root_overrides = root_settings.parse(Setting.assert_tp(
            root_overrides if root_overrides else {}, dict,
            err_msg=f'Root settings in config is not a dictionary! Cannot parse...')
        )
        root_settings = dataclasses.replace(root_settings, **root_overrides)

        parse_store(store_path, config, root_settings, self.store)
        log(logging.DEBUG, f'STORE: {self.store}')

    def get(self, path: Path) -> typing.Generator[Repository[_SettingsT], None, None]:
        """Walks all paths within the given path and generates any instances of repository Settings that are found."""

        def subconfig(config: dict, key: str, *keys: str):
            if not keys:
                return config.get(key)
            return subconfig(config.get(key, {}), keys[0], *keys[1:])

        def walk(config: dict):
            for child in config.values():
                if isinstance(child, Repository):
                    yield child
                elif isinstance(child, dict):
                    walk(child)

        start_config = subconfig(self.store, *path.parts)
        return walk(start_config)
