import os
import shlex
import subprocess
import sys

import pack
import runner
from aenum import extend_enum, Enum

try:
    import yaml
except ImportError:
    from pip._internal import main as pip

    pip(['install', '--user', 'yaml'])
    import yaml
import tarfile


class Test:
    var1 = 0

    def __init__(self):
        self.var2 = 1
        self.var3 = 2

    def __str__(self):
        return str(self.var1)


if __name__ == '__main__':
    # print(Pack.global_settings.items())
    # pack1 = Pack('PACK_NAME', ['app1', 'app2'], settings=Pack.Settings(install_cmd='echo $apps$! install biggus diccus!',
    #                                                                   create_backup_cmd='echo deez $backup_sources$',
    #                                                                  extract_backup_cmd='echo deez other $backup_sources$, $install_cmd$'))
    # print(pack1)
    # subprocess = Runner()
    # subprocess.run(['echo $USER; sudo echo $USER'], Runner.ErrorHandling.PROMPT)
    # text = 'echo hello!; echo no way!!; echo "some;string ;"'
    # shlexer = shlex(instream=text, punctuation_chars=True)
    # print(list(shlexer))
    # p = subprocess.Popen(['tar -cJPf - "${@:2}" | openssl enc -e -aes-256-cbc -md sha512 -pbkdf2 -salt -out "$1.tar.xz.enc"', ''] +
    #                      ['/home/alvin/Downloads/testing/encrypted_boot', '/home/alvin/Downloads/testing/boot loli.jpeg'],
    #                      stdin=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
    # p.wait()
    # print('hello' % 'hi')

    # can be set to b if a --debug type option is set

    sys.tracebacklimit = None  # None if --debug option is present else 0
    try:
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        file.close()
    except yaml.YAMLError as error:
        raise yaml.YAMLError('There was an error reading config.') from error

    thing = runner.Runner('alvin')

    print(config['predefined']['alias_prefix'])
    # print(thing.run('ech hi! $1; echo no!; sleep 2s; asdf', ['man'])[1])
    settings = config


    def print_settings(verbose=True):
        rtn = []

        def append_dict(a_dict: dict, lvl: int):
            for key, val in a_dict.items():
                if isinstance(val, dict):
                    rtn.append("\t" * lvl + f'{key}:')
                    append_dict(val, lvl + 1)
                else:
                    rtn.append(('\t' * lvl) + f'{key}: ' + (f'\n{val}'.replace('\n', '\n' + '\t' * (lvl + 1))
                                                            if isinstance(val, str) and '\n' in val else
                                                            val.name if issubclass(type(val), Enum) else str(val)))

        if verbose:
            append_dict(settings, 0)
        print('\n'.join(rtn))
    settings['packs']['defaults']['ubuntu']['app_settings']['install_type'] = pack.Predefined.AppInstallTypes.FLATPAK

    print_settings()
