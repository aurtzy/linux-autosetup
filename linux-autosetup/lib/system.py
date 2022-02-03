import logging
import os.path
import subprocess
import threading
import time
from os import PathLike

from lib.settings import global_settings
from lib.logger import log
from lib.prompter import get_input


def run(cmd: str, args: list[str] = None) -> int:
    """
    Run the given command(s) through the shell along with any arguments.

    :param cmd:     String of command(s) to run.
    :param args:    Optional arguments to supply to the shell.
    :return:        Return-code of running command(s).
    """
    log(f'Running command(s):\n{cmd}', logging.DEBUG)
    args = args or []
    log(f'The following shell arguments will be passed:\n{args}', logging.DEBUG)
    try:
        pass
        # TODO: temporary; remove when appropriate
        # subprocess.run([cmd, ''] + args, check=True, text=True, shell=True)
    except subprocess.CalledProcessError as error:
        log(f'Encountered an error running shell commands:\n'
            f'{error}\n', logging.ERROR)
        return error.returncode
    return 0


def sudo_loop():
    """
    Mitigates potential issues when running prolonged commands that may cause the sudo
    timeout to expire, resulting in sudo prompts during the script.

    Should only be called at most once within script.

    Once called, loop sudo -v every 5 seconds until parent process (the caller) ends.
    Sudo may prompt for a password at call start.

    Raises PermissionError if the first sudo call is not successful.
    """
    log('Starting sudo loop.', logging.INFO)

    # TODO: FIX SUDO COMMENTS WHEN NOT A NUISANCE
    # if run('sudo -v') != 0:
    #     raise PermissionError('sudo could not validate.')

    def sudo_loop_thread():
        i = 0.0
        while True:
            if not threading.main_thread().is_alive():
                log('Exiting sudo_loop_thread.', logging.DEBUG)
                break
            if i >= 5.0:
                log('Revalidating sudo.', logging.DEBUG)
                # run('sudo -v')
                i = 0.0
            else:
                time.sleep(0.5)
                i += 0.5

    threading.Thread(target=sudo_loop_thread).start()
    log('Started sudo_loop_thread.', logging.DEBUG)


class Path(PathLike):
    """
    Provides methods in which to manipulate and interact with files on the system.

    Calling these methods will invoke a check for if the path(s) exist, and an error
    is raised if any path does not exist.
    """

    def __init__(self, path: str):
        self.path = os.path.expandvars(path)

    @staticmethod
    def copy(dest: str, *args: str) -> bool:
        """
        Copies files from the given path(s) args to dest.

        :return: True if the copy was successful; False otherwise.
        """
        print(f'TEMP: copy {", ".join(str(path) for path in args)} to {dest}')
        return True

    @staticmethod
    def move(dest: str, *args: str) -> bool:
        """
        Moves files from the given path(s) args to dest.

        :return: True if the move was successful; False otherwise.
        """
        print(f'TEMP: move {", ".join(str(path) for path in args)} to {dest}')
        return True

    @staticmethod
    def mkdir(path: str) -> bool:
        """
        Creates directory if it doesn't exist at the specified path.

        :return: True if the directory creation was successful or if it already exists; False otherwise.
        """
        print(f'TEMP: Create directory to path {path} if it doesn\'t exist.')
        return True

    @classmethod
    def existing_path(cls, path: str):
        """
        Checks if the given path exists, returning a Path object if it does.

        If no_confirm is true, the method will automatically return None if the path does not already exist;
        otherwise, when no_confirm is false, it prompts the user with various options to attempt to resolve this.

        :return: A Path object with path passed as an argument if path exists; None otherwise.
        """
        while True:
            log(f'Checking if "{path}" exists...', logging.INFO)
            if run(f'{global_settings.system_cmds.superuser} '
                   f'{global_settings.system_cmds.validate_path}', [path]) == 0:
                log('Path found.', logging.INFO)
                return cls(path)
            elif global_settings.options.noconfirm:
                log('Path not found. Ignoring...', logging.INFO)
                return None
            else:
                log('Path not found. Prompting user to handle...', logging.DEBUG)
                i = get_input([
                    ['Try searching for it again?', 'T'],
                    ['Ignore this path for the session?', 'I'],
                    ['Abort this script?', 'A']
                ], f'The path "{path}" could not be found. How do you want to handle this?')
                match i:
                    case 0:
                        log('Trying again to find path...', logging.INFO)
                        continue
                    case 1:
                        log('Ignoring path.', logging.INFO)
                        return None
                    case _:
                        log('Aborting.', logging.ERROR)
                        exit(1)

    @classmethod
    def valid_dir(cls, path: str):
        """
        Validates the given directory path. Unlike path_exists, this method allows the given directory path
        to be created if it is not found.

        If no_confirm is true and the path does not exist, automatically create the directory and return its
        respective Path object.
        Otherwise, prompt the user for options to handle the missing directory.

        :return: A Path object with path pass as an argument if the path is valid; None otherwise.
        """
        while True:
            log(f'Checking if directory path "{path}" exists...', logging.INFO)
            if run(f'{global_settings.system_cmds.superuser} '
                   f'{global_settings.system_cmds.validate_dir}', [path]) == 0:
                log(f'Directory path found.', logging.INFO)
                return cls(path)
            elif global_settings.options.noconfirm:
                log(f'Path is missing - automatically creating directory at "{path}".', logging.INFO)
                cls.mkdir(path)
            else:
                log('Path could not be found - Prompting user to handle.', logging.DEBUG)
                i = get_input(
                    [['Try to find it again? If it\'s on another drive, check if it is mounted.', 'T'],
                     ['Create a new directory?', 'C'],
                     ['Ignore this path for the session?', 'I'],
                     ['Abort this script?', 'A']],
                    pre_prompt=f'The directory "{path}" was not found. How do you want to handle this?')
                match i:
                    case 0:
                        log('Attempting to find directory again.', logging.INFO)
                        continue
                    case 1:
                        log(f'Creating new directory.', logging.INFO)
                        cls.mkdir(path)
                        return cls(path)
                    case 2:
                        log(f'Ignoring this path for the session.', logging.INFO)
                        return None
                    case _:
                        log('Aborting.', logging.INFO)
                        exit(1)

    def __fspath__(self) -> str:
        return self.path

    def __str__(self) -> str:
        return self.path
