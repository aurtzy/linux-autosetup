import abc
import logging
import typing

from .logger import log


class Settings(abc.ABC):
    """
    This class provides a simple API for implementing user_config-to-script settings.

    Its purpose is to add an initialization period for additional actions to take place when
    translating from the configparser to settings that are to be used during runtime, as some
    data written to config files may have to be checked prematurely for the script to function as desired.

    The Settings class mainly provides the following:
        - A class argument "keys", which is used when creating subclasses to
          designate the location that settings for a particular class will be found in the
          user configuration file.

        - Hooks to this class for initialization that are automatically ordered
          based on the import sequence of Python modules.

        - An abstract method initialize_settings() that is called during the initialization period.

        - Miscellaneous helper methods for parsing settings from the given user config.
    """

    _keys: tuple[str] = ()

    hooks: list[typing.Type["Settings"]] = []

    @staticmethod
    def assert_tp(settings: dict, key, tp, default=None):
        """
        Asserts that item is of type tp.

        Raises a TypeError if a type does not match.
        """
        value = settings.get('key', default)
        if not isinstance(value, tp):
            log(f'Unexpected type {type(value)}: {key} did not match the type {tp}.', logging.ERROR)
            raise TypeError
        return value

    def __init_subclass__(cls, keys: tuple[str] = (), **kwargs):
        """
        Assigns keys to the subclass of Settings
        and adds a hook to the list of hooks in Settings.
        """
        super().__init_subclass__(**kwargs)
        for hook in cls.hooks:
            if keys == hook._keys[0:len(keys)]:
                log(f'{hook.__name__} has an overlap with existing keys {keys}! Is this intentional?', logging.DEBUG)
                break
        cls._keys = cls._keys + keys
        cls.hooks.append(cls)

    @classmethod
    def get_key_config(cls, **settings) -> dict:
        """
        Gets the relevant key config from a given dictionary of settings.
        :return: A dict obtained from parsing through _keys levels of settings.
        """
        for key in cls._keys:
            settings = settings.get(key, {})
            if not isinstance(settings, dict):
                log(f'Expected a dict while retrieving the key {key} value from given settings.\n'
                    f'{settings}', logging.ERROR)
                raise ValueError
        return settings

    @classmethod
    @abc.abstractmethod
    def initialize_settings(cls, **key_config):
        """
        Run during the settings initialization period.

        Used for parsing the class's designated settings from a user config - that being
        the argument key_config - in order to perform any necessary preliminary actions.
        """
        pass


def initialize_settings(**new_config):
    """
    Initializes all settings for the subclasses that have hooks in the Settings class.
    """
    for hook in Settings.hooks:
        hook.initialize_settings(**hook.get_key_config(**new_config))
