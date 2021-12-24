import getpass
import os
import pwd
import shlex
from subprocess import Popen


class Runner:
    """
    Provides a means of running command strings and handles management of permission elevations.

    Limitations:
        os.geteuid() may not produce desired results if a user with sufficient privileges is not
        an actual root user.
    """
    is_root = os.geteuid() == 0

    def __init__(self, target_user: str = None, sudo_loop: bool = True):
        """
        :param target_user: The user to run commands under.
                            Only allowed if the script is root, and
                            will throw a KeyError if username cannot be associated with anything.
        :param sudo_loop:   Whether script should refresh sudo calls to avoid sudo timeout.
        """
        if target_user != getpass.getuser():
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
        self.sudo_loop = sudo_loop

        #self.sudo_validate()

    def sudo_validate(self):
        """
        Validate sudo, prompting password if necessary and refreshing timeout.

        This should be used in conjunction with a loop to ensure sudo does not expire
        while commands are being run, which
        """
        if not self.is_root:
            Popen(['sudo', '-v']).wait()

    def run(self, cmd: str, args: list[str] = None) -> int:
        """
        Run the given command(s) through the shell along with any arguments.

        :param cmd:     String of command(s) to run.
        :param args:    Optional arguments to supply to the shell.
        :return:        Return-code of running command(s).
        """
        args = list(map(lambda x: shlex.quote(x), args)) if args else ['']
        if self.target_user:
            def get_set_ids():
                def set_ids():
                    os.initgroups(self.target_user['uname'], self.target_user['gid'])
                    os.setuid(self.target_user['uid'])
                return set_ids()
            p = Popen([cmd, ''] + args,
                      preexec_fn=get_set_ids(), universal_newlines=True, shell=True, env=self.target_user['env'])
        else:
            p = Popen([cmd, ''] + args, universal_newlines=True, shell=True)
        p.communicate()
        return p.returncode
