import logging
import subprocess
import threading
import time
import typing
from os import PathLike, fspath, environ

from .settings import Settings
from .logger import log
from .cli import get_option_i


class Cmd(Settings, keys=('system_cmds',)):
    """

    Settings:
        su: str
            Command used for elevating commands when appropriate (e.g. "sudo").
    """

    su: str

    @classmethod
    def init_settings(cls, **key_config):
        def assert_cmd(key) -> str:
            return cls.assert_tp(key_config, key, str)

        try:
            # superuser
            cls.su = assert_cmd('su')
        except TypeError:
            log('Values must be specified for system commands in the config to avoid ambiguity.', logging.ERROR)
            raise

    def __init__(self, cmd: list[str], as_su: bool = False):
        self.cmd = cmd
        self.as_su = as_su


def run(cmd: typing.Union[list, str], pipe: typing.Union[list, str] = None):
    """
    Run the given command cmd.

    If given a pipe value, it is piped into cmd.

    :param cmd: The command to be run. This will be passed as-is into subprocess.run().
    :param pipe: Disabled if pipe is None.
                 If pipe is a list, it is interpreted as a command that is piped into cmd.
                 Otherwise, str(pipe) is piped into cmd.
    :return: Return code of cmd (or pipe_cmd). Note that 0 means success, while any other
             integer indicates that the command was unsuccessful.
    """
    log(f'Running command:\n{cmd}', logging.DEBUG)
    try:
        if isinstance(pipe, list):
            pipe_cmd = subprocess.Popen(pipe, stdout=subprocess.PIPE)
            main_cmd = subprocess.Popen(cmd, stdin=pipe_cmd.stdout)
            main_cmd.communicate()
        elif pipe:
            main_cmd = subprocess.Popen(cmd, stdin=subprocess.PIPE)
            main_cmd.communicate(bytes(pipe, encoding='utf-8'))
        else:
            subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as error:
        log(f'Encountered an error running shell commands:\n'
            f'{error}', logging.ERROR)
        return error.returncode
    return 0


