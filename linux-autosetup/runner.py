import getpass
from os import getuid
from subprocess import Popen, PIPE


class Runner:

    def __init__(self):
        """
        Get user sudo password as securely as possible.

        :return: None
        """
        if getuid() != 0:
            self.is_root = False
            self.passwd = getpass.getpass("Enter sudo password: ")
            p = Popen('sudo -S echo &> /dev/null <<< "%s"' % self.passwd, shell=True)
            p.communicate(self.passwd + '\n')
            if p.returncode != 0:
                raise Exception("error validating password")
        else:
            self.is_root = True
            self.passwd = None

    def run(self, cmd: str) -> int:
        """
        Run cmd param in shell with appropriate permissions

        :param cmd: Command(s) to run in shell
        :return: return_code value after running last command in cmd
        """
        if cmd is None:
            raise Exception('cmd argument is type NoneType')
        if not self.is_root and 'sudo' in cmd:
            runner = Popen(cmd.replace('sudo', 'sudo -Sk'), stdin=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
            runner.communicate(self.passwd + '\n')
        else:
            runner = Popen(cmd, universal_newlines=True, shell=True)
            runner.wait()
        return runner.returncode
