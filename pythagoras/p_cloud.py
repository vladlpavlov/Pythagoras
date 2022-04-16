import os
import platform
import socket
import sys
from abc import ABC, abstractmethod
from datetime import datetime
from functools import wraps
from getpass import getuser
from pprint import pprint
from random import Random
from inspect import getsource
import traceback
from typing import Any, Optional, Callable, List
from zoneinfo import ZoneInfo


from pythagoras.p_hash_address import PValueAddress, PFuncOutputAddress, KwArgsDict
from pythagoras.dicts import FileDirDict, SimplePersistentDict, SimpleDictKey
from pythagoras.utils import get_long_infoname, replace_special_chars, buid_context


class ExceptionInfo:
    """ Helper class for remote logging, encapsulates exception/environment info."""

    def __init__(self, exc_type, exc_value, trace_back, path, time_zone):
        assert isinstance(exc_value, BaseException)
        self.__name__ = get_long_infoname(exc_value)
        self.exception = exc_value
        self.exception_description = traceback.format_exception(
            exc_type,exc_value, trace_back)
        self.context = buid_context(path,time_zone)

def kw_args(**kwargs) -> KwArgsDict:
    """ Helper function to be used with .sync_parallel and similar methods

    It enables simple syntax to simultaneously launch
    many remote instances of a function with different input arguments:

    some_slow_function.sync_parallel(
        kw_args(arg1=i, arg2=j) for i in range(100) for j in range(15)  )
    """
    return KwArgsDict(**kwargs)


