import logging
import os
import subprocess
import threading
import time

from lib.logger import log


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
    try:
        subprocess.run([cmd, ''] + args, check=True, text=True, shell=True)
    except subprocess.CalledProcessError as error:
        log(f'Encountered an error running shell commands:\n'
            f'{error}\n', logging.ERROR)
        return error.returncode
    return 0


class Path(os.PathLike):
    """
    Implements os.PathLike with additional functionalities for interacting with the system.

    path: str
        A path to some directory or file on the system which may or may not exist.

    Class variables:
        su_cmd: str
            Superuser command, used to elevate commands to make sure they have necessary permissions to function.
            Uses 'sudo' by default.

        The following variables are configured for use with GNU/Linux systems by default, but may be
        changed to work for other systems instead:

        cp_cmd: str
            Copy command, used for copying files to locations.
        mv_cmd: str
            Move command, used for moving files to locations.
        mkdir_cmd: str
            Make directory command, used for creating directories.
    """

    os.environ['DOLLARSIGN'] = '$'

    su_cmd: str = 'sudo'

    cp_cmd: str = 'cp -at "$1" "${@:2}"'
    mv_cmd: str = 'mv -t "$1" "${@:2}'
    mkdir_cmd: str = 'mkdir -p $1'

    def __init__(self, path):
        self.path = path

    @staticmethod
    def copy(dest: "Path", *args: "Path") -> bool:
        """
        Copies files from the given path(s) args to dest.

        :return: True if the copy was successful; False otherwise.
        """
        print(f'TEMP: copy {", ".join(str(path) for path in args)} to {dest}')
        return True

    @staticmethod
    def move(dest: "Path", *args: "Path") -> bool:
        """
        Moves files from the given path(s) args to dest.

        :return: True if the move was successful; False otherwise.
        """
        print(f'TEMP: move {", ".join(str(path) for path in args)} to {dest}')
        return True

    @staticmethod
    def mkdir(path: "Path") -> bool:
        """
        Creates directory if it doesn't exist at the specified path.

        :return: True if the directory creation was successful or if it already exists; False otherwise.
        """
        print(f'TEMP: Create directory to path {path} if it doesn\'t exist.')
        return True

    @staticmethod
    def expanded_vars(path: str):
        """Returns a Path object with expanded environment variables from the given path arg."""
        return Path(os.path.expandvars(str(path)))

    def subdir(self, rel_path: "Path") -> "Path":
        """Returns a subdirectory of self.path, in which the rel_path argument is appended to self.path."""
        return Path(self.path + '/' + str(rel_path))

    def __fspath__(self):
        return self.path

    def __str__(self):
        return self.path
