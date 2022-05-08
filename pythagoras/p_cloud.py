""" Main Pythagoras classes that provide cloud-access functionality.

P_Cloud: base class for Pythagoras clouds.
SharedStorage_P2P_Cloud (inherited from P_Cloud): DIY P2P cloud.
"""

import os
import platform
import socket
import sys
from abc import ABC, abstractmethod
from datetime import datetime
from functools import wraps
from getpass import getuser
from random import Random
from inspect import getsource
import traceback
from typing import Any, Optional, Callable, List, Union
from zoneinfo import ZoneInfo


from pythagoras.p_hash_address import PValueAddress, PFuncOutputAddress, KwArgsDict
from pythagoras.dicts import FileDirDict, SimplePersistentDict, SimpleDictKey
from pythagoras.utils import get_long_infoname, replace_unsafe_chars
from pythagoras.utils import buid_context, ABC_PostInitializable


class ExceptionInfo:
    """ Helper class for remote logging, encapsulates exception/environment info.

    This class is used by P_Cloud objects to log information
    in P_Cloud.exception persistent store.
    """

    def __init__(self, exc_type, exc_value, trace_back, path, time_zone):
        assert isinstance(exc_value, BaseException)
        self.__name__ = get_long_infoname(exc_value)
        self.exception = exc_value
        self.exception_description = traceback.format_exception(
            exc_type, exc_value, trace_back)
        self.context = buid_context(path, time_zone)

def kw_args(**kwargs) -> KwArgsDict:
    """ Helper function to be used with .sync_parallel and similar methods

    It enables simple syntax to simultaneously launch
    many remote instances of a function with different input arguments:

    some_slow_function.sync_parallel(
        kw_args(arg1=i, arg2=j) for i in range(100) for j in range(15)  )
    """
    return KwArgsDict(**kwargs)


