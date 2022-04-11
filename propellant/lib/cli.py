import logging
import re

from .logger import log
from .. import Settings


class CLI(Settings):
    """
    Settings:
        noconfirm: bool
            Indicates whether the script is allowed to prompt the user.

            User config will be ignored if noconfirm is already set to True.
    """

    noconfirm: bool = False

    @classmethod
    def initialize_settings(cls, **key_config):

        # noconfirm
        if not cls.noconfirm:
            cls.noconfirm = cls.assert_tp(key_config.get('noconfirm'), bool)


def get_input(prompt: str = ': ') -> str:
    if CLI.noconfirm:
        log('Cannot get input: noconfirm is True.', logging.ERROR)
        raise NotImplementedError
    return input(prompt)


def get_option_i(*options: tuple, prompt: str = ': ', default: int = None) -> int:
    """
    Provides a universal method of getting decently formatted prompts from the user.

    Expects tuple arguments as options. Each tuple is an option, with the last element of each tuple being
    the option description. All elements of the tuple are used as match cases with user input.

    :returns: The list index of matched option from user input. If noconfirm is True, return default if
              it is not None; otherwise, an error is raised.
    """
    log(f'Getting custom option with settings:\n'
        f'options: {options}\n'
        f'prompt: "{prompt}"\n'
        f'default: {default}', logging.DEBUG)
    if not options:
        log('get_option_i() expects at least option argument.', logging.ERROR)
        raise NotImplementedError
    elif len(options) == 1:
        log(f'Defaulting to {options[0]} due to being the only option.', logging.DEBUG)
        return 0

    if CLI.noconfirm:
        if default is None:
            log('This option does not have a default value.', logging.ERROR)
            raise NotImplementedError
        log(f'Automatically choosing default option {default}.', logging.DEBUG)
        return default

    formatted = '\n'.join([': '.join(
        [str(i), *(str(opt) for opt in option)]) for i, option in enumerate(options)]) + f'\n{prompt}'

    while True:
        log('Prompting user.', logging.DEBUG)
        user_in = get_input(formatted)
        for i, option in enumerate(options):
            if user_in == str(i) or re.match(
                    f'^({"|".join(str(matcher).lower() for matcher in option)}).*', user_in.lower()):
                log(f'Matched:\n{option}', logging.DEBUG)
                return i
