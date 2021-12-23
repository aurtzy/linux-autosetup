import getpass
import os
from enum import Enum
from os import getuid
from subprocess import Popen, PIPE


class Runner:

    class ErrorHandling(Enum):
        """
        Determines how errors should be handled when running commands.

        PROMPT : Prompt users to try running the command again, skip.

        SKIP : Skip commands that error out and continue running commands.

        ABORT : Abort running the rest of the command.
        """
        PROMPT = 1
        SKIP = 2
        ABORT = 3

    def __init__(self):
        """
        Get user sudo password as securely as possible.

        :return: None
        """
        if getuid() != 0:
            self.is_root = False
            self.passwd = getpass.getpass("Enter sudo password: ")
            self.p = Popen('sudo -S echo &> /dev/null <<< "%s"' % self.passwd, universal_newlines=True, shell=True)
            self.p.communicate(self.passwd + '\n')
            if self.p.returncode != 0:
                raise Exception("error validating password")
        else:
            self.is_root = True
            self.passwd = None

    def run(self, cmds: list[str], error_handle: ErrorHandling) -> bool:
        """
        Runs given list of commands, each in their own subprocess in order to avoid sudo expiring.

        Limitation: Multi-line commands (like if; then statements) must be condensed into single lines due
                    to lines being separated this way.

        :param cmds: Command(s) to run in shell
        :param error_handle: Indicates how to handle errors
        :return: Whether running the command(s) was successful. Always true when cmds is None.
        """
        if cmds is None:
            return True

        for cmd in cmds:
            if not self.is_root and 'sudo' in cmd:
                runner = Popen(cmd.replace('sudo', 'sudo -S'),
                               stdin=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
                # runner.stdin.write(self.passwd + '\n')
            else:
                runner = Popen(cmd, universal_newlines=True, shell=True)

        return True
