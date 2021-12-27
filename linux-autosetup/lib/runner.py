import getpass
import logging
import os
import pwd
import threading
import time
from subprocess import Popen, PIPE

from lib.logger import log


class Runner:
    """
    Provides a means of running command strings and handles management of permission elevations.

    Limitations:
        Since is_root checks if the euid is 0, users may not be able to run as target users if they are not the
        root user, even if they may have sufficient privileges to do so. This means
        users are required to run the script as root if they want to target another user.
    """
    is_root = os.geteuid() == 0

    def __init__(self, target_user: str = None, sudo_loop: bool = True):
        """
        :param target_user: The user to run commands under.
                            Only allowed if the script is root.
        :param sudo_loop:   Whether script should refresh sudo calls to avoid sudo timeout.
        """
        log('Initializing runner object.', logging.INFO)
        if target_user and target_user != getpass.getuser():
            assert self.is_root, 'Setting target users is only allowed if the script is run as root.'
            try:
                info = pwd.getpwnam(target_user)
            except KeyError:
                print('User %s does not exist.' % target_user)
                raise
            self.target_user = dict(
                uname=target_user,
                gid=info.pw_gid,
                uid=info.pw_uid,
                env=os.environ.copy()
            )
            self.target_user['env'].update({'HOME': info.pw_dir, 'LOGNAME': target_user, 'USER': target_user})
        else:
            self.target_user = None
        self.has_target_user = self.target_user is not None
        if sudo_loop:
            self.sudo_loop()
        log(f'Runner object was created with the following settings:\n{str(self)}', logging.DEBUG)

    @staticmethod
    def sudo_loop():
        """
        Once called, loop sudo validate every 5 seconds until parent process dies.
        Sudo may prompt for a password at call start.

        Raises PermissionError if the first sudo call is not successful.
        """
        log('Starting sudo loop.', logging.INFO)
        # TODO: FIX SUDO COMMENTS AND PLACEHOLDER ECHOS WHEN NOT A NUISANCE

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
                    # Popen(['sudo', '-v']).wait()
                    i = 0.0
                else:
                    time.sleep(0.5)
                    i += 0.5
        threading.Thread(target=sudo_loop_thread).start()
        log('Started sudo_loop_thread.', logging.DEBUG)

    def run(self, cmd: str, args: list[str] = None) -> (int, str):
        """
        Run the given command(s) through the shell along with any arguments.

        :param cmd:     String of command(s) to run.
        :param args:    Optional arguments to supply to the shell.
        :return:        Return-code of running command(s).
        """
        log(f'Running cmd:\n{cmd}', logging.DEBUG)
        args = args or []
        p = None
        try:
            if self.target_user:
                def set_ids():
                    os.initgroups(self.target_user['uname'], self.target_user['gid'])
                    os.setuid(self.target_user['uid'])

                p = Popen([cmd, ''] + args,
                          preexec_fn=set_ids, stderr=PIPE, universal_newlines=True, shell=True, env=self.target_user['env'])
            else:
                p = Popen([cmd, ''] + args, stderr=PIPE, universal_newlines=True, shell=True)
            _, error = p.communicate()
            if p.returncode != 0:
                log(f'The following command exited with a non-zero returncode:\n'
                    f'{cmd}\n'
                    f'exit code {p.returncode}\n'
                    f'stderr {error}', logging.ERROR)
        except KeyboardInterrupt:
            if p:
                p.terminate()
            return exit('\nAborting.')
        return p.returncode

    def __str__(self):
        rtn = '\n'.join([
            f'is_root: {self.is_root}',
            f'target_user: {self.target_user}',
            f'has_target_user: {self.has_target_user}'
        ])
        return rtn
