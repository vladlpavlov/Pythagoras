import os
from copy import deepcopy
from functools import wraps
from random import shuffle
from inspect import getsource
from datetime import datetime
from pythagoras import PHashAddress, SimplePersistentDict, PValueAddress, PFuncResultAddress, FileDirDict, KwArgsDict



def kw_args(**kwargs):
    """ helper function to be used with .parallel and similar methods

    It enables simple syntax to simultaneously launch
    many remote instances of a function with different input arguments:

    some_slow_function.parallel(
        kw_args(arg1=i, arg2=j) for i in range(100) for j in range(15)  )
    """
    return  KwArgsDict(**kwargs)


class SharedStorage_P2P_Cloud:

    def __init__(self, requires:str="", shared_dir_name:str="Simple_P2P_Cloud"):

        assert not os.path.isfile(shared_dir_name)
        if not os.path.isdir(shared_dir_name):
            os.mkdir(shared_dir_name)
        assert os.path.isdir(shared_dir_name)
        self.base_dir = os.path.abspath(shared_dir_name)
        self.requires = requires # TODO: polish this functionality later
                                 # we need to convert "requires" to some "normal" form to
                                 # prevent sintax variability from impacting hash calculations
        self.functions = []
        self.value_store = FileDirDict(dir_name=os.path.join(self.base_dir, "value_store"))
        self.func_output_store = FileDirDict(dir_name=os.path.join(self.base_dir, "func_execution_results"))


    def push_value(self,value):
        key = PValueAddress(value)
        if not key in self.value_store:
            self.value_store[key] = value
        return key


    def add_pure_function(self, a_func): # TODO: add some basic checks for purity
        assert callable(a_func)

        @wraps(a_func)
        def wrapped_function(**kwargs):
            kwargs_packed = KwArgsDict(kwargs).pack(cloud=self)
            func_key = PFuncResultAddress(wrapped_function, kwargs_packed, self)

            if func_key in self.func_output_store:
                result_key = self.func_output_store[func_key]
                result = self.value_store[result_key]
            else:
                kwargs_unpacked = KwArgsDict(kwargs).unpack(cloud=self)
                result = a_func(**kwargs_unpacked)
                result_key = self.push_value(result)
                self.func_output_store[func_key]=result_key

            return result

        def parallel(inpt):
            input_list = list(inpt)
            for e in input_list:
                assert isinstance(e,KwArgsDict)
            shuffled_input_list = list(enumerate(input_list))
            shuffle(shuffled_input_list) #TODO: deal with seeds

            result = []
            for e in shuffled_input_list:
                func_call_arguments = e[1]
                func_call_output = wrapped_function(**func_call_arguments)
                result_item = (e[0],func_call_output)
                result.append( result_item )

            result = sorted(result, key=lambda t:t[0])

            return [e[1] for e in result]

        def is_stored(**kwargs):
            kwargs_packed = KwArgsDict(kwargs).pack(cloud=self)
            func_key = PFuncResultAddress(wrapped_function, kwargs_packed, self)
            return func_key in self.func_output_store

        wrapped_function.parallel = parallel
        wrapped_function.serverless_cloud = self
        wrapped_function.full_string_repr = f"FUNCTION REQUIRES {self.requires}, SOURCE {getsource(a_func)}"
        wrapped_function.is_stored = is_stored

        self.functions.append(wrapped_function)

        return wrapped_function