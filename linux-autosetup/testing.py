from enum import Enum
from runner import Runner
from pack import Pack


class Test:
    var1 = 0

    def __init__(self):
        self.var2 = 1
        self.var3 = 2

    def __str__(self):
        return str(self.var1)


if __name__ == '__main__':
    test = Test()
    print(test)
    print(Test)

    # print(Pack.global_settings.items())
    pack1 = Pack('PACK_NAME', ['app1', 'app2'])
    print(pack1)

