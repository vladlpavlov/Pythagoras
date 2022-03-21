from random import shuffle

def sync_remote(**kargs):
    return kargs

class ServerlessCloud:
    def __init__(self, *args, **kargs):
        pass

    def add(self, a_func):
        assert callable(a_func)

        def prll(inpt):
            inpt = list(inpt)
            ret_rez = list(a_func(**i) for i in inpt)
            shuffle(ret_rez)
            return ret_rez

        a_func.parallel = prll
        a_func.sync_remote = a_func

        return a_func