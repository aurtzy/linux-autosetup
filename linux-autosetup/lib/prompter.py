import logging

from lib.logger import log


def get_input(options: list[list[str]], pre_prompt: str = ''):
    """
    Provides a universal method of getting decently formatted prompts from the user.

    Expects a list of list[str], in which each element contains an option.

    The first index of each element will be considered the message to be attached.
    Any elements of the list[str] after that are assumed as alternative accepted inputs that are associated with
    that option.

    Every option in options is automatically tagged with their respective natural number in the list
    which can also be matched with the user input.

    :returns: The index of the first found option which matches user input.
    """
    if not options:
        log('get_input only expects a non-empty list of options... Exiting.', logging.ERROR)
        exit(1)
    log(f'Attempting to get input from the user with the following:\n'
        f'pre_prompt: {pre_prompt}\n'
        f'options: {options}', logging.DEBUG)

    formatted_prompt = '\n'.join(f'{i} [{"/".join(option[1:])}] {option[0]}' for i, option in enumerate(options))

    while True:
        log('Prompting user.', logging.DEBUG)
        if pre_prompt:
            print(pre_prompt)
        print(formatted_prompt)
        user_in = input('Please choose one of the options above: ')
        for i, option in enumerate(options):
            if user_in in option[1:] or user_in == str(i):
                log(f'Accepting input {user_in} and returning {i}.', logging.DEBUG)
                return i
        log(f'Could not find any option matching input. Try again.', logging.INFO)
