from Pack import Pack


if __name__ == '__main__':
    pack1 = Pack(apps=[])
    print(pack1.apps)
    pack2 = Pack(apps=['test', 'hi'])
    print(pack2.apps)
    thing = {
        'a': 'hi'
    }
    print('%s, %s' % (thing.get('a'), thing.get('b')))
    pack1.install()
    print(Pack.packs)
