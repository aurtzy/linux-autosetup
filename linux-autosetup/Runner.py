import getpass
from os import getuid
from subprocess import Popen, PIPE

PASSWD: str


def get_passwd():
    """
    Get user sudo password as securely as possible.

    :return: None
    """
    global PASSWD
    return
    if getuid() != 0:
        PASSWD = getpass.getpass("Enter sudo password: ")
        p = Popen('sudo -Slk &> /dev/null <<< "%s"' % PASSWD, shell=True)
        p.communicate(PASSWD + '\n')
        if p.returncode != 0:
            raise Exception("error validating password")


def run(cmd: str) -> int:
    """
    Run cmd param in shell with appropriate permissions

    :param cmd: Command(s) to run in shell
    :return: Return code after running last command in cmd
    """
    if cmd is None:
        raise Exception('cmd argument is type NoneType')
    if cmd.split(' ')[0].strip() == 'sudo':
        runner = Popen(cmd.replace('sudo', 'sudo -Sk'), stdin=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
        runner.communicate(PASSWD + '\n')
    else:
        runner = Popen(cmd, universal_newlines=True, shell=True)
        runner.wait()
    return runner.returncode
