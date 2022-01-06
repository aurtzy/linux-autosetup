import logging
import subprocess
import threading
import time

from lib.logger import log

# Superuser command, used to run things as root if needed.
# Uses 'sudo' by default.
su_cmd: str = 'sudo'

# Copy command, used for copying files to locations.
cp_cmd: str = 'cp -at "$1" "${@:2}"'

# Move command, used for moving files to locations.
mv_cmd: str = 'mv -t "$1" "${@:2}'

# Command for creating directories.
mkdir_cmd: str = 'mkdir -p $1'

# TODO: still unsure about if this is necessary; marking for now
# set_file_perms =


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


def copy(dest: str, src: str | list[str]) -> bool:
    """
    Copies files from the given path(s) src to dest.

    :param dest: str
        Destination path to copy source(s) to.
    :param src: str | list[str]
        Source path(s) to copy from.
    :return: True if the copy was successful; False otherwise.
    """
    print(f'TEMP: copy from {src} to {dest}')
    return True


def move(dest: str, src: str | list[str]) -> bool:
    """
    Moves files from the given path(s) src to dest.

    :param dest: str
        Destination path to move source(s) to.
    :param src: str | list[str]
        Source path(s) to copy from.
    :return: True if the move was successful; False otherwise.
    """
    print(f'TEMP: move {src} to {dest}')
    return True


def mkdir(path: str) -> bool:
    """
    Creates directory if it doesn't exist at the specified path.

    :param path: str
        Path to create directory to.
    :return: True if the directory creation was successful or if it already exists; False otherwise.
    """
    print(f'TEMP: Create directory to path {path} if it doesn\'t exist.')
    return True