def shell_run(cmd: str, *args: str) -> int:
    """
    todo: DEPRECATED
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
        # subprocess.run([cmd, ''] + list(args), check=True, text=True, shell=True)
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
    log('Starting sudo loop.', logging.DEBUG)

    # TODO: FIX SUDO COMMENTS WHEN NOT A NUISANCE
    #if run(['sudo', '-v']) != 0:
    #    raise PermissionError('sudo could not validate.')

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
    log('Started sudo loop thread.', logging.DEBUG)


class Path(PathLike, Settings, keys=('system_cmds',)):
    """
    Provides methods in which to manipulate and interact with files on the system.

    Calling these methods will invoke a check for whether the path(s) exists, and an error
    is raised if a path does not exist.

    File manipulation commands will be elevated with permissions as necessary.

    Settings:
        cp: str
            Used to copy files from one path to another.
            Expects: $1 = target directory; ${@:2} = files to move to target directory
        mv: str
            Used to move files from one path to another.
            Expects: $1 = target directory; ${@:2} = files to move to target directory
        mkdir: str
            Used to create directories at specified paths.
            Expects: $1 = Path of directory to be made
        check_path: str
            Used to confirm if a path exists to some file/directory.
            Excepts: $1 = Path to check
        check_dir: str
            Used to confirm if a path exists to some directory.
            Excepts: $1 = Path to check
    """
    # todo?
    #   init_dir instead of valid_dir; can be initialized any
    #   time making initialization of a Path more lazy (good),
    #   so only paths that are to be used are initialized at pre_install/backup
    #  fields: is/needs_root, exists
    #   question of how root field works - is read/write important to consider?
    #    currently thinking yes. split "is_root" into maybe "root_read" and "root_write"?
    #    or no... files without read permission fall in a weird place. actually,
    #    it's everything that's in a weird place.
    #    how to get correct permissions for files? is pushing 'sudo' to command list
    #    enough to satisfy cases? if it is enough, then is having a single 'root'
    #    field also enough?
    environ.update({'DOLLARSIGN': '$'})

    cp: str
    mv: str
    mkdir: str
    check_path: str
    check_dir: str

    @staticmethod
    def files_need_perms(mode: str = 'r', *paths: typing.Union[str, PathLike]):
        """Tests passed paths for a PermissionError when trying to open."""
        for path in paths:
            try:
                open(path, mode).close()
            except PermissionError:
                return True
            except IOError:
                continue
            else:
                continue
        else:
            return False

    @classmethod
    def init_settings(cls, **key_config):

        def assert_cmd(key) -> str:
            return cls.assert_tp(key_config, key, str)

        try:
            # cp
            cls.cp = assert_cmd('cp')

            # mv
            cls.mv = assert_cmd('mv')

            # mkdir
            cls.mkdir = assert_cmd('mkdir')

            # check_path
            cls.check_path = assert_cmd('check_path')

            # check_dir
            cls.check_dir = assert_cmd('check_dir')
        except TypeError:
            log('Values must be specified for system commands in the config to avoid ambiguity.', logging.ERROR)
            raise

    @classmethod
    def copy(cls, dest: typing.Union[str, PathLike], *args: typing.Union[str, PathLike]) -> bool:
        """
        Copies files from the given path(s) args to dest.

        :return: True if the copy was successful; False otherwise.
        """
        cmd = cls.cp
        if cls.files_need_perms('r', dest) or cls.files_need_perms('w', *args):
            cmd = f'{Cmd.su} {cmd}'
        exit_code = shell_run(cmd, dest, *map(fspath, args))
        return not bool(exit_code)

    @classmethod
    def move(cls, dest: typing.Union[str, PathLike], *args: typing.Union[str, PathLike]) -> bool:
        """
        Moves files from the given path(s) args to dest.

        :return: True if the move was successful; False otherwise.
        """
        cmd = cls.mv
        if cls.files_need_perms('r', dest) or cls.files_need_perms('w', *args):
            cmd = f'{Cmd.su} {cmd}'
        exit_code = shell_run(cmd, dest, *map(fspath, args))
        return not bool(exit_code)

    @classmethod
    def mkdir(cls, path: typing.Union[str, PathLike]) -> bool:
        """
        Creates directory if it doesn't exist at the specified path.

        :return: True if the directory creation was successful or if it already exists; False otherwise.
        """
        cmd = cls.mkdir
        if cls.files_need_perms('w', path):
            cmd = f'{Cmd.su} {cmd}'
        exit_code = shell_run(cmd, *map(fspath, path))
        return not bool(exit_code)

    @classmethod
    def valid_dir(cls, path: typing.Union[str, PathLike]):
        """
        Validates the given directory path. Unlike path_exists, this method allows the given directory path
        to be created if it is not found.

        If no_confirm is true and the path does not exist, automatically create the directory and return its
        respective Path object.
        Otherwise, prompt the user for options to handle the missing directory.

        :return: A Path object with path pass as an argument if the path is valid; None otherwise.
        """
        while True:
            log(f'Checking if "{path}" is an existing directory...', logging.DEBUG)
            if shell_run(f'{Cmd.su} {cls.check_dir}', path) == 0:
                log(f'Found.', logging.DEBUG)
                return cls(path)
            else:
                log(f'The following path could not be found: {path}', logging.WARNING)
                i = get_option_i(('Attempt to find the directory again',),
                                 ('Create a new directory',),
                                 ('Ignore this path for the session',),
                                 ('Abort this script',),
                                 prompt=f'The directory "{path} could not be found.\n'
                                        f'Please choose how this should be handled')
                if i == 0:
                    log('Attempting to find directory again.', logging.INFO)
                    continue
                elif i == 1:
                    log(f'Creating new directory.', logging.INFO)
                    cls.mkdir(path)
                    return cls(path)
                elif i == 2:
                    log(f'Ignoring this path for the session.', logging.INFO)
                    return None
                else:
                    log('Aborting.', logging.INFO)
                    exit(1)

    def __init__(self, path: str):
        self.path = path

    def __fspath__(self) -> str:
        return self.path

    def __str__(self) -> str:
        return self.path
