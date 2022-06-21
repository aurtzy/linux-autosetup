import scriptman

if __name__ == '__main__':
    try:
        scriptman.run_module()
    except BaseException:
        if getattr(scriptman.args, 'debug', False):
            raise
    exit()
