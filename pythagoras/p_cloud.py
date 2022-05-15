""" Main Pythagoras classes that provide cloud-access functionality.

P_Cloud: base class for Pythagoras clouds.
SharedStorage_P2P_Cloud (inherited from P_Cloud): DIY P2P cloud.
"""
from __future__ import annotations

import os
import platform
import socket
import sys
import uuid
from abc import ABC, abstractmethod, ABCMeta
from collections.abc import Sequence
from copy import deepcopy
from datetime import datetime
from functools import wraps
from getpass import getuser
from random import Random
from inspect import getsource
import traceback
from typing import Any, Optional, Callable, List, Union, Dict
from zoneinfo import ZoneInfo
from joblib.hashing import NumpyHasher, Hasher

from pythagoras._dependency_discovery import _all_dependencies_one_func
from pythagoras.persistent_dicts import FileDirDict, SimplePersistentDict, SimpleDictKey
from pythagoras.utils import get_long_infoname, replace_unsafe_chars
from pythagoras.utils import buid_context, ABC_PostInitializable


def kw_args(**kwargs) -> KwArgsDict:
    """ Helper function to be used with .sync_parallel and similar methods

    It enables simple syntax to simultaneously launch
    many remote instances of a function with different input arguments:

    some_slow_function.sync_parallel(
        kw_args(arg1=i, arg2=j) for i in range(100) for j in range(15)  )
    """
    return KwArgsDict(**kwargs)


class PCloudizedFunction:
    """ An API for various execution modes for cloudized functions."""

    original_name:str
    cloud:P_Cloud_Implementation
    original_function:Callable
    original_annotations:Dict
    original_source:str
    func_snapshot_address:Optional[PFuncSnapshotAddress]
    _original_source_with_dependencies:Optional[str]

    def __init__(
            self
            , cloud:P_Cloud_Implementation
            , function_name:str
            ):
        self.cloud = cloud
        self.original_name = self.__name__ = function_name
        original_function = cloud.original_functions[function_name]
        original_annotations = dict()
        if hasattr(original_function, "__annotations__"):
            original_annotations = deepcopy(original_function.__annotations__)
        if "self" in original_annotations:
            #TODO: Should we issue a warning here? Or raise an exception?
            del original_annotations["self"]
        self.original_source = getsource(original_function)
        self.func_snapshot_address = None
        self._original_source_with_dependencies = None
        # self.__call__.__annotations__ = deepcopy(original_annotations)
        # self.sync_remote.__annotations__ = deepcopy(original_annotations)
        # self.async_remote.__annotations__ = deepcopy(original_annotations)
        # self.async_remote.__annotations__['return'] = PFuncOutputAddress
        self.__doc__ = original_function.__doc__
        #TODO: fully mimic functools.update_wrapper for all 5 execution methods


    def __call__(self,**kwargs) -> Any:
        """Locally run memoized/cloudized version of a function"""
        address = self.cloud.local_function_call(
            self.__name__, KwArgsDict(**kwargs))
        return self.cloud.get_func_output(address)


    def sync_remote(self, **kwargs) -> Any:
        """Perform synchronous remote execution of a function"""
        address = self.cloud.sync_remote_function_call(
            self.__name__, KwArgsDict(**kwargs))
        return self.cloud.get_func_output(address)


    def async_remote(self, **kwargs) -> PFuncOutputAddress:
        """Perform asynchronous remote execution of a function"""
        address = self.cloud.async_remote_function_call(
            self.__name__, KwArgsDict(**kwargs))
        return address


    def sync_parallel(self
                      ,argslist:List[KwArgsDict]
                      ) -> List[Any]:
        """Synchronously run multiple instances of function"""
        addresses = self.cloud.sync_parallel_function_call(
            self.__name__, argslist)
        return [self.cloud.get_func_output(a) for a in addresses]


    def async_parallel(self
                       ,argslist:List[KwArgsDict]
                       ) -> List[PFuncOutputAddress]:
        """Asynchronously run multiple instances of function"""
        addresses = self.cloud.sync_parallel_function_call(
            self.__name__, argslist)
        return addresses


    def is_output_available(self, **kwargs):
        """Check if function output for the arguments has already been cached"""
        return self.cloud.check_if_func_output_is_available(
            self.__name__, KwArgsDict(**kwargs))


    @property
    def original_source_with_dependencies(self) -> str:
        """Lazily construct a list of function dependencies within a cloud.

         Returns a string containing source code for the cloudized function
         and all other cloudized functions (from the same P_Cloud)
         that the function depends on.

         Returned functions are sorted in alphabetical order by their names.
         """
        if self._original_source_with_dependencies is not None:
            return self._original_source_with_dependencies

        dependencies = _all_dependencies_one_func(
            self.__name__, self.cloud.cloudized_functions)
        dependencies = sorted(dependencies)
        self._original_source_with_dependencies = ""

        for f in dependencies:
            self._original_source_with_dependencies += (
                    self.cloud.cloudized_functions[f].original_source + "\n\n")

        return self._original_source_with_dependencies


