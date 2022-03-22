from random import shuffle

class ArgsDict(dict):
    def __init__(self,*args, **kargs):
        super().__init__(*args, **kargs)

def remote_args(**kargs):
    """ helper function to be used with .sync_parallel and similar methods"""
    result = ArgsDict()
    for k in sorted(kargs.keys()):
        result[k] = kargs[k]
    return result

class ServerlessCloud:
    def __init__(self, requires:str, **kargs):
        self.requires = requires

    def add(self, a_func):
        assert callable(a_func)

        def prll(inpt):
            inpt = list(inpt)
            ret_rez = list(a_func(**i) for i in inpt)
            shuffle(ret_rez)
            return ret_rez

        a_func.sync_parallel = prll
        a_func.sync_remote = a_func

        return a_func