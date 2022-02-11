import logging
import re

from .logger import log

noconfirm: bool = False


def set_noconfirm(setting: bool):
    global noconfirm
    noconfirm = setting
    if noconfirm:
        log(f'Set noconfirm to {noconfirm}.', logging.DEBUG)


def get_input(prompt: str) -> str:
    return input(prompt)


def get_option_i(options: list[tuple], prompt: str = ': ', default: int = None) -> int:
    """
    Provides a universal method of getting decently formatted prompts from the user.

    Expects argument options to be a list of tuples. Each tuple is an option, with the last element being
    the option description. All elements of the tuple are used as match cases with user input.

    If noconfirm is True, the first option in the list will automatically be chosen, and the method
    will return 0.

    :returns: The list index of matched option from user input.
    """

    if not options:
        log('get_input() only expects a non-empty list of options.', logging.ERROR)
        raise ValueError

    log(f'Getting custom option with settings:\n'
        f'options: {options}\n'
        f'prompt: "{prompt}"\n'
        f'default: {default}', logging.DEBUG)
    if noconfirm:
        if default is None:
            log('This option does not have a default value.', logging.ERROR)
            raise NotImplementedError
        log(f'Automatically choosing default option {default}.', logging.DEBUG)
        return default

    formatted = '\n'.join([': '.join(
        [str(i), *(str(opt) for opt in option)]) for i, option in enumerate(options)]) + f'\n{prompt}'

    while True:
        log('Prompting user.', logging.DEBUG)
        user_in = input(formatted)
        for i, option in enumerate(options):
            if user_in == str(i) or re.match(
                    f'^({"|".join(str(matcher).lower() for matcher in option)}).*', user_in.lower()):
                log(f'Matched:\n{option}', logging.DEBUG)
                return i