class PCloudizedFunctionSnapshot:
    """ Information about a specific version of a cloudized function.

    Objects of this class contain full information, needed to restore
    from scratch a specific version of a cloudized function
    in a cloud-independent way. They are used to store and
    exchange functions between different instances of P_Cloud.
    """

    def __init__(self, f:PCloudizedFunction):
        assert isinstance(f,PCloudizedFunction)
        self.__name__ = f.__name__
        self.install_requires = f.cloud.install_requires
        self.python_requires = f.cloud.python_requires
        self.source = f.original_source
        self.source_with_dependencies = f.original_source_with_dependencies


class PHashAddress(Sequence):
    """A globally unique address, includes a human-readable prefix and a hash."""

    prefix: str
    hash_id: str
    _hash_type: str = "sha256"

    @staticmethod
    def _build_prefix(x: Any) -> str:
        """Create a short human-readable summary of an object."""

        prfx = get_long_infoname(x)

        if (hasattr(x, "shape")
                and hasattr(x.shape, "__iter__")
                and callable(x.shape.__iter__)
                and not callable(x.shape)):

            prfx += "_shape_"
            for n in x.shape:
                prfx += str(n) + "_x_"
            prfx = prfx[:-3]

        elif (hasattr(x, "__len__")
              and callable(x.__len__)):
            prfx += "_len_" + str(len(x))

        clean_prfx = replace_unsafe_chars(prfx, "_")

        return clean_prfx

    @staticmethod
    def _build_hash_id(x: Any) -> str:
        """Create a URL-safe hashdigest for an object."""

        if 'numpy' in sys.modules:
            hasher = NumpyHasher(hash_name=PHashAddress._hash_type)
        else:
            hasher = Hasher(hash_name=PHashAddress._hash_type)
        return hasher.hash(x) #TODO: switch to Base32


    def __eq__(self, other) -> bool:
        """Return self==other. """
        return ( isinstance(other, self.__class__)
                and self.prefix  == other.prefix
                and self.hash_id == other.hash_id )

    def __ne__(self, other) -> bool:
        """Return self!=other. """
        return not self.__eq__(other)


    def __len__(self) -> int:
        """Return len(self), always equals to 2. """
        return 2


    def __getitem__(self, item):
        """""X.__getitem__(y) is an equivalent to X[y]"""
        if item == 0:
            return self.prefix
        elif item == 1:
            return self.hash_id
        else:
            raise IndexError("PHashAddress only has 2 items.")


    @abstractmethod
    def __repr__(self):
        raise NotImplementedError


class PValueAddress(PHashAddress):
    """A globally unique address of an immutable value: a prefix + a hash code.

    PValueAddress is a universal global identifier of any (constant) value.
    Using only the value's hash should (theoretically) be enough to
    uniquely address all possible data objects that the humanity  will create
    in the foreseeable future (see, for example ipfs.io).

    However, an address also includes a prefix. It makes it more easy
    for humans to interpret an address, and further decreases collision risk.
    """

    def __init__(self, x: Any):
        if isinstance(x, PValueAddress):
            self.prefix = x.prefix
            self.hash_id = x.hash_id
        else:
            assert not isinstance(x,PHashAddress), (
                "PValueAddress is the only PHashAddress which is allowed "
                +"to be converted to PValueAddress")
            self.prefix = self._build_prefix(x)
            self.hash_id = self._build_hash_id(x)

    def __repr__(self):
        return f"ValueAddress( prefix={self.prefix} , hash_id={self.hash_id} )"


