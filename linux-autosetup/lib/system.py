import logging
import subprocess
import threading
import time

from lib.logger import log
from lib.prompter import get_input


# Used for commands that may require superuser elevation, such as PathOps.
# By default, uses 'sudo'
su_cmd: str = 'sudo'


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
    # p = Popen(['sudo', '-v'])
    # p.communicate()
    # if p.returncode != 0:
    #   raise PermissionError('sudo could not validate.')

    def sudo_loop_thread():
        i = 0.0
        while True:
            if not threading.main_thread().is_alive():
                log('Exiting sudo_loop_thread.', logging.DEBUG)
                break
            if i >= 5.0:
                log('Revalidating sudo.', logging.DEBUG)
                # Popen(['sudo', '-v']).communicate()
                i = 0.0
            else:
                time.sleep(0.5)
                i += 0.5

    threading.Thread(target=sudo_loop_thread).start()
    log('Started sudo_loop_thread.', logging.DEBUG)


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


class PathOps:
    """
    Provides methods in which to manipulate and interact with files on the system.

    The following commands are configured to work on most GNU/Linux systems, but may be changed to
    work with other systems.

    su_cmd: str
        Superuser command, used to elevate commands to make sure they have necessary permissions to function.
        Uses 'sudo' by default.
    cp_cmd: str
        Copy command, used for copying files to locations.
    mv_cmd: str
        Move command, used for moving files to locations.
    mkdir_cmd: str
        Make directory command, used for creating directories.

    validate_path: str
        Command that checks if a file or directory exists.
        POSIX compliant by default.
    validate_dir: str
        Command that checks if a directory exists.
        POSIX compliant by default.

    Calling these methods will invoke a check for if the path(s) exist, and an error
    is raised if any path does not exist.
    """

    cp_cmd: str = 'cp -at "$1" "${@:2}"'
    mv_cmd: str = 'mv -t "$1" "${@:2}'
    mkdir_cmd: str = 'mkdir -p $1'

    validate_path: str = '[ -e "$1" ]'
    validate_dir: str = '[ -d "$1" ]'

    @classmethod
    def copy(cls, dest: str, *args: str) -> bool:
        """
        Copies files from the given path(s) args to dest.

        :return: True if the copy was successful; False otherwise.
        """
        print(f'TEMP: copy {", ".join(str(path) for path in args)} to {dest}')
        return True

    @classmethod
    def move(cls, dest: str, *args: str) -> bool:
        """
        Moves files from the given path(s) args to dest.

        :return: True if the move was successful; False otherwise.
        """
        print(f'TEMP: move {", ".join(str(path) for path in args)} to {dest}')
        return True

    @classmethod
    def mkdir(cls, path: str) -> bool:
        """
        Creates directory if it doesn't exist at the specified path.

        :return: True if the directory creation was successful or if it already exists; False otherwise.
        """
        print(f'TEMP: Create directory to path {path} if it doesn\'t exist.')
        return True

    @classmethod
    def path_exists(cls, path: str, no_confirm: bool = False) -> bool:
        """
        Checks if the given path exists.

        If no_confirm is true, the method will return false if the path does not exist.
        Otherwise, when no_confirm is false, it prompts the user with various options to attempt to resolve this.

        Implementations should not use the given path if this method returns False.

        :return: True if the path is valid and exists; false otherwise.
        """
        while True:
            log(f'Checking if "{path}" exists...', logging.INFO)
            if run(f'{su_cmd} {cls.validate_path}', [path]) == 0:
                log('Path found.', logging.INFO)
                return True
            elif no_confirm:
                log('Path not found. Ignoring...', logging.INFO)
                return False
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
                        return False
                    case _:
                        log('Aborting.', logging.ERROR)
                        exit(1)

    @classmethod
    def dir_valid(cls, dir_path: str, no_confirm: bool = False) -> bool:
        """
        Validates the given directory path. Unlike path_exists, this method allows the given directory path
        to be created if it is not found.

        If no_confirm is true and the path does not exist, automatically create the directory and return True.
        Otherwise, prompt the user for options to handle the missing directory.

        Implementations should not use the directory given if this method returns False.

        :return: True if the directory path is valid and exists; False otherwise.
        """
        while True:
            log(f'Checking if directory path "{dir_path}" exists...', logging.INFO)
            if run(f'{su_cmd} {cls.validate_dir}', [dir_path]) == 0:
                log(f'Directory path found.', logging.INFO)
                return True
            elif no_confirm:
                log(f'Path is missing - automatically creating directory at "{dir_path}".', logging.INFO)
                PathOps.mkdir(dir_path)
            else:
                log('Path could not be found - Prompting user to handle.', logging.DEBUG)
                i = get_input(
                    [['Try to find it again? If it\'s on another drive, check if it is mounted.', 'T'],
                     ['Create a new directory?', 'C'],
                     ['Ignore this path for the session?', 'I'],
                     ['Abort this script?', 'A']],
                    pre_prompt=f'The directory "{dir_path}" was not found. How do you want to handle this?')
                match i:
                    case 0:
                        log('Attempting to find directory again.', logging.INFO)
                        continue
                    case 1:
                        log(f'Creating new directory.', logging.INFO)
                        PathOps.mkdir(dir_path)
                        return True
                    case 2:
                        log(f'Ignoring this path for the session.', logging.INFO)
                        return False
                    case _:
                        log('Aborting.', logging.INFO)
                        exit(1)