class P_Cloud(metaclass=ABC_PostInitializable):
    """ A base class for all Pythagoras clouds.

    It is a base class for all objects that are implementing
    Pythagoras Abstraction Model:
    https://docs.google.com/document/d/1lgNOaRcZNGvW4wF894s7KmIWjhLX2cDVM_15a4lE02Y

    Attributes
    ----------
    value_store : SimplePersistentDict
            An abstract property: a persistent dict-like object that
            stores all the values ever created within any running instance
            of cloudized functions. It's a key-value store, where
            the key (the object's address) is composed using
            the object's hash. Under the hood, these hash-based addresses
            are used by Pythagoras the same way as RAM-based addresses
            are used (via pointers and references) in C and C++ programs.

    func_output_store : SimplePersistentDict
            An abstract property: a persistent dict-like object that
            caches all results of all cloudized function executions
            that ever happened in the system. Enables distributed
            memoization functionality ("calculate once, reuse
            forever").

    exception_log: SimplePersistentDict
            An abstract property: a persistent dict-like object that
            stores a complete history of all the exceptions
            (catastrophic events) that terminated execution of any of
            the scripts/notebooks that had instantiated the P_Cloud class.
            The log is stored in human-readable json format.
            The main purpose of the property is to improve
            transparency/debuggability of the code that uses P_Cloud.
            This property is not intended to be used as a messaging tool
            that enables automated response to detected exceptions.

    event_log: SimplePersistentDict
            An abstract property: a persistent dict-like object that
            serves as a log of various non-catastrophic events, recorded by any
            of the scripts/notebooks that had instantiated the P_Cloud class.
            The log is stored in human-readable json format.
            The main purpose of the property is to
            improve transparency/debuggability of the code that uses P_Cloud.
            This property is not intended to be used as a messaging tool
            that enables communication between various components of the code.

    p_purity_checks : float
            Probability of stochastic purity checks. If a functions
            output has been stored on a cache, when the function is
            called with the same arguments next time, it will re-use
            cached output with probability (1-p_purity_checks).
            With probability p_purity_checks the function will be
            executed once again, and its output will be compared with
            the cached one: if they differ, purity check will fail.

    original_functions : dict[str, Callable]
            A dictionary with original (before application of the
            @add_pure_function decorator) versions of all cloudized
            functions in P_Cloud. Keys are the names of the
            functions.

    cloudized_functions : dict[str, Callable]
            A dictionary with modified (as a result of  applying
            the @add_pure_function decorator) versions of all
            cloudized functions in P_Cloud. Keys are the names
            of the functions.
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
    its seed with other Random objects.
    This is done to ensure correct parallelization via randomization 
    in cases when a cloudized function explicitly sets seed value 
    for the default Random object, which it might do in order 
    to be qualified as a pure function."""

    _event_counter:int = 0

    _instance_counter:int = 0
    _init_signature_hash_address = None

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

    def __post__init__(self, *args, **kwargs) -> None:
        """ Enforce arguments-based singleton pattern. """
        P_Cloud._instance_counter += 1
        if P_Cloud._instance_counter == 1:
            init_signature  = (type(self),args,kwargs)
            P_Cloud._init_signature_hash_address = PValueAddress(
                init_signature)
        else:
            new_init_signature = (type(self),args,kwargs)
            new_init_sign_hash = PValueAddress(new_init_signature)
            assert new_init_sign_hash == P_Cloud._init_signature_hash_address, (
                "You can't have several P_Cloud instances with different "
                "types and/or initialization arguments.")

    def _register_exception_handlers(self) -> None:
        """ Intersept & redirect unhandled exceptions to self.exceptions """

        P_Cloud._old_excepthook = sys.excepthook

        def cloud_excepthook(exc_type, exc_value, trace_back):

            exc_event = ExceptionInfo(
                exc_type, exc_value
                , trace_back
                , self.base_dir
                , self.baseline_timezone)

            self._post_event(
                event_store=self.exception_log, key=None, event=exc_event)

            P_Cloud._old_excepthook(exc_type, exc_value, trace_back)
            return

        sys.excepthook = cloud_excepthook

        def cloud_excepthandler(
                other_self
                , exc_type
                , exc_value
                , trace_back
                , tb_offset=None):

            exc_event = ExceptionInfo(
                exc_type
                , exc_value
                , trace_back
                , self.base_dir
                , self.baseline_timezone)

            self._post_event(
                event_store=self.exception_log, key=None, event=exc_event)

            traceback.print_exception(exc_type, exc_value, trace_back)
            return

        try:  # if we are inside a notebook
            get_ipython().set_custom_exc(
                (BaseException,), cloud_excepthandler)
            self._is_running_inside_IPython = True
        except:
            self._is_running_inside_IPython = False


    @property
    @abstractmethod
    def value_store(self) -> SimplePersistentDict:
        """ A persistent dict-like object that stores all ever created values.

        It's a key-value store, where the key (the object's address)
        is composed using the object's hash. Under the hood, these
        hash-based addresses are used by Pythagoras the same way
        as RAM-based addresses are used (via pointers and references)
        in C and C++ programs.
        """
        raise NotImplementedError


    @property
    @abstractmethod
    def func_output_store(self) -> SimplePersistentDict:
        """Persistent cache that keeps execution results for cloudized functions.

        It's a dict-like store that enables persistent / distributed
        memoization functionality ("calculate once, reuse forever").
        """
        raise NotImplementedError


    @property
    @abstractmethod
    def exception_log(self) -> SimplePersistentDict:
        """Persistent store that keeps history of all catastrophic events.

        A catastrophic event is defined as an exception that
        terminated execution of any of the scripts/notebooks which
        had instantiated the P_Cloud class.
        The log is stored in human-readable json format.
        The main purpose of the property is to improve
        transparency/debuggability of the code that uses P_Cloud.
        This property is not intended to be used as a messaging tool
        that enables automated response to detected exceptions.
        """
        raise NotImplementedError


    @property
    @abstractmethod
    def func_snapshots(self) -> SimplePersistentDict:
        raise NotImplementedError


    @property
    @abstractmethod
    def event_log(self) -> SimplePersistentDict:
        """ A log of various non-catastrophic events.

        The events can be recorded by any of the scripts/notebooks
        that had instantiated the P_Cloud class.
        The log is stored in human-readable json format.
        The main purpose of the property is to
        improve transparency/debuggability of the code that uses P_Cloud.
        This property is not intended to be used as a messaging tool
        that enables communication between various components of the code.
        """
        raise NotImplementedError


    def push_value(self, value:Any) -> PValueAddress:
        """ Add a value to value_store"""

        key = PValueAddress(value)
        if not key in self.value_store:
            self.value_store[key] = value
        return key

    def _post_event(self
                    , event_store: SimplePersistentDict
                    , key:Optional[SimpleDictKey]
                    , event: Any
                    ) -> None:
        """ Add an event to an event store. """

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
        event_id = replace_unsafe_chars(event_id,"_")

        if key is None:
            key = (event_id,)
        else:
            key = event_store._normalize_key(key) + (event_id,)

        event_store[key] = event


    def local_function_call(self, func_name:str, **kwargs) -> Any:
        """ Perform a local synchronous call for a cloudized function.

        This method should not be called directly. Instead,
        use the traditional syntax below while caling a cloudized function:
        func_name(**kwargs)
        """

        #TODO: See if we still need try/except here
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
            self._post_event(event_store=self.exception_log, key=None, event=ex)
            raise

        return result


    def sync_remote_function_call(self, func_name:str, **kwargs) -> Any:
        """ Perform a remote synchronous call for a cloudized function.

        This method should not be called directly. Instead, use the syntax
        below (requires a functions first to be added to a cloud):
        func_name.sync_remote(**kwargs)
        """
        raise NotImplementedError


    def async_remote_function_call(self, func_name: str, **kwargs) -> Any:
        """ Perform a remote asynchronous call for a cloudized function.

        This method should not be called directly. Instead, use the syntax
        below (requires a functions first to be added to a cloud):
        func_name.async_remote(**kwargs)
        """
        raise NotImplementedError


    def sync_parallel_function_call(self
                                    , func_name: str
                                    , all_kwargs:List[KwArgsDict]
                                    ) -> List[Any]:
        """Synchronously execute multiple instances of a cloudized function.

        This method should not be called directly. Instead, use the syntax
        below (requires a functions first to be added to a cloud):
        func_name.sync_parallel( kw_args(..) for .. in .. )
        """

        raise NotImplementedError


    def async_parallel_function_call(self
                                     , func_name: str
                                     , all_kwargs:List[KwArgsDict]
                                     ) -> List[Any]:
        """Asynchronously execute multiple instances of a cloudized function.

        This function should not be called directly. Instead, use the syntax
        below (requires a functions first to be added to a cloud):
        func_name.async_parallel( kw_args(..) for .. in .. )
        """
        raise NotImplementedError


    def check_if_func_output_is_stored(self
                                       , func_name: str
                                       , **kwargs
                                       ) -> bool:
        """Check if function output for the arguments has already been cached.

        This function should not be called directly. Instead, use the syntax
        below (requires a functions first to be added to a cloud):
        func_name.is_stored(**kwargs)
        """
        cloudized_function = self.cloudized_functions[func_name]
        kwargs_packed = KwArgsDict(kwargs).pack(cloud=self)
        func_key = PFuncOutputAddress(cloudized_function, kwargs_packed)
        return func_key in self.func_output_store


    def add_pure_function(self, a_func):
        """Decorator which 'cloudizes' user-provided functions. """
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
            """Run memoized/cloudized version of a function"""
            return self.local_function_call(a_func.__name__, **kwargs)

        def sync_parallel(inpt):
            """Synchronously run multiple instances of function"""
            return self.sync_parallel_function_call(a_func.__name__, inpt)

        def async_parallel(inpt):
            """Asynchronously run multiple instances of function"""
            return self.async_parallel_function_call(a_func.__name__, inpt)

        def async_remote(**kwargs):
            """Perform asynchronous remote execution of a function"""
            return self.async_remote_function_call(a_func.__name__, **kwargs)

        def sync_remote(**kwargs):
            """Perform synchronous remote execution of a function"""
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

        self._exception_log = FileDirDict(
            dir_name=os.path.join(self.base_dir, "exception_log")
            ,file_type="json")

        self._func_snapshots = FileDirDict(
            dir_name=os.path.join(self.base_dir, "func_snapshots")
            ,file_type="json")

        self._event_log = FileDirDict(
            dir_name=os.path.join(self.base_dir, "event_log")
            ,file_type="json")


    @property
    def value_store(self) -> SimplePersistentDict:
        """ A persistent dict-like object that stores all ever created values.

        It's a key-value store, where the key (the object's address)
        is composed using the object's hash. Under the hood, these
        hash-based addresses are used by Pythagoras the same way
        as RAM-based addresses are used (via pointers and references)
        in C and C++ programs.
        """
        return self._value_store


    @property
    def func_output_store(self) -> SimplePersistentDict:
        """Persistent cache that keeps execution results for cloudized functions.

        It's a dict-like store that enables persistent / distributed
        memoization functionality ("calculate once, reuse forever").
        """
        return self._func_output_store


    @property
    def exception_log(self) -> SimplePersistentDict:
        """Persistent store that keeps history of all catastrophic events.

        A catastrophic event is defined as an exception that
        terminated execution of any of the scripts/notebooks which
        had instantiated the P_Cloud class.
        The log is stored in human-readable json format.
        The main purpose of the property is to improve
        transparency/debuggability of the code that uses P_Cloud.
        This property is not intended to be used as a messaging tool
        that enables automated response to detected exceptions.
        """
        return self._exception_log


    @property
    def func_snapshots(self) -> SimplePersistentDict:
        return self._func_snapshots


    @property
    def event_log(self) -> SimplePersistentDict:
        """ A log of various non-catastrophic events.

        The events can be recorded by any of the scripts/notebooks
        that had instantiated the P_Cloud class.
        The log is stored in human-readable json format.
        The main purpose of the property is to
        improve transparency/debuggability of the code that uses P_Cloud.
        This property is not intended to be used as a messaging tool
        that enables communication between various components of the code.
        """
        return self._event_log

    def sync_remote_function_call(self
                                  , func_name: str
                                  , **kwargs
                                  ) -> Any:
        """Emulate synchronous remote execution of a function.

        Instead of actual remote execution, it performs local one.
        """

        return self.local_function_call(func_name, **kwargs)

    def sync_parallel_function_call(self
                                    , func_name: str
                                    , all_kwargs:List[KwArgsDict]
                                    ) -> Any:
        """Emulate parallel execution of multiple instances of function.

        Instead of actual remote parallel execution,
        it performs local sequential randomized execution .
        """

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

class MLProjectWorkspace:
    """Simple shared workspace for small teams working on ML projects.

    Objects of this class enable faster experimentation and
    more efficient collaboration for small teams working on ML projects,
    e.g. teams participating in Kaggle competitions.

    MLProjectWorkspace also provides API similar to P_Cloud objects,
    even though MLProjectWorkspace does not inherit from P_Cloud
    """

    base_cloud: P_Cloud

    def __init__(self, base: Union[str, P_Cloud]):
        if isinstance(base, str):
            self.base_cloud = SharedStorage_P2P_Cloud(base_dir=base)
        elif isinstance(base, P_Cloud):
            self.base_cloud = base
        else:
            assert False, "base must be either str or P_Cloud"
            # TODO: chaneg to exception

    @property
    def value_store(self) -> SimplePersistentDict:
        """ A persistent dict-like object that stores all ever created values.

        It's a key-value store, where the key (the object's address)
        is composed using the object's hash. Under the hood, these
        hash-based addresses are used by Pythagoras the same way
        as RAM-based addresses are used (via pointers and references)
        in C and C++ programs.
        """
        return self.base_cloud.value_store


    @property
    def func_output_store(self) -> SimplePersistentDict:
        """Persistent cache that keeps execution results for cloudized functions.

        It's a dict-like store that enables persistent / distributed
        memoization functionality ("calculate once, reuse forever").
        """
        return self.base_cloud.func_output_store


    @property
    def exception_log(self) -> SimplePersistentDict:
        """Persistent store that keeps history of all catastrophic events.

        A catastrophic event is defined as an exception that
        terminated execution of any of the scripts/notebooks which
        had instantiated the P_Cloud class.
        The log is stored in human-readable json format.
        The main purpose of the property is to improve
        transparency/debuggability of the code that uses P_Cloud.
        This property is not intended to be used as a messaging tool
        that enables automated response to detected exceptions.
        """
        return self.base_cloud.exception_log


    @property
    def func_snapshots(self) -> SimplePersistentDict:
        return self.base_cloud.func_snapshots


    @property
    def event_log(self) -> SimplePersistentDict:
        """ A log of various non-catastrophic events.

        The events can be recorded by any of the scripts/notebooks
        that had instantiated the P_Cloud class.
        The log is stored in human-readable json format.
        The main purpose of the property is to
        improve transparency/debuggability of the code that uses P_Cloud.
        This property is not intended to be used as a messaging tool
        that enables communication between various components of the code.
        """
        return self.base_cloud.event_log


    @property
    def p_purity_checks(self) -> float:
        """ Probability of stochastic purity checks.

        If a functions output has been stored on a cache, when the function is
        called with the same arguments next time, it will re-use
        cached output with probability (1-p_purity_checks).
        With probability p_purity_checks the function will be
        executed once again, and its output will be compared with
        the cached one: if they differ, purity check will fail.
        """
        return self.base_cloud.p_purity_checks

    def add_pure_function(self, a_func):
        """Decorator which 'cloudizes' user-provided functions. """
        return self.base_cloud.add_pure_function(a_func)