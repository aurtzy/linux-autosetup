import logging
import os.path
import subprocess
import threading
import time
from os import PathLike

from .settings import global_settings
from .logger import log
from .user_input import get_option_i


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

    os.environ.update({'DOLLARSIGN': '$'})

    def __init__(self, path: str):
        self.path = path

    @staticmethod
    def copy(dest: str, *args: str) -> bool:
        """
        Copies files from the given path(s) args to dest.

        :return: True if the copy was successful; False otherwise.
        """
        success = run(global_settings.system_cmds.cp, [dest] + list(args))
        return bool(success)

    @staticmethod
    def move(dest: str, *args: str) -> bool:
        """
        Moves files from the given path(s) args to dest.

        :return: True if the move was successful; False otherwise.
        """
        success = run(global_settings.system_cmds.mv, [dest] + list(args))
        return bool(success)

    @staticmethod
    def mkdir(path: str) -> bool:
        """
        Creates directory if it doesn't exist at the specified path.

        :return: True if the directory creation was successful or if it already exists; False otherwise.
        """
        success = run(global_settings.system_cmds.mkdir, [path])
        return bool(success)

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
        path = os.path.expandvars(path)
        while True:
            log(f'Checking if directory path "{path}" exists...', logging.INFO)
            if run(f'{global_settings.system_cmds.superuser} '
                   f'{global_settings.system_cmds.check_dir}', [path]) == 0:
                log(f'Directory path found.', logging.INFO)
                return cls(path)
            else:
                log('Path could not be found.', logging.WARNING)
                i = get_option_i([('Attempt to find the directory again',),
                                  ('Create a new directory',),
                                  ('Ignore this path for the session',),
                                  ('Abort this script',)],
                                 prompt=f'The directory "{path} could not be found.\n'
                                        f'Please choose how this should be handled')
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