class PFuncSnapshotAddress(PHashAddress):
    """ Globally unique address of a function snapshot (version).

    PFuncSnapshotAddress is a universal global identifier of a function.
    It contains a hash value for the cloudized function's source code,
    combined with the source code of all other cloudized functions that
    the function is using, as well as its "requires" lists
    (a list of required modules with their versions, and Python version).
    A change in the source code, or a change in the "requires" lists
    (python_requires or install_requires) results in the
    creation of a new hash (hence, a new address).

    An address also includes a prefix, which makes it more simple
    for humans to interpret an address,
    and further decreases collision risk.

    The first time a new PFuncSnapshotAddress is created,
    it writes a new entry to P_Cloud.function_snapshots store.
    """

    def __init__(self, f:Union[PCloudizedFunction,PFuncSnapshotAddress]):
        """Persist a cloudized function's snapshot, create its address.

        Actual calculation happens only the first time the constructor
        is called. Then the address is stored in the .func_snapshot_address
        attribute of the cloudized function.
        """
        if isinstance(f, PFuncSnapshotAddress):
            self.prefix = f.prefix
            self.hash_id = f.hash_id
            return
        assert isinstance(f,PCloudizedFunction)
        assert f.__name__ in f.cloud.cloudized_functions
        if f.func_snapshot_address is not None:
            self.prefix = f.func_snapshot_address.prefix
            self.hash_id = f.func_snapshot_address.hash_id
            return
        self.prefix = self._build_prefix(f)
        snapshot = PCloudizedFunctionSnapshot(f)
        snapshot_address = f.cloud.push_value(snapshot)
        self.hash_id = snapshot_address.hash_id
        # if self not in f.cloud.func_snapshots:
        #     f.cloud.func_snapshots[self] = snapshot_address
        #     f.cloud.post_log_entry(
        #         prefix_key="func_snapshot_first_usage"
        #         ,log_entry = snapshot
        #         ,add_context_info = True)

    def __repr__(self):
        return (f"PFuncSnapshotAddress( prefix={self.prefix} ,"
               + f" hash_id={self.hash_id} )")


class KwArgsDict(dict):
    """ A class that encapsulates keyword arguments for a function call."""

    def __init__(self,*args, **kargs): # TODO: check if we need *args here
        super().__init__(*args, **kargs)

    def pack(self, *, cloud:P_Cloud) -> KwArgsDict:
        """ Replace values in a dict with their hash addresses.

        This function also "normalizes" the dictionary by sorting keys
        in order to always get the same hash values
        for the same lists of arguments.
        """
        packed_copy = KwArgsDict()
        for k in sorted(self.keys()):
            value = self[k]
            if isinstance(value,PValueAddress):
                packed_copy[k] = value
            else:
                key = cloud.push_value(value)
                packed_copy[k] = key
        return packed_copy

    def unpack(self,*,cloud:P_Cloud) -> KwArgsDict:
        """ Restore values based on their hash addresses."""
        unpacked_copy = KwArgsDict()
        for k,v in self.items():
            if isinstance(v, PValueAddress):
                unpacked_copy[k] = cloud.value_store[v]
            else:
                unpacked_copy[k] = v
        return unpacked_copy


class PFuncOutputAddress(PHashAddress):
    """A globally unique address of a function execution result.

    PFuncOutputAddress is a universal global identifier of a value,
    which was (or will be) an output of a cloudized function execution.
    Assuming a function is pure, we only need function's PFuncSnapshotAddress
    and arguments' values to build a "signature",
    which serves as a unique key for the output object.
    The hash component of an address is a hash of this unique key.

    An address also includes a prefix, which makes it easy for humans
    to interpret the address, and further decreases collision risk.
    """

    def __init__(self, f:PCloudizedFunction, arguments:KwArgsDict):
        assert isinstance(f,PCloudizedFunction)
        assert isinstance(arguments, KwArgsDict)
        f_base_address =  PFuncSnapshotAddress(f)
        self.prefix = f_base_address.prefix
        self.hash_id = self._build_hash_id(
            (f_base_address.hash_id, arguments.pack(cloud=f.cloud)))


    def __repr__(self):
        return (f"PFuncOutputAddress( prefix={self.prefix} ,"
               + f" hash_id={self.hash_id} )")



