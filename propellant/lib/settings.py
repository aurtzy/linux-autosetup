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

    _category: tuple = ()
    _keys: tuple = ()

    hooks: list[typing.Type["Settings"]] = []

    @staticmethod
    def assert_tp(settings: dict, key, tp, default=None):
        """
        Asserts that item is of type tp.

        Raises a TypeError if a type does not match.
        """
        def raise_error():
            log(f'Unexpected type {type(value)}: {key} did not match the type {tp}.', logging.ERROR)
            raise TypeError
        value = settings.get(key, default)
        if typing.get_origin(tp) is typing.Union:
            if not isinstance(value, typing.get_args(tp)):
                raise_error()
        elif typing.get_origin(tp) is None:
            if not isinstance(value, tp):
                raise_error()
        else:
            raise NotImplementedError(f'Unexpected type {tp} given - could not interpret.')
        return value

    def __init_subclass__(cls, keys: tuple[str] = (), local_keys: bool = False, **kwargs):
        """
        Assigns keys to the subclass of Settings
        and adds a hook to the list of hooks in Settings.

        If local_keys is True, only keys from the parent class will be inherited. All keys for
        this class will be local.
        """
        super().__init_subclass__(**kwargs)
        for hook in cls.hooks:
            if keys == hook._keys[0:len(keys)]:
                log(f'{hook.__name__} has an overlap with existing keys {keys}! Is this intentional?', logging.DEBUG)
                break
        if local_keys:
            cls._keys = keys
        else:
            cls._category = cls._category + keys
            cls._keys = ()
        cls.hooks.append(cls)

    @classmethod
    def get_key_config(cls, settings: dict) -> dict:
        """
        Gets the relevant key config from a given dictionary of settings.
        :return: A dict obtained from parsing through _keys levels of settings.
        """
        for key in cls._category + cls._keys:
            settings = settings.get(key, {})
            if not isinstance(settings, dict):
                log(f'Expected a dict while retrieving the key {key} value from given settings.\n'
                    f'{settings}', logging.ERROR)
                raise ValueError
        return settings

    @classmethod
    @abc.abstractmethod
    def init_settings(cls, **key_config):
        """
        Run during the settings initialization period.

        Used for parsing the class's designated settings from a user config - that being
        the argument key_config - in order to perform any necessary preliminary actions.
        """
        pass


def init_settings(new_config: dict):
    """
    Initializes all settings for the subclasses that have hooks in the Settings class.
    """
    for hook in Settings.hooks:
        hook.init_settings(**hook.get_key_config(new_config))