class P_Cloud(ABC):
    """ A base class for all Pythagoras clouds.

     It is a base class for all objects that are implementing
     Pythagoras Abstraction Model:
     https://docs.google.com/document/d/1lgNOaRcZNGvW4wF894s7KmIWjhLX2cDVM_15a4lE02Y

     """
    p_cloud_single_instance = None

    install_requires: Optional[str] = None
    python_requires: Optional[str] = None

    original_functions: dict[str, Callable] = dict()
    cloudized_functions: dict[str, Callable] = dict()

    p_purity_checks:float = 0.1

    baseline_timezone = ZoneInfo("America/Los_Angeles")

    _old_excepthook: Optional[Callable] = None
    _is_running_inside_IPython: Optional[bool] = None
    _randomizer:Random = Random()
    """We are using a new instance of Random object that does not share 
    the same seed with other Random objects.
    This is done to ensure correct parallelization via randomization 
    in cases when a cloudized function explicitly sets seed value 
    for the default Random object, which it might do in order 
    to be qualified as a pure function."""

    _event_counter:int = 0

    def __init__(self
                 , install_requires:str = ""
                 , python_requires = ""
                 , base_dir = "P_Cloud"
                 , p_purity_checks = 0.1
                 , **kwargs):

        self.install_requires = install_requires  # TODO: polish later
        self.python_requires = python_requires  # TODO: polish later

        assert not os.path.isfile(base_dir)
        if not os.path.isdir(base_dir):
            os.mkdir(base_dir)
        assert os.path.isdir(base_dir)
        self.base_dir = os.path.abspath(base_dir)

        assert 0 <= p_purity_checks <= 1
        self.p_purity_checks = p_purity_checks

        self._register_exception_handlers()


    def _register_exception_handlers(self):

        self._old_excepthook = sys.excepthook

        def cloud_excepthook(exc_type, exc_value, trace_back):
            exc_event = ExceptionInfo(exc_type, exc_value, trace_back, self.base_dir, self.baseline_timezone)
            self._post_event(event_store=self.exceptions, key=None, event=exc_event)
            self._old_excepthook(exc_type, exc_value, trace_back)
            return

        sys.excepthook = cloud_excepthook

        def cloud_excepthandler(other_self, exc_type, exc_value, trace_back, tb_offset=None):
            exc_event = ExceptionInfo(exc_type, exc_value, trace_back, self.base_dir, self.baseline_timezone)
            self._post_event(event_store=self.exceptions, key=None, event=exc_event)
            traceback.print_exception(exc_type, exc_value, trace_back)
            return

        try:  # if we are inside a notebook
            get_ipython().set_custom_exc((BaseException,), cloud_excepthandler)
            self._is_running_inside_IPython = True
        except:
            self._is_running_inside_IPython = False


    @property
    @abstractmethod
    def value_store(self) -> SimplePersistentDict:
        raise NotImplementedError


    @property
    @abstractmethod
    def func_output_store(self) -> SimplePersistentDict:
        raise NotImplementedError


    @property
    @abstractmethod
    def exceptions(self) -> SimplePersistentDict:
        raise NotImplementedError


    @property
    @abstractmethod
    def func_snapshots(self) -> SimplePersistentDict:
        raise NotImplementedError


    @property
    @abstractmethod
    def events(self) -> SimplePersistentDict:
        raise NotImplementedError


    def push_value(self, value:Any) -> PValueAddress:
        """ Add a value to value_store"""
        key = PValueAddress(value)
        if not key in self.value_store:
            self.value_store[key] = value
        return key

    def _post_event(self, event_store: SimplePersistentDict, key:Optional[SimpleDictKey], event: Any):
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
        event_id = replace_special_chars(event_id)

        if key is None:
            key = (event_id,)
        else:
            key = event_store._normalize_key(key) + (event_id,)

        event_store[key] = event


    def local_function_call(self, func_name:str, **kwargs) -> Any:
        try:
            original_function = self.original_functions[func_name]
            cloudized_function = self.cloudized_functions[func_name]

            kwargs_packed = KwArgsDict(kwargs).pack(cloud=self)
            func_key = PFuncOutputAddress(cloudized_function, kwargs_packed)

            if self.p_purity_checks == 0:
                use_cached_output = True
            elif self.p_purity_checks == 1:
                use_cached_output = False
            else:
                use_cached_output = (
                        self.p_purity_checks < self._randomizer.uniform(0, 1))

            if use_cached_output and func_key in self.func_output_store:
                result_key = self.func_output_store[func_key]
                result = self.value_store[result_key]
            else:
                kwargs_unpacked = KwArgsDict(kwargs).unpack(cloud=self)
                result = original_function(**kwargs_unpacked)
                result_key = self.push_value(result)

                if func_key in self.func_output_store:
                    # TODO: change to a "raise" statement
                    assert self.func_output_store[func_key] == result_key, (
                        "Stochastic purity check has failed")
                else:
                    self.func_output_store[func_key] = result_key

        except BaseException as ex:
            self._post_event(event_store=self.exceptions, key=None, event=ex)
            raise

        return result


    def sync_remote_function_call(self, func_name:str, **kwargs) -> Any:
        raise NotImplementedError


    def async_remote_function_call(self, func_name: str, **kwargs) -> Any:
        raise NotImplementedError


    def remote_function_call(self
                             , mode:str
                             , func_name: str
                             , **kwargs
                             ) -> Any:
        assert mode in {"sync", "async"}
        if mode == "sync":
            return self.sync_remote_function_call(func_name, **kwargs)
        else:
            return self.async_remote_function_call(func_name, **kwargs)


    def sync_parallel_function_call(self
                                    , func_name: str
                                    , all_kwargs:List[KwArgsDict]
                                    ) -> List[Any]:
        raise NotImplementedError


    def async_parallel_function_call(self
                                     , func_name: str
                                     , all_kwargs:List[KwArgsDict]
                                     ) -> List[Any]:
        raise NotImplementedError


    def parallel_function_call(self, mode:str
                               , func_name: str
                               , all_kwargs:List[KwArgsDict]
                               ) -> Any:
        assert mode in {"sync", "async"}
        if mode == "sync":
            return self.sync_parallel_function_call(func_name, all_kwargs)
        else:
            return self.async_parallel_function_call(func_name, all_kwargs)


    def check_if_func_output_is_stored(self
                                       , func_name: str
                                       , **kwargs
                                       ) -> bool:
        """Check if function output for the arguments has already been cached"""
        cloudized_function = self.cloudized_functions[func_name]
        kwargs_packed = KwArgsDict(kwargs).pack(cloud=self)
        func_key = PFuncOutputAddress(cloudized_function, kwargs_packed)
        return func_key in self.func_output_store


    def add_pure_function(self, a_func):
        assert callable(a_func)
        assert not hasattr(a_func, "p_cloud"), (
            "A function is not allowed to be added to the cloud twice")
        assert hasattr(a_func,"__name__"), (
            "Nameless functions can not be cloudized")
        assert a_func.__name__ != "<lambda>", (
            "Lambda dunctions can not be cloudized")

        # TODO: change to custom exception
        assert a_func.__name__ not in self.original_functions, (
            f"Function {a_func.__name__} has already been added to the cloud."
            + "Can't add one more time.")

        self.original_functions[a_func.__name__] = a_func

        @wraps(a_func)
        def wrapped_function(**kwargs):
            """compose memoized/cloudized version of a function"""
            return self.local_function_call(a_func.__name__, **kwargs)

        def sync_parallel(inpt):
            """Enable parallel execution of multiple instances of function"""
            return self.sync_parallel_function_call(a_func.__name__, inpt)

        def async_parallel(inpt):
            return self.async_parallel_function_call(a_func.__name__, inpt)

        def async_remote(**kwargs):
            return self.async_remote_function_call(a_func.__name__, **kwargs)

        def sync_remote(**kwargs):
            return self.sync_remote_function_call(a_func.__name__, **kwargs)

        def is_stored(**kwargs):
            """Check if function output for the arguments has already been cached"""
            return self.check_if_func_output_is_stored(a_func.__name__, **kwargs)

        wrapped_function.sync_parallel = sync_parallel
        wrapped_function.async_parallel = async_parallel
        wrapped_function.sync_remote = sync_remote
        wrapped_function.async_remote = async_remote
        wrapped_function.p_cloud = self
        wrapped_function.original_source = getsource(a_func)
        wrapped_function.is_stored = is_stored

        # TODO: change to custom exception
        assert wrapped_function.__name__ not in self.cloudized_functions, (
            f"Function {wrapped_function.__name__} has already been added "
            + "to the cloud. Can't add one more time.")

        self.cloudized_functions[wrapped_function.__name__] = wrapped_function

        return wrapped_function


