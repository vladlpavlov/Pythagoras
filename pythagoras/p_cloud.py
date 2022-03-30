import os
from functools import wraps
from random import Random
from inspect import getsource
from pythagoras import PValueAddress, PFuncOutputAddress, FileDirDict, KwArgsDict


def kw_args(**kwargs):
    """ Helper function to be used with .parallel and similar methods

    It enables simple syntax to simultaneously launch
    many remote instances of a function with different input arguments:

    some_slow_function.parallel(
        kw_args(arg1=i, arg2=j) for i in range(100) for j in range(15)  )
    """
    return  KwArgsDict(**kwargs)


class SharedStorage_P2P_Cloud:
    """ Simple P2P cloud based on using a shared folder (via Dropbox, NFS, etc.)

    Allows to distribute an execution of a program via multiple computers that share the same file folder.
    The program must be launched an every computer,
    with shared_dir_name parameter of their SharedStorage_P2P_Cloud object pointing to the same shared folder.
    Execution of parallelized calls ( function.sync_parallel(...) ) will be distributed between participating computers.
    Execution of all other calls will be redundantly carried on each participating computer.
    """

    def __init__(self, requires:str="", shared_dir_name:str="SharedStorage_P2P_Cloud"):

        assert not os.path.isfile(shared_dir_name)
        if not os.path.isdir(shared_dir_name):
            os.mkdir(shared_dir_name)
        assert os.path.isdir(shared_dir_name)
        self.base_dir = os.path.abspath(shared_dir_name)
        self.requires = requires # TODO: polish this functionality later
                                 # we need to convert "requires" to some "normal" form to
                                 # prevent syntax variability from impacting hash calculations
        self.functions = []
        self.value_store = FileDirDict(dir_name=os.path.join(self.base_dir, "value_store"))
        self.func_output_store = FileDirDict(dir_name=os.path.join(self.base_dir, "func_output_store"))


    def push_value(self,value):
        """ Add a value to value_store"""
        key = PValueAddress(value)
        if not key in self.value_store:
            self.value_store[key] = value
        return key


    def add_pure_function(self, a_func): # TODO: implement all 3 scenarios of stochastic purity checks
        assert callable(a_func)

        @wraps(a_func)
        def wrapped_function(**kwargs):
            """compose memoized version of a function"""
            kwargs_packed = KwArgsDict(kwargs).pack(cloud=self)
            func_key = PFuncOutputAddress(wrapped_function, kwargs_packed, self)

            if func_key in self.func_output_store:
                result_key = self.func_output_store[func_key]
                result = self.value_store[result_key]
            else:
                kwargs_unpacked = KwArgsDict(kwargs).unpack(cloud=self)
                result = a_func(**kwargs_unpacked) # TODO: add exception handling mechanism
                result_key = self.push_value(result)

                if func_key in self.func_output_store:
                    assert self.func_output_store[func_key] == result_key, (
                        "Stochastic purity check has failed") # TODO: change to a "raise" statement
                else:
                    self.func_output_store[func_key]=result_key

            return result

        def sync_parallel(inpt):
            """Enable parallel execution of multiple instances of function"""
            input_list = list(inpt)
            for e in input_list:
                assert isinstance(e,KwArgsDict)
            shuffled_input_list = list(enumerate(input_list))

            Random().shuffle(shuffled_input_list)   # Important: we are using a new instance of Random object that
                                                    # does not share the same seed with any other Random object.
                                                    # This is done to ensure correct parallelization via randomization
                                                    # in cases when a cloudized function
                                                    # explicitly sets seed value for the default Random object,
                                                    # which it might do in order to be qualified as a pure function.

            result = []
            for e in shuffled_input_list:
                func_call_arguments = e[1]
                func_call_output = wrapped_function(**func_call_arguments)
                result_item = (e[0],func_call_output)
                result.append( result_item )

            result = sorted(result, key=lambda t:t[0])

            return [e[1] for e in result]

        def async_parallel(inpt):
            raise NotImplementedError

        def async_remote(**kwargs):
            raise NotImplementedError

        def is_stored(**kwargs):
            """Check if the function output for these arguments has been calculated and cached"""
            kwargs_packed = KwArgsDict(kwargs).pack(cloud=self)
            func_key = PFuncOutputAddress(wrapped_function, kwargs_packed, self)
            return func_key in self.func_output_store

        wrapped_function.sync_parallel = sync_parallel
        wrapped_function.async_parallel = async_parallel
        wrapped_function.sync_remote = a_func
        wrapped_function.async_remote = async_remote
        wrapped_function.serverless_cloud = self
        wrapped_function.full_string_repr = f"FUNCTION REQUIRES {self.requires}, SOURCE {getsource(a_func)}"
        wrapped_function.is_stored = is_stored

        self.functions.append(wrapped_function)

        return wrapped_function

class PCloud(SharedStorage_P2P_Cloud):
    """ Dummy class used in the intro tutorial. Shall be refactored later into a parent class."""

    def __init__(self, requires:str="", shared_dir_name:str="SharedStorage_P2P_Cloud", connection:str=""):
        super().__init__(requires, shared_dir_name)