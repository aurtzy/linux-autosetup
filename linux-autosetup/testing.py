
import pack
from lib.runner import Runner

try:
    import yaml
except ImportError:
    from pip._internal import main as pip
    pip(['install', '--user', 'yaml'])
    import yaml

try:
    from aenum import Enum, extend_enum
except ImportError:
    from pip._internal import main as pip
    pip(['install', '--user', 'aenum'])
    from aenum import Enum, extend_enum


class Test:
    var1 = 0

    def __init__(self):
        self.var2 = 1
        self.var3 = 2

    def __str__(self):
        return str(self.var1)


if __name__ == '__main__':

    # can be set to be more verbose if a --debug type option is set
    # logging.basicConfig(format='%(message)s', level=logging.INFO)
    try:
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        file.close()
    except yaml.YAMLError as error:
        raise yaml.YAMLError('There was an error reading config.') from error

    runner = Runner('alvin')

    #print(config['predefined']['alias_prefix'])
    # print(thing.run('ech hi! $1; echo no!; sleep 2s; asdf', ['man'])[1])
    settings = config

    #print_settings()

    # pack.fallback_settings.update({'error_handling': pack.ErrorHandling.ABORT})
    some_pack = pack.Pack('some_pack', pack.fallback_settings)
    #print(some_pack)

    def thisthing():
        print(__name__)

    print(__file__)
    runner.run('yay')