class SharedStorage_P2P_Cloud(P_Cloud):
    """ Simple P2P cloud based on using a shared folder (via Dropbox, NFS, etc.)

    Allows to distribute an execution of a program via multiple computers
    that share the same file folder. The program must be launched
    on every computer with shared_dir_name parameter of their
    SharedStorage_P2P_Cloud object pointing to the same shared folder.
    Execution of parallelized calls ( function.sync_parallel(...) )
    will be distributed between participating computers.
    Execution of all other calls will be redundantly carried
    on each participating computer.
    """

    def __init__(self
                 , install_requires:str=""
                 , python_requires = ""
                 , base_dir = "SharedStorage_P2P_Cloud"
                 , p_purity_checks=0.1
                 , *kwargs
                 ):
        super().__init__(install_requires = install_requires
                         , python_requires = python_requires
                         , base_dir = base_dir
                         , p_purity_checks = p_purity_checks)

        self._value_store = FileDirDict(
            dir_name=os.path.join(self.base_dir, "value_store")
            ,file_type="pkl")

        self._func_output_store = FileDirDict(
            dir_name=os.path.join(self.base_dir, "func_output_store")
            ,file_type="pkl")

        self._exceptions = FileDirDict(
            dir_name=os.path.join(self.base_dir, "exceptions")
            ,file_type="json")

        self._func_snapshots = FileDirDict(
            dir_name=os.path.join(self.base_dir, "func_snapshots")
            ,file_type="json")

        self._events = FileDirDict(
            dir_name=os.path.join(self.base_dir, "events")
            ,file_type="json")


    @property
    def value_store(self) -> SimplePersistentDict:
        return self._value_store


    @property
    def func_output_store(self) -> SimplePersistentDict:
        return self._func_output_store


    @property
    def exceptions(self) -> SimplePersistentDict:
        return self._exceptions


    @property
    def func_snapshots(self) -> SimplePersistentDict:
        return self._func_snapshots


    @property
    def events(self) -> SimplePersistentDict:
        return self._events

    def sync_remote_function_call(self
                                  , func_name: str
                                  , **kwargs
                                  ) -> Any:
        return self.local_function_call(func_name, **kwargs)

    def sync_parallel_function_call(self
                                    , func_name: str
                                    , all_kwargs:List[KwArgsDict]
                                    ) -> Any:
        """Enable parallel execution of multiple instances of function"""

        cloudized_function = self.cloudized_functions[func_name]

        input_list = list(all_kwargs)
        for e in input_list:
            assert isinstance(e, KwArgsDict)

        shuffled_input_list = list(enumerate(input_list))
        self._randomizer.shuffle(shuffled_input_list)

        result = []
        for e in shuffled_input_list:
            func_call_arguments = e[1]
            func_call_output = cloudized_function(**func_call_arguments)
            result_item = (e[0], func_call_output)
            result.append(result_item)

        result = sorted(result, key=lambda t: t[0])
        result = [e[1] for e in result]

        return result