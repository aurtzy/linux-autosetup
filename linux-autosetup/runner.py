import getpass
import os
import pwd
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
                            Only allowed if the script is root.
        :param sudo_loop:   Whether script should refresh sudo calls to avoid sudo timeout.
        """
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
        self.has_target_user = target_user is not None
        if sudo_loop:
            self.sudo_loop()

    @staticmethod
    def sudo_loop():
        """
        Once called, loop sudo validate every 5 seconds until parent process dies.
        Sudo may prompt for a password at call start.

        Raises PermissionError if the first sudo call is not successful.
        """
        # TODO: FIX SUDO COMMENTS AND PLACEHOLDER ECHOS WHEN NOT A NUISANCE
        p = Popen('echo sudo_loop called', shell=True)
        p.communicate()
        if p.returncode != 0:
            raise PermissionError('oh no! sudo failed on the call??')

        # p = Popen(['sudo', '-v'])
        # p.communicate()
        # if p.returncode != 0:
        #   raise PermissionError('sudo could not validate.')

        def sudo_loop_thread():
            i = 0.0
            while True:
                if not threading.main_thread().is_alive():
                    break
                if i >= 5.0:
                    Popen('echo sudo_loop', shell=True)
                    # Popen(['sudo', '-v']).wait()
                    i = 0.0
                else:
                    time.sleep(0.5)
                    i += 0.5
        threading.Thread(target=sudo_loop_thread).start()

    def run(self, cmd: str, args: list[str] = None) -> int:
        """
        Run the given command(s) through the shell along with any arguments.

        :param cmd:     String of command(s) to run.
        :param args:    Optional arguments to supply to the shell.
        :return:        Return-code of running command(s).
        """
        args = args if args else []
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
