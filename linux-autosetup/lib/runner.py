import logging
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
