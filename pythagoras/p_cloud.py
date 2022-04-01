import os
import platform
import socket
import sys
from datetime import datetime
from functools import wraps
from getpass import getuser
from random import Random
from inspect import getsource
from typing import Any
from zoneinfo import ZoneInfo

from pythagoras import PValueAddress, PFuncOutputAddress, FileDirDict, KwArgsDict, get_long_infoname, \
    drop_special_chars, SimplePersistentDict


def kw_args(**kwargs):
    """ Helper function to be used with .parallel and similar methods

    It enables simple syntax to simultaneously launch
    many remote instances of a function with different input arguments:

    some_slow_function.sync_parallel(
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

    def __init__(self
                 , requires:str=""
                 , shared_dir_name:str="SharedStorage_P2P_Cloud"
                 , baseline_timezone = ZoneInfo("America/Los_Angeles")
                 , p_purity_checks:float = 0.1
                 ):

        assert not os.path.isfile(shared_dir_name)
        if not os.path.isdir(shared_dir_name):
            os.mkdir(shared_dir_name)
        assert os.path.isdir(shared_dir_name)
        self.base_dir = os.path.abspath(shared_dir_name)
        assert 0 <= p_purity_checks <= 1
        self.p_purity_checks = p_purity_checks

        self.requires = requires # TODO: polish this functionality later
                                 # we need to convert "requires" to some "normal" form to
                                 # prevent syntax variability from impacting hash calculations
        self.functions = []
        self.value_store = FileDirDict(dir_name=os.path.join(self.base_dir, "value_store"))
        self.func_output_store = FileDirDict(dir_name=os.path.join(self.base_dir, "func_output_store"))
        self.baseline_timezone = baseline_timezone
        self.exceptions = FileDirDict(dir_name=os.path.join(self.base_dir, "exceptions"), file_type="json")
        self._event_counter = 0

        self._randomizer = Random()
        """We are using a new instance of Random object that does not share the same seed with other Random objects.
        This is done to ensure correct parallelization via randomization in cases when a cloudized function
        explicitly sets seed value for the default Random object, which it might do in order 
        to be qualified as a pure function."""

        self._old_excepthook =  sys.excepthook

        def cloud_excepthook(exctype, value, traceback):
            self._post_event(event_store = self.exceptions, key=None, event = value)
            self._old_excepthook(exctype, value, traceback)

        sys.excepthook = cloud_excepthook

        # TODO: add handler for exceptions in Jupyter Notebooks
        # Something like get_ipython().set_custom_exc((Exception,), custom_exc)

        self._post_event(event_store=self.exceptions, key=None, event="Finished PCloud creation")


    def push_value(self,value):
        """ Add a value to value_store"""
        key = PValueAddress(value)
        if not key in self.value_store:
            self.value_store[key] = value
        return key

    def _post_event(self, event_store: SimplePersistentDict, key, event: Any):
        """ Add an event to an event store """
        event_id = str(datetime.now(self.baseline_timezone)).replace(":", "-")
        event_id += f"   USER={getuser()}"
        event_id += f"   HOST={socket.gethostname()}"
        event_id += f"   PID={os.getpid()}"
        event_id += f"   PLATFORM={platform.platform()}"
        event_id += f"   EVENT={get_long_infoname(event)}"
        self._event_counter +=1
        if self._event_counter >= 1_000_000_000_000:
            self._event_counter = 1
        event_id += f"   CNTR={self._event_counter}"
        event_id += f"   RNMD={self._randomizer.uniform(0,1)}"
        event_id = drop_special_chars(event_id)

        if key is None:
            key = (event_id,)
        else:
            key = event_store._normalize_key(key) + (event_id,)

        event_store[key] = event


    def add_pure_function(self, a_func):
        assert callable(a_func)

        @wraps(a_func)
        def wrapped_function(**kwargs):
            """compose memoized version of a function"""
            try:

                kwargs_packed = KwArgsDict(kwargs).pack(cloud=self)
                func_key = PFuncOutputAddress(wrapped_function, kwargs_packed, self)

                if self.p_purity_checks == 0:
                    use_cached_output = True
                elif self.p_purity_checks == 1:
                    use_cached_output = False
                else:
                    use_cached_output =  ( self.p_purity_checks < self._randomizer.uniform(0,1) )

                if use_cached_output and func_key in self.func_output_store:
                    result_key = self.func_output_store[func_key]
                    result = self.value_store[result_key]
                else:
                    kwargs_unpacked = KwArgsDict(kwargs).unpack(cloud=self)
                    result = a_func(**kwargs_unpacked)
                    result_key = self.push_value(result)

                    if func_key in self.func_output_store:
                        assert self.func_output_store[func_key] == result_key, (
                            "Stochastic purity check has failed") # TODO: change to a "raise" statement
                    else:
                        self.func_output_store[func_key]=result_key

            except BaseException as ex:
                self._post_event(event_store=self.exceptions, key=None, event=ex)
                raise

            return result

        def sync_parallel(inpt):
            """Enable parallel execution of multiple instances of function"""

            input_list = list(inpt)
            for e in input_list:
                assert isinstance(e,KwArgsDict)
            shuffled_input_list = list(enumerate(input_list))

            self._randomizer.shuffle(shuffled_input_list)

            result = []
            for e in shuffled_input_list:
                func_call_arguments = e[1]
                func_call_output = wrapped_function(**func_call_arguments)
                result_item = (e[0],func_call_output)
                result.append( result_item )

            result = sorted(result, key=lambda t:t[0])
            result = [e[1] for e in result]

            return result

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
    """ Dummy class used in the intro tutorial. Shall be refactored later into a parent class.

    Currently, we are learning from experimenting with P2P_cloud, this is our main focus now.
    PCloud is just a dummy class at this point, used in the tutorial for the sake of simplicity.
    Later, when we know enough to generalize, PCloud will become a base class in the hierarchy
    of cloud classes.
    """

    def __init__(self, requires:str="", shared_dir_name:str="SharedStorage_P2P_Cloud", connection:str=""):
        super().__init__(requires, shared_dir_name)