class P_Cloud(metaclass=ABCMeta):
    """A base class for all Pythagoras clouds.

    It is an interface for all objects that are implementing
    Pythagoras Abstraction Model:
    https://docs.google.com/document/d/1lgNOaRcZNGvW4wF894s7KmIWjhLX2cDVM_15a4lE02Y

    Methods:
    ----------
    add_pure_function(a_func:Callable) -> Callable
            Decorator that 'cloudizes' user-provided functions.

    push_value(value:Any) -> PValueAddress
            Add a value to value_store.

    post_log_entry(log_entry,prefix_key,add_context_info) -> SimpleDictKey
            Post a new entry into the event_log store.

    Properties
    ----------
    value_store: SimplePersistentDict
            An abstract property: a persistent dict-like object that
            stores all the values ever created within any running instance
            of cloudized functions. It's a key-value store, where
            the key (the object's address) is composed using
            the object's hash. Under the hood, these hash-based addresses
            are used by Pythagoras the same way as RAM-based addresses
            are used (via pointers and references) in C and C++ programs.

    func_snapshots: SimplePersistentDict
            Persistent store that keeps all version of all cloudized functions.
            It's a dict-like store that provides access to all versions of
            all functions ever created within the same P_Cloud.

    func_output_store: SimplePersistentDict
            An abstract property: a persistent dict-like object that
            caches all results of all cloudized function executions
            that ever happened in the system. Enables distributed
            memoization functionality ("calculate once, reuse
            forever").

    crash_history: SimplePersistentDict
            An abstract property: a persistent dict-like object that
            stores a complete log of all the exceptions
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

    p_purity_checks: float
            An abstract property: probability of stochastic purity checks.
            If a functions output has been stored on a cache,
            when the function is called with the same arguments next time,
            it'll re-use cached output with probability (1-p_purity_checks).
            With probability p_purity_checks the function will be
            executed once again, and its output will be compared with
            the cached one: if they differ, purity check will fail.
            p_purity_checks==1 means 'never re-use cached values'.
            p_purity_checks==0 means 'always re-use cached values when possible'.

    baseline_timezone: ZoneInfo
            An abstract property: a timezone used by all instances
            of cloudized functions. Different instances of cloudized
            functions might run on servers, physically located
            in various timezonses. To make logging and reporting consistent,
            all of them are required to use their P_Cloud's timezone,
            not their server's timezone.

    python_requires: str
            An abstract property: version specifier for Python.
            Defines which Python versions are supported by a P_Loud instance
            to run. Its format follows setuptools' python_requires format.

    install_requires: str | List[str]
            An abstract property: minimally required dependencies.
            The list of packages that a P_Cloud instance minimally needs
            to run. Its format follows setuptools' install_requires format.
    """

    def __init__(self,*args,**kwargs):
        pass


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


    # @property
    # @abstractmethod
    # def func_snapshots(self) -> SimplePersistentDict:
    #     """Persistent store that keeps all version of all cloudized functions.
    #
    #     It's a dict-like store that provides access to all version of
    #     all functions ever created within the same P_Cloud.
    #     """
    #     raise NotImplementedError


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
    def crash_history(self) -> SimplePersistentDict:
        """Persistent store that keeps log of all catastrophic events.

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


    @property
    @abstractmethod
    def p_purity_checks(self) -> float:
        """ Probability of stochastic purity checks.

        If a functions output has been stored on a cache, when the function is
        called with the same arguments next time, it will re-use
        cached output with probability (1-p_purity_checks).
        With probability p_purity_checks the function will be
        executed once again, and its output will be compared with
        the cached one: if they differ, purity check will fail.
        p_purity_checks==1 means 'never re-use cached values'.
        p_purity_checks==0 means 'always re-use cached values when possible'.
        """
        raise NotImplementedError


    @property
    @abstractmethod
    def baseline_timezone(self) -> ZoneInfo:
        """ Timezone used by all instances of cloudized functions.

        Different instances of cloudized functions might run on servers,
        physically located in various timezonses. To make logging and reporting
        consistent, all of them are required to use their P_Cloud's timezone,
        not their server's timezone.
        """
        raise NotImplementedError


    @property
    @abstractmethod
    def python_requires(self) -> str:
        """A version specifier for Python.

        Defines which Python versions are supported by a P_Loud instance
        to run. Its format follows setuptools' python_requires format.
        """
        raise NotImplementedError


    @property
    @abstractmethod
    def install_requires(self) -> Optional[Union[str,List[str]]]:
        """Packages that a P_Cloud instance minimally needs to run.

        The property's format follows setuptools' install_requires format.
        """
        raise NotImplementedError


    def push_value(self, value:Any) -> PValueAddress:
        """ Add a value to value_store"""
        key = PValueAddress(value)
        if not key in self.value_store:
            self.value_store[key] = value
        return key


    def get_func_output(self, address:PFuncOutputAddress) -> Any:
        key = self.func_output_store[address]
        return self.value_store[key]


    @abstractmethod
    def add_pure_function(self, a_func:Callable) -> PCloudizedFunction:
        """Decorator which 'cloudizes' user-provided functions. """
        raise NotImplementedError


    @abstractmethod
    def post_log_entry(
            self
            ,log_entry:Any
            ,prefix_key:Optional[SimpleDictKey]=None
            ,add_context_info:bool=True
            ) -> SimpleDictKey:
        """Post a new entry into the event_log store.
        
        If add_context_info==True, the entry name will contain human-readable
        information about the event (timestamp, node, process, etc.),
        and the entry will be augmented with detailed information about
        an execution environment from which the entry was posted. Otherwise,
        an UUID will be used to create the entry name, and no augmentation
        will be performed.
        """
        raise NotImplementedError


class ExceptionInfo:
    """ Helper class for remote logging, encapsulates exception/environment info.

    This class is used by P_Cloud_Implementation objects to log information
    in P_Cloud.exception persistent store.
    """

    def __init__(self, exc_type, exc_value, trace_back):
        assert isinstance(exc_value, BaseException)
        self.__name__ = get_long_infoname(exc_value)
        self.exception = exc_value
        self.exception_description = traceback.format_exception(
            exc_type, exc_value, trace_back)


class P_Cloud_Implementation(P_Cloud, metaclass=ABC_PostInitializable):
    """ A base class for all Pythagoras clouds.

    It is a base class for all objects that are implementing
    Pythagoras Abstraction Model:
    https://docs.google.com/document/d/1lgNOaRcZNGvW4wF894s7KmIWjhLX2cDVM_15a4lE02Y

    Methods:
    ----------
    add_pure_function(a_func:Callable) -> Callable
            Decorator that 'cloudizes' user-provided functions.

    push_value(value:Any) -> PValueAddress
            Add a value to value_store.

    post_log_entry(log_entry,prefix_key,add_context_info) -> SimpleDictKey
            Post a new entry into the event_log store.

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

    cloudized_functions: dict[str, Callable]
            A dictionary with modified (as a result of  applying
            the @add_pure_function decorator) versions of all
            cloudized functions in P_Cloud. Keys are the names
            of the functions.
    """
    _p_cloud_single_instance = None
    _install_requires: Optional[str] = None
    _python_requires: Optional[str] = None

    original_functions: dict[str, Callable] = dict()
    cloudized_functions: dict[str, PCloudizedFunction] = dict()

    base_dir:str = ""

    _p_purity_checks:float = 0.1

    _baseline_timezone = ZoneInfo("America/Los_Angeles")

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
        super().__init__(**kwargs)
        self._install_requires = install_requires  # TODO: polish later
        self._python_requires = python_requires  # TODO: polish later

        assert not os.path.isfile(base_dir)
        if not os.path.isdir(base_dir):
            os.mkdir(base_dir)
        assert os.path.isdir(base_dir)
        self.base_dir = os.path.abspath(base_dir)

        assert 0 <= p_purity_checks <= 1
        self._p_purity_checks = p_purity_checks

        self._register_exception_handlers()

    def __post__init__(self, *args, **kwargs) -> None:
        """ Enforce arguments-based singleton pattern. """
        P_Cloud_Implementation._instance_counter += 1
        if P_Cloud_Implementation._instance_counter == 1:
            init_signature  = (type(self),args,kw_args(**kwargs))
            P_Cloud_Implementation._init_signature_hash_address = PValueAddress(
                init_signature)
        else:
            new_init_signature = (type(self),args,kw_args(**kwargs))
            new_init_sign_hash = PValueAddress(new_init_signature)
            assert new_init_sign_hash == (
                P_Cloud_Implementation._init_signature_hash_address), (
                "You can't have several P_Cloud instances with different "
                "types and/or initialization arguments.")

    def _register_exception_handlers(self) -> None:
        """ Intersept & redirect unhandled exceptions to self.exceptions """

        P_Cloud_Implementation._old_excepthook = sys.excepthook

        def cloud_excepthook(exc_type, exc_value, trace_back):

            exc_event = ExceptionInfo(exc_type, exc_value, trace_back)

            self._post_event(
                event_store=self.crash_history
                , prefix_key=None
                , log_entry=exc_event
                , add_context_info = True)

            P_Cloud_Implementation._old_excepthook(
                exc_type, exc_value, trace_back)
            return

        sys.excepthook = cloud_excepthook

        def cloud_excepthandler(
                other_self
                , exc_type
                , exc_value
                , trace_back
                , tb_offset=None):

            exc_event = ExceptionInfo(exc_type, exc_value, trace_back)

            self._post_event(
                event_store=self.crash_history
                ,prefix_key=None
                ,log_entry=exc_event
                ,add_context_info=True)

            traceback.print_exception(exc_type, exc_value, trace_back)
            return

        try:  # if we are inside a notebook
            get_ipython().set_custom_exc(
                (BaseException,), cloud_excepthandler)
            self._is_running_inside_IPython = True
        except:
            self._is_running_inside_IPython = False


    def install_requires(self) -> Optional[Union[str,List[str]]]:
        return self._install_requires


    def python_requires(self) -> str:
        return self._python_requires


    def post_log_entry(
            self
            , log_entry: Any
            , prefix_key: Optional[SimpleDictKey] = None
            , add_context_info: bool = True
            ) -> SimpleDictKey:
        """Post a new entry into the event_log store."""
        return self._post_event(
            event_store = self.event_log
            , prefix_key = prefix_key
            , log_entry = log_entry
            , add_context_info = add_context_info)


    def _post_event(self
                    , event_store: SimplePersistentDict
                    , prefix_key:Optional[SimpleDictKey]
                    , log_entry: Any
                    , add_context_info:bool = True
                    ) -> SimpleDictKey:
        """ Add an event to an event store. """
        if add_context_info:
            event_id = str(datetime.now(self.baseline_timezone)
                           ).replace(":", "-")
            event_id += f"  user={getuser()}"
            event_id += f"  host={socket.gethostname()}"
            event_id += f"  pid={os.getpid()}"
            event_id += f"  platform={platform.platform()}"
            event_id += f"  event={get_long_infoname(log_entry)}"
            self._event_counter +=1
            if self._event_counter >= 1_000_000_000_000:
                self._event_counter = 1
            event_id += f"  counter={self._event_counter}"
            random_int = self._randomizer.randint(1,1_000_000_000_000)
            event_id += f"  random={random_int}"
            event_id = replace_unsafe_chars(event_id,"_")
        else:
            event_id = str(uuid.uuid1())

        if prefix_key is None:
            key = (event_id,)
        else:
            key = event_store._normalize_key(prefix_key) + (event_id,)

        if add_context_info:
            event = dict(
                event = log_entry
                ,context=buid_context(self.base_dir, self.baseline_timezone))
        else:
            event = log_entry

        event_store[key] = event
        return key

    @property
    def baseline_timezone(self) -> ZoneInfo:
        """ Timezone used by all instances of cloudized functions.

        Different instances of cloudized functions might run on servers,
        physically located in various timezonses. To make logging and reporting
        consistent, all of them are required to use their P_Cloud's timezone,
        not their server's timezone.
        """
        return self._baseline_timezone

    @property
    def p_purity_checks(self) -> float:
        """ Probability of stochastic purity checks.

        If a functions output has been stored on a cache, when the function is
        called with the same arguments next time, it will re-use
        cached output with probability (1-p_purity_checks).
        With probability p_purity_checks the function will be
        executed once again, and its output will be compared with
        the cached one: if they differ, purity check will fail.
        p_purity_checks==1 means 'never re-use cached values'.
        p_purity_checks==0 means 'always re-use cached values when possible'.
        """
        return self._p_purity_checks


    def local_function_call(
            self
            ,func_name:str
            ,func_kwargs:KwArgsDict
            ) -> PFuncOutputAddress:
        """ Perform a local synchronous call for a cloudized function.

        This method should not be called directly. Instead,
        use the traditional syntax below while caling a cloudized function:
        func_name(**kwargs)
        """

        original_function = self.original_functions[func_name]
        cloudized_function = self.cloudized_functions[func_name]

        kwargs_packed = func_kwargs.pack(cloud=self)
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
            # result = self.value_store[result_key]
        else:
            kwargs_unpacked = func_kwargs.unpack(cloud=self)
            result = original_function(**kwargs_unpacked)
            result_key = self.push_value(result)

            if func_key in self.func_output_store:
                # TODO: change to a "raise" statement
                assert self.func_output_store[func_key] == result_key, (
                    "Stochastic purity check has failed")
            else:
                self.func_output_store[func_key] = result_key

        return func_key


    def sync_remote_function_call(self
                                  ,func_name:str
                                  ,func_kwargs:KwArgsDict
                                  ) -> PFuncOutputAddress:
        """ Perform a remote synchronous call for a cloudized function.

        This method should not be called directly. Instead, use the syntax
        below (requires a functions first to be added to a cloud):
        func_name.sync_remote(**kwargs)
        """
        raise NotImplementedError


    def async_remote_function_call(self
                                   ,func_name: str
                                   ,func_kwargs: KwArgsDict
                                   )-> PFuncOutputAddress:
        """ Perform a remote asynchronous call for a cloudized function.

        This method should not be called directly. Instead, use the syntax
        below (requires a functions first to be added to a cloud):
        func_name.async_remote(**kwargs)
        """
        raise NotImplementedError


    def sync_parallel_function_call(self
                                    , func_name: str
                                    , all_kwargs: List[KwArgsDict]
                                    ) -> List[PFuncOutputAddress]:
        """Synchronously execute multiple instances of a cloudized function.

        This method should not be called directly. Instead, use the syntax
        below (requires a functions first to be added to a cloud):
        func_name.sync_parallel( kw_args(..) for .. in .. )
        """

        raise NotImplementedError


    def async_parallel_function_call(self
                                     , func_name: str
                                     , all_kwargs:List[KwArgsDict]
                                     ) -> List[PFuncOutputAddress]:
        """Asynchronously execute multiple instances of a cloudized function.

        This function should not be called directly. Instead, use the syntax
        below (requires a functions first to be added to a cloud):
        func_name.async_parallel( kw_args(..) for .. in .. )
        """
        raise NotImplementedError


    def check_if_func_output_is_available(
            self
            ,func_name: str
            ,func_kwargs: KwArgsDict
            ) -> bool:
        """Check if function output for the arguments has already been cached.

        This function should not be called directly. Instead, use the syntax
        below (requires a functions first to be added to a cloud):
        func_name.is_output_available(**kwargs)
        """
        cloudized_function = self.cloudized_functions[func_name]
        func_key = PFuncOutputAddress(cloudized_function, func_kwargs)
        return func_key in self.func_output_store


    def add_pure_function(self, a_func:Callable) -> PCloudizedFunction:
        """Decorator which 'cloudizes' user-provided functions. """
        assert callable(a_func)
        assert not isinstance(a_func, PCloudizedFunction), (
            "A function is not allowed to be added to the cloud twice")
        assert hasattr(a_func,"__name__"), (
            "Nameless functions can not be cloudized")
        assert a_func.__name__ != "<lambda>", (
            "Lambda functions can not be cloudized")

        # TODO: change to custom exception
        assert a_func.__name__ not in self.original_functions, (
            f"Function {a_func.__name__} has already been added to the cloud."
            + "Can't add one more time.")

        self.original_functions[a_func.__name__] = a_func

        wrapped_function = PCloudizedFunction(self,a_func.__name__)

        # TODO: change to custom exception
        assert wrapped_function.__name__ not in self.cloudized_functions, (
            f"Function {wrapped_function.__name__} has already been added "
            + "to the cloud. Can't add one more time.")

        self.cloudized_functions[wrapped_function.__name__] = wrapped_function

        return wrapped_function


class SharedStorage_P2P_Cloud(P_Cloud_Implementation):
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

        self._crash_history = FileDirDict(
            dir_name=os.path.join(self.base_dir, "exception_log")
            ,file_type="json")

        # self._func_snapshots = FileDirDict(
        #     dir_name=os.path.join(self.base_dir, "func_snapshots")
        #     ,file_type="json")

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
    def crash_history(self) -> SimplePersistentDict:
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
        return self._crash_history


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
                                  , func_kwargs: KwArgsDict
                                  ) -> PFuncOutputAddress:
        """Emulate synchronous remote execution of a function.

        Instead of actual remote execution, it performs local one.
        """

        return self.local_function_call(func_name, func_kwargs)

    def async_remote_function_call(self
                                  , func_name: str
                                  , func_kwargs: KwArgsDict
                                  ) -> PFuncOutputAddress:
        """Emulate asynchronous remote execution of a function.

        Instead of actual asynchronous remote  execution,
        it performs local synchronous one.
        """

        return self.local_function_call(func_name, func_kwargs)

    def sync_parallel_function_call(self
                                    , func_name: str
                                    , all_kwargs:List[KwArgsDict]
                                    ) -> List[PFuncOutputAddress]:
        """Emulate parallel execution of multiple instances of function.

        Instead of actual remote parallel execution,
        it performs randomized local sequential execution .
        """

        input_list = list(all_kwargs)
        for e in input_list:
            assert isinstance(e, KwArgsDict)

        shuffled_input_list = list(enumerate(input_list))
        self._randomizer.shuffle(shuffled_input_list)

        result = []
        for e in shuffled_input_list:
            func_call_arguments = e[1]
            func_call_output = self.local_function_call(
                func_name,func_call_arguments)
            result_item = (e[0], func_call_output)
            result.append(result_item)

        result = sorted(result, key=lambda t: t[0])
        result = [e[1] for e in result]

        return result


    def async_parallel_function_call(self
                                    , func_name: str
                                    , all_kwargs:List[KwArgsDict]
                                    ) -> List[PFuncOutputAddress]:
        """Emulate parallel async execution of multiple instances of function.

        Instead of actual remote asynchronous parallel execution,
        it performs randomized local sequential synchronous execution.
        """
        return self.sync_parallel_function_call(func_name, all_kwargs)


class MLProjectWorkspace(P_Cloud):
    """Simple shared workspace for small teams working on ML projects.

    Objects of this class enable faster experimentation and
    more efficient collaboration for small teams working on ML projects,
    e.g. teams participating in Kaggle competitions.

    MLProjectWorkspace also provides API similar to P_Cloud objects,
    even though MLProjectWorkspace does not inherit from P_Cloud
    """

    base_cloud: P_Cloud

    def __init__(self, base: Union[str, P_Cloud], **kwargs):
        super().__init__()
        if isinstance(base, str):
            self.base_cloud = SharedStorage_P2P_Cloud(base_dir=base)
        elif isinstance(base, P_Cloud):
            self.base_cloud = base
        else:
            assert False, "base must be either str or P_Cloud"
            # TODO: chaneg to exception


    def value_store(self) -> SimplePersistentDict:
        """ A persistent dict-like object that stores all ever created values.

        It's a key-value store, where the key (the object's address)
        is composed using the object's hash. Under the hood, these
        hash-based addresses are used by Pythagoras the same way
        as RAM-based addresses are used (via pointers and references)
        in C and C++ programs.
        """
        return self.base_cloud.value_store


    def func_output_store(self) -> SimplePersistentDict:
        """Persistent cache that keeps execution results for cloudized functions.

        It's a dict-like store that enables persistent / distributed
        memoization functionality ("calculate once, reuse forever").
        """
        return self.base_cloud.func_output_store


    def crash_history(self) -> SimplePersistentDict:
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
        return self.base_cloud.crash_history

    #
    # def func_snapshots(self) -> SimplePersistentDict:
    #     return self.base_cloud.func_snapshots


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