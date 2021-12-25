import getpass
import os
import pwd
import shlex
import threading
import time
from subprocess import Popen


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
                            Only allowed if the script is root, and
                            will throw a KeyError if username cannot be associated with anything.
        :param sudo_loop:   Whether script should refresh sudo calls to avoid sudo timeout.
        """
        if target_user and target_user != getpass.getuser():
            if not self.is_root:
                raise Exception('Setting target users is only allowed if the script is run as root.')
            info = pwd.getpwnam(target_user)
            self.target_user = dict(
                uname=target_user,
                gid=info.pw_gid,
                uid=info.pw_uid,
                env=os.environ.copy()
            )
            self.target_user['env'].update({'HOME': info.pw_dir, 'LOGNAME': target_user, 'USER': target_user})
        else:
            self.target_user = None
        self.has_target_user = target_user is not None
        if sudo_loop:
            threading.Thread(target=Runner.sudo_loop).start()

    @staticmethod
    def sudo_loop():
        """
        Meant to be run in a separate thread - threading.Thread(target=sudo_loop)

        Loop sudo validate every 5 seconds.

        Sudo may prompt for a password at call start.

        This should be used in conjunction with a loop to ensure sudo does not expire
        while commands are being run.
        :return: Popen validation process if self.is_root; else None
        """
        def sleep():
            i = 0.0
            while i < 5:
                if not threading.main_thread().is_alive():
                    break
                time.sleep(0.5)
                i += 0.5
        sleeper = threading.Thread(target=sleep)
        while True:
            if not threading.main_thread().is_alive():
                break
            if not sleeper.is_alive():
                # TODO: FIX COMMENT AND REMOVE BELOW WHEN NOT A NUISANCE
                Popen('echo sudo_loop', shell=True)
                #Popen(['sudo', '-v']).wait()
                sleeper = threading.Thread(target=sleep)
                sleeper.start()

    def run(self, cmd: str, args: list[str] = None) -> int:
        """
        Run the given command(s) through the shell along with any arguments.

        If sudo_loop is True, run sudo_validate() every 5 seconds until process terminates.

        :param cmd:     String of command(s) to run.
        :param args:    Optional arguments to supply to the shell.
        :return:        Return-code of running command(s).
        """
        args = list(map(lambda x: shlex.quote(x), args)) if args else ['']
        if self.target_user:
            def set_ids():
                os.initgroups(self.target_user['uname'], self.target_user['gid'])
                os.setuid(self.target_user['uid'])
            p = Popen([cmd, ''] + args,
                      preexec_fn=set_ids, universal_newlines=True, shell=True, env=self.target_user['env'])
        else:
            p = Popen([cmd, ''] + args, universal_newlines=True, shell=True)
        try:
            p.communicate()
        except KeyboardInterrupt:
            p.terminate()
            exit('\nAborting.')
        return p.returncode