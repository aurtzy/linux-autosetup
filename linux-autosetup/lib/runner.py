import logging
import os
import pwd
import subprocess

from lib.logger import log


class Runner:
    """
    Provides a means of running commands as another user.

    This code assumes the script is run as root.
    """

    def __init__(self, target_uname: str = None):
        """
        :param target_uname: None if the script does not have a target user; applies when running
                            directly as root user.
                            Expects a valid dictionary containing:
                                uname: str, the target user name
                                gid: int, the target user group id
                                uid: int, the target user id
        """
        log('Initializing runner.', logging.INFO)
        if target_uname:
            try:
                info = pwd.getpwnam(target_uname)
            except KeyError:
                log(f'User {target_uname} does not exist.', logging.ERROR)
                raise
            self.target_user = dict(
                uname=target_uname,
                gid=info.pw_gid,
                uid=info.pw_uid)
        else:
            self.target_user = None
        log(f'Runner object was created with the following settings:\n{str(self)}', logging.DEBUG)

    # @staticmethod
    # def sudo_loop():
    #     """
    #     Once called, loop sudo validate every 5 seconds until parent process dies.
    #     Sudo may prompt for a password at call start.
    #
    #     Raises PermissionError if the first sudo call is not successful.
    #     """
    #     log('Starting sudo loop.', logging.INFO)
    #     # FIX SUDO COMMENTS AND PLACEHOLDER ECHOS WHEN NOT A NUISANCE
    #
    #     # p = Popen(['sudo', '-v'])
    #     # p.communicate()
    #     # if p.returncode != 0:
    #     #   raise PermissionError('sudo could not validate.')
    #
    #     def sudo_loop_thread():
    #         i = 0.0
    #         while True:
    #             if not threading.main_thread().is_alive():
    #                 log('Exiting sudo_loop_thread.', logging.DEBUG)
    #                 break
    #             if i >= 5.0:
    #                 log('Revalidating sudo.', logging.DEBUG)
    #                 # Popen(['sudo', '-v']).wait()
    #                 i = 0.0
    #             else:
    #                 time.sleep(0.5)
    #                 i += 0.5
    #     threading.Thread(target=sudo_loop_thread).start()
    #     log('Started sudo_loop_thread.', logging.DEBUG)

    def run(self, cmd: str, args: list[str] = None) -> int:
        """
        Run the given command(s) through the shell along with any arguments.

        :param cmd:     String of command(s) to run.
        :param args:    Optional arguments to supply to the shell.
        :return:        Return-code of running command(s).
        """
        log(f'Running command(s):\n{cmd}', logging.DEBUG)
        args = args or []

        def set_ids():
            if self.target_user:
                os.initgroups(self.target_user['uname'], self.target_user['gid'])
                os.setuid(self.target_user['uid'])

        try:
            subprocess.run([cmd, ''] + args, preexec_fn=set_ids, check=True, text=True, shell=True)
        except subprocess.CalledProcessError as error:
            log(f'Encountered a CalledProcessError exception:\n'
                f'{error}\n', logging.ERROR)
            return error.returncode
        return 0

    def __str__(self):
        rtn = f'target_user: {self.target_user}'
        return rtn
