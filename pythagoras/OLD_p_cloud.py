""" Core Pythagoras classes that provide cloud-access functionality.
"""
from __future__ import annotations

import base64
import hashlib
import inspect
import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from abc import abstractmethod, ABCMeta
from collections.abc import Sequence
from copy import deepcopy
from random import Random, randint
import traceback
from typing import Any, Optional, Callable, List, Union, Dict, TypeVar, Type
from joblib.hashing import NumpyHasher, Hasher

from pythagoras.________OLD________.OLD_dependency_discovery import _all_dependencies_one_func
from pythagoras.________OLD________.OLD_persistent_dicts import FileDirDict, SimplePersistentDict
from pythagoras.OLD_utils import get_long_infoname, replace_unsafe_chars \
    ,get_normalized_function_source ,detect_local_variable_in_callstack

from pythagoras.OLD_utils import ABC_PostInitializable


def kw_args(**kwargs) -> KwArgsDict:
    """ Helper function to be used with .parallel and similar methods

    It enables simple syntax to simultaneously launch
    many remote instances of a function with different input arguments:

    some_slow_function.parallel(
        kw_args(arg1=i, arg2=j) for i in range(100) for j in range(15)  )
    """
    return KwArgsDict(**kwargs).pack()


class PCloudizedFunction:
    """ An API for various execution modes for cloudized functions."""

    original_name:str
    original_function:Callable
    original_annotations:Dict
    original_source:str
    func_snapshot_address:Optional[PFuncSnapshotAddress]
    __original_source_with_dependencies:Optional[Dict[str,str]]

    def __init__(self, function_name:str):
        cloud = P_Cloud_Implementation._single_instance
        self.original_name = self.__name__ = function_name
        original_function = cloud.original_functions[function_name]
        # original_annotations = dict()
        # if hasattr(original_function, "__annotations__"):
        #     original_annotations = deepcopy(original_function.__annotations__)
        # if "self" in original_annotations:
        #     #TODO: Should we issue a warning here? Or raise an exception?
        #     del original_annotations["self"]
        self.original_source = get_normalized_function_source(original_function)
        self.func_snapshot_address = None
        self.__original_source_with_dependencies = None
        self.__doc__ = original_function.__doc__
        #TODO: mimic functools.update_wrapper for all 5 execution methods


    @property
    def _cloud(self) -> P_Cloud_Implementation:
        return P_Cloud_Implementation._single_instance


    @property
    def _fsnapshot_event_log(self) -> SimplePersistentDict:
        dummy_addr = PFuncOutputAddress(self,KwArgsDict())
        snapshot_addr = (dummy_addr[0],dummy_addr[1])
        return self._cloud.event_log.get_subdict(snapshot_addr)


    @property
    def _fsnapshot_crash_history(self) -> SimplePersistentDict:
        dummy_addr = PFuncOutputAddress(self, KwArgsDict())
        snapshot_addr = (dummy_addr[0], dummy_addr[1])
        return self._cloud.crash_history.get_subdict(snapshot_addr)


    @property
    def _fname_event_log(self) -> SimplePersistentDict:
        dummy_addr = PFuncOutputAddress(self, KwArgsDict())
        snapshot_addr = (dummy_addr[0],)
        return self._cloud.event_log.get_subdict(snapshot_addr)


    @property
    def _fname_crash_history(self) -> SimplePersistentDict:
        dummy_addr = PFuncOutputAddress(self, KwArgsDict())
        snapshot_addr = (dummy_addr[0],)
        return self._cloud.crash_history.get_subdict(snapshot_addr)


    def __call__(self,**kwargs) -> Any:
        """Locally run memoized/cloudized version of a function"""
        return self._sync_inprocess_v(**kwargs)

    def remote(self,**kwargs) -> PFuncOutputAddress:
        """Asynchronously/remotely run a cloudized version of a function

         'Remotely' could mean either running on a different computer
         in the cloud or running in a different process on the
         local computer. There is no guaranty where exactly
         the function will run.

         'Asynchronously' means there is no guaranty for the execution
         timeline and there is no guaranty for how many times
         the function will run; eventually it will execute
         at least once. The .remote() call returns a cloud address.
         The address will point to the actual function output
         once it successfully completes its first execution;
         until then the address points to an unretrievable non-value.
         """
        return self._async_incloud_a(**kwargs)

    def parallel(self, arg_list:List[KwArgsDict]) -> List[Any]:
        """Synchronously execute multiple cloudized function calls.

        For each set of input parameters from arg_list,
        the system will run the function with this set of parameters.
        There is no guaranty whether all (or even most) of
        these function calls will be executed on a local computer
        or in the cloud, and in which order; however,
        at least one execution will always happen locally
        unless all outputs are already stored in the cache.

        Pythagoras will try to execute most (or at least some)
        of the function calls in parallel in the cloud;
        if it's not possible, they will be executed
        locally and sequentially. Once each function call
        executes at least once, .parallel() will return
        a list of the execution outputs.
        """
        self._async_group_incloud_kwargss_a(arg_list)
        return self._sync_group_inpocess_kwargss_v(arg_list)


    def remote_parallel(self
            , arg_list:List[KwArgsDict]
            ) -> List[PFuncOutputAddress]:
        """Asynchronously execute multiple cloudized function calls.

        For each set of input parameters from arg_list,
        the system will run the function with this set of parameters.
        There is no guaranty whether all (or even most) of
        these function calls will be executed on a local computer
        or in the cloud.

        Pythagoras will try to execute most (or at least some)
        of the function calls in parallel. However,
        there is no guaranty for the execution
        timeline/order, and there is no guaranty for how many times
        each combination of input parameters will be used;
        eventually each of them will be used at least once.

        .remote_parallel() will return a list of cloud addresses.
        Each address will point to an actual function output
        once the function successfully runs with the corresponding
        set of parameters; until then the address points
        to an unretrievable non-value.
        """
        return self._async_group_incloud_kwargss_a(arg_list)


    def _sync_inprocess_v(self, **kwargs) -> Any:
        """Perform synchronous local inprocess execution of a function.

        Returns an actual value of the execution output.
        """
        return self._sync_inprocess_kwargs_v(
            KwArgsDict(**kwargs).pack())


    def _sync_inprocess_kwargs_v(self, kwargsd:KwArgsDict) -> Any:
        """Perform synchronous local inprocess execution of a function.

        Returns an actual value of the execution output.
        """
        assert isinstance(kwargsd, KwArgsDict)
        __fo_addr__ = PFuncOutputAddress(self.__name__, kwargsd)
        # post_log_entry() attributes posted events to an address, stored
        # in a variable named __fo_addr__ in one of callstack frames
        try:
            self._cloud.sync_local_inprocess_function_call(__fo_addr__)
            return __fo_addr__.get(timeout=0)
        except BaseException as exc:
            post_log_entry(exc)
            raise


    def _sync_subprocess_v(self, **kwargs) -> Any:
        """Perform synchronous local execution of a function in a subprocess"""
        return self._sync_subprocess_kwargs_v(KwArgsDict(**kwargs).pack())



    def _sync_subprocess_kwargs_v(self, kwargsd:KwArgsDict) -> Any:
        """Perform synchronous local execution of a function in a subprocess"""
        assert isinstance(kwargsd, KwArgsDict)
        __fo_addr__ = PFuncOutputAddress(self.__name__, kwargsd)
        # post_log_entry() attributes posted events to an address, stored
        # in a variable named __fo_addr__ in one of callstack frames
        try:
            self._cloud.sync_local_subprocess_function_call(__fo_addr__)
            return __fo_addr__.get()
        except BaseException as exc:
            post_log_entry(exc)
            raise


    def _async_subprocess_a(self
            , **kwargs
            ) -> PFuncOutputAddress:
        """Perform asynchronous local execution of a function in a subprocess"""
        return self._async_subprocess_kwargs_a(KwArgsDict(**kwargs).pack())


    def _async_subprocess_kwargs_a(self
            , kwargsd:KwArgsDict
            ) -> PFuncOutputAddress:
        """Perform asynchronous local execution of a function in a subprocess"""
        assert isinstance(kwargsd, KwArgsDict)
        __fo_addr__ = PFuncOutputAddress(self.__name__, kwargsd)
        # post_log_entry() attributes events to an address, stored
        # in a variable named __fo_addr__ in one of callstack frames
        try:
            self._cloud.async_local_subprocess_function_call(__fo_addr__)
            return __fo_addr__
        except BaseException as exc:
            post_log_entry(exc)
            raise


    def _async_incloud_a(self
            , **kwargs
            ) -> PFuncOutputAddress:
        """Perform asynchronous remote execution of a function"""
        return self._async_incloud_kwargs_a(KwArgsDict(**kwargs).pack())


    def _async_incloud_kwargs_a(self
            , kwargsd:KwArgsDict
            ) -> PFuncOutputAddress:
        """Perform asynchronous remote execution of a function"""
        assert isinstance(kwargsd,KwArgsDict)
        __fo_addr__ = PFuncOutputAddress(self.__name__, kwargsd)
        # post_log_entry() attributes posted events to an address, stored
        # in a variable named __fo_addr__ in one of callstack frames
        try:
            self._cloud.async_incloud_function_call(__fo_addr__)
            return  __fo_addr__
        except BaseException as exc:
            post_log_entry(exc)
            raise


    def _sync_group_inpocess_kwargss_v(self
              ,arg_list:Sequence[KwArgsDict]
              ) -> List[Any]:
        """Synchronously execute multiple function calls"""
        addresses = []
        for a in arg_list:
            assert isinstance(a, KwArgsDict)
            addresses.append(PFuncOutputAddress(self.__name__, a))

        shuffled_arg_list = [deepcopy(a.pack()) for a in arg_list]
        self._cloud._randomizer.shuffle(shuffled_arg_list)

        for a in shuffled_arg_list:
            self._sync_inprocess_kwargs_v(a)

        result =  [a.get(timeout=0) for a in addresses]
        return result


    def _async_group_incloud_kwargss_a(self
                       ,arg_list:List[KwArgsDict]
                       ) -> List[PFuncOutputAddress]:
        """Asynchronously run in the cloud multiple instances of function"""
        addresses = []
        for a in arg_list:
            assert isinstance(a, KwArgsDict)
            __fo_addr__ = PFuncOutputAddress(self.__name__, a)
            addresses.append(__fo_addr__)
            self._cloud.async_incloud_function_call(__fo_addr__)
        result = addresses
        return result


    def ready(self, **kwargs):
        """Check if function output for the arguments has already been cached"""

        return self._cloud.check_if_ready(
            self.__name__, KwArgsDict(**kwargs))


    @property
    def original_source_with_dependencies(self) -> Dict[str,str]:
        """Lazily construct a list of function dependencies within a cloud.

         Returns a string containing source code for the cloudized function
         and all other cloudized functions (from the same P_Cloud)
         that the function depends on.

         Returned functions are sorted in alphabetical order by their names.
         """
        if self.__original_source_with_dependencies is not None:
            #TODO: should we add asserts / checks here?
            return self.__original_source_with_dependencies

        dependencies = _all_dependencies_one_func(
            self.__name__, self._cloud.cloudized_functions)
        dependencies = sorted(dependencies)

        result = {f:self._cloud.cloudized_functions[f].original_source
                  for f in dependencies}

        self.__original_source_with_dependencies = result

        return result


class PCloudizedFunctionSnapshot:
    """ Information about a specific version of a cloudized function.

    Objects of this class contain full information, needed to restore
    from scratch a specific version of a cloudized function
    in a cloud-independent way. They are used to store and
    exchange functions between different instances of P_Cloud.
    """

    def __init__(self, f:PCloudizedFunction):
        assert isinstance(f,PCloudizedFunction)
        p_cloud = P_Cloud_Implementation._single_instance
        self.__name__ = self.name = f.__name__
        self.install_requires = p_cloud.install_requires
        self.python_requires = p_cloud.python_requires
        self.shared_import_statements = p_cloud.shared_import_statements
        self.source = f.original_source
        self.source_with_dependencies = f.original_source_with_dependencies
        assert self.source == self.source_with_dependencies[self.name]
        #TODO: refactor to drop self.source


class PFunctionCallSignature:
    def __init__(self, f:PCloudizedFunction, a:KwArgsDict):
        assert isinstance(f, PCloudizedFunction)
        assert isinstance(a, KwArgsDict)
        self.__name__ = f.__name__
        self.function_addr = PFuncSnapshotAddress(f)
        self.args_addr = PValueAddress(a)

    def get_snpsht_id(self):
        return "snpsht_"+self.function_addr.hash_value[:10]


class PHashAddress(Sequence):
    """A globally unique hash-based address.

     Consists of 2 or 3 strings. Includes
     a human-readable prefix, an optional descriptor, and a hash.
     """

    prefix: str
    descriptor: Optional[str]
    hash_value: str
    _hash_type: str = "sha256"

    @staticmethod
    def _build_prefix(x: Any) -> str:
        """Create a short human-readable summary of an object."""

        prfx = get_long_infoname(x)

        clean_prfx = replace_unsafe_chars(prfx, "_")

        return clean_prfx

    @staticmethod
    def _build_descriptor(x: Any) -> Optional[str]:
        """Create a short summary of object's length/shape."""

        dscrptr = None

        if isinstance(x,PFunctionCallSignature):
            # TODO: replace with proper OOP approach
            dscrptr = x.get_snpsht_id()

        elif (hasattr(x, "shape")
            and hasattr(x.shape, "__iter__")
            and callable(x.shape.__iter__)
            and not callable(x.shape)):

            dscrptr = "shape_"
            for n in x.shape:
                dscrptr += str(n) + "_x_"
            dscrptr = dscrptr[:-3]

        elif (hasattr(x, "__len__")
              and callable(x.__len__)):
            dscrptr = "len_" + str(len(x))

        if dscrptr:
            return replace_unsafe_chars(dscrptr, "_")
        else:
            return None


    @staticmethod
    def _build_hash_value(x: Any) -> str:
        """Create a URL-safe hashdigest for an object."""

        if 'numpy' in sys.modules:
            hasher = NumpyHasher(hash_name=PHashAddress._hash_type)
        else:
            hasher = Hasher(hash_name=PHashAddress._hash_type)
        return hasher.hash(x) #TODO: switch to Base32


    @classmethod
    def from_strings(cls, *
                     , prefix:str
                     , hash_value:str
                     , descriptor: Optional[str]=None
                     , check_value_store:bool=True
                     ) -> PHashAddress:
        """(Re)construct address from text representations of prefix and hash"""

        assert prefix, "prefix must be a non-empty string"
        assert hash_value, "hash_value must be a non-empty string"
        if descriptor is not None:
            assert descriptor, "descriptor must be None or a non-empty string"

        address = cls.__new__(cls)
        super(cls, address).__init__()
        address.prefix = prefix
        address.descriptor = descriptor
        address.hash_value = hash_value
        if check_value_store:
            p_cloud = P_Cloud_Implementation._single_instance
            assert address in p_cloud.value_store
        return address

    @property
    @abstractmethod
    def ready(self) -> bool:
        """Check if address points to a value that is ready to be retrieved."""
        # TODO: decide whether we need .ready() at the base class
        raise NotImplementedError


    @abstractmethod
    def get(self, timeout:Optional[int] = None) -> Any:
        """Retrieve value, referenced by the address"""
        raise NotImplementedError


    def __eq__(self, other) -> bool:
        """Return self==other. """
        return (isinstance(other, self.__class__)
                and self.prefix == other.prefix
                and self.descriptor == other.descriptor
                and self.hash_value == other.hash_value)


    def __ne__(self, other) -> bool:
        """Return self!=other. """
        return not self.__eq__(other)


    def __len__(self) -> int:
        """Return len(self), always equals to 2 or 3. """
        return 3 if self.descriptor else 2


    def __getitem__(self, item):
        """""X.__getitem__(y) is an equivalent to X[y]"""

        if item == 0:
            return self.prefix

        if item == 1:
            return self.descriptor if self.descriptor else self.hash_value

        if item == 2 and self.descriptor:
            return self.hash_value

        raise IndexError(f"PHashAddress only has {len(self)} items.")


    @abstractmethod
    def __repr__(self):
        raise NotImplementedError


T = TypeVar("T")

class PValueAddress(PHashAddress):
    """A globally unique address of an immutable value.

    PValueAddress is a universal global identifier of any (constant) value.
    Using only the value's hash should (theoretically) be enough to
    uniquely address all possible data objects that the humanity  will create
    in the foreseeable future (see, for example ipfs.io).

    However, an address also includes a prefix and an optional descriptor.
    It makes it easier for humans to interpret an address,
    and further decreases collision risk.
    """

    def __init__(self, data: Any, push_to_cloud:bool=True):

        if isinstance(data, PValueAddress):
            self.prefix = data.prefix
            self.descriptor = data.descriptor
            self.hash_value = data.hash_value
            return

        assert not isinstance(data,PHashAddress), (
            "PValueAddress is the only PHashAddress which is allowed "
            +"to be converted to PValueAddress")

        if isinstance(data, KwArgsDict):
            data = data.pack()

        self.prefix = self._build_prefix(data)
        self.descriptor = self._build_descriptor(data)
        self.hash_value = self._build_hash_value(data)

        if push_to_cloud:
            cloud = P_Cloud_Implementation._single_instance
            cloud.value_store[self] = data

    @property
    def ready(self):
        """Check if address points to a value that is ready to be retrieved."""
        cloud = P_Cloud_Implementation._single_instance
        return self in cloud.value_store


    def get(self, timeout:Optional[int] = None) -> Any:
        """Retrieve value, reference by the address"""
        cloud = P_Cloud_Implementation._single_instance
        return cloud.value_store[self]

    def get_typed(self
            ,expected_type:Type[T]
            ,timeout:Optional[int]=None
            ) -> T:
        """Retrieve value with a known type """
        result = self.get(timeout)
        assert isinstance(result, expected_type)
        return result

    def __repr__(self):
        str_repr =  f"ValueAddress( prefix={self.prefix} "
        if self.descriptor:
            str_repr += f", descriptor={self.descriptor} "
        str_repr += f", hash_value={self.hash_value} )"
        return str_repr


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

    An address also includes a prefix, which makes it
    more simple for humans to interpret an address,
    and further decreases collision risk.

    The first time a new PFuncSnapshotAddress is created,
    it writes a new entry to P_Cloud.function_snapshots store.
    """

    def __init__(self
                 ,f:Union[PCloudizedFunction,PFuncSnapshotAddress]
                 ,push_to_cloud = True):
        """Persist a cloudized function's snapshot, create its address.

        Actual calculation happens only the first time the constructor
        is called. Then the address is stored in the .func_snapshot_address
        attribute of the cloudized function.
        """
        if isinstance(f, PFuncSnapshotAddress):
            self.prefix = f.prefix
            self.descriptor = f.descriptor
            self.hash_value = f.hash_value
            return
        assert isinstance(f,PCloudizedFunction)
        cloud = P_Cloud_Implementation._single_instance
        assert f.__name__ in cloud.cloudized_functions
        if f.func_snapshot_address is not None:
            self.prefix = f.func_snapshot_address.prefix
            self.descriptor = f.func_snapshot_address.descriptor
            self.hash_value = f.func_snapshot_address.hash_value
            return
        snapshot = PCloudizedFunctionSnapshot(f)
        snapshot_address = PValueAddress(snapshot,push_to_cloud)
        self.prefix = snapshot_address.prefix
        self.descriptor = snapshot_address.descriptor
        self.hash_value = snapshot_address.hash_value
        f.func_snapshot_address = self

    @property
    def ready(self):
        """Check if address points to a value that is ready to be retrieved."""
        cloud = P_Cloud_Implementation._single_instance
        return self in cloud.value_store


    def get(self, timeout:Optional[int]=None) -> PCloudizedFunctionSnapshot:
        """Retrieve value, reference by the address"""
        cloud = P_Cloud_Implementation._single_instance
        return cloud.value_store[self]


    def __repr__(self):
        str_repr = f"PFuncSnapshotAddress( prefix={self.prefix} "
        if self.descriptor:
            str_repr += f", descriptor={self.descriptor} "
        str_repr += f", hash_value={self.hash_value} )"
        return str_repr


class KwArgsDict(dict):
    """ A class that encapsulates keyword arguments for a function call."""

    def __init__(self, **kargs): # TODO: check if we need *args here
        super().__init__()
        for k in sorted(kargs):
            self[k] = kargs[k]

    @property
    def _cloud(self) -> P_Cloud_Implementation:
        return P_Cloud_Implementation._single_instance

    def pack(self) -> KwArgsDict:
        """ Replace values in a dict with their hash addresses.

        This function  "normalizes" the dictionary by sorting the keys
        and replacing values with their hash addresses
        in order to always get the same hash values
        for the same lists of arguments.
        """
        packed_copy = KwArgsDict()
        for k in sorted(self):
            value = self[k]
            if isinstance(value,PValueAddress):
                packed_copy[k] = value
            else:
                key = self._cloud.push_value(value)
                packed_copy[k] = key
        return packed_copy


    def unpack(self) -> KwArgsDict:
        """ Restore values based on their hash addresses."""
        unpacked_copy = KwArgsDict()
        for k,v in self.items():
            if isinstance(v, PValueAddress):
                unpacked_copy[k] = self._cloud.value_store[v]
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

    An address also includes a prefix and a descriptor,
    which make it easy for humans to interpret the address,
    and further decreases collision risk.
    """

    def __init__(self
                 , f:Union[PCloudizedFunction,str]
                 , arguments:KwArgsDict):
        assert isinstance(f,(PCloudizedFunction,str))
        assert isinstance(arguments, KwArgsDict)
        if isinstance(f,str):
            cloud = P_Cloud_Implementation._single_instance
            f = cloud.cloudized_functions[f]
        f_o_signature = PFunctionCallSignature(f,arguments)
        result = PValueAddress(f_o_signature)
        self.prefix = result.prefix
        self.descriptor = result.descriptor
        self.hash_value = result.hash_value

    @property
    def ready(self):
        """Check if address points to a value that is ready to be retrieved."""
        return self in self._cloud.func_output_store


    def get(self, timeout:Optional[int]=None) -> Any:
        """Retrieve value, referenced by the address.

        If the value is not immediately available, backoff exponentially
        till timeout is exceeded. If timeout is None, keep trying forever.
        """
        cloud = P_Cloud_Implementation._single_instance
        start_time, backoff_period = time.time(), 1.0
        stop_time = (start_time+timeout) if timeout else None
        # start_time, stop_time and backoff_period are in seconds
        while True:
            try:
                address = cloud.func_output_store[self]
                return cloud.value_store[address]
            except:
                time.sleep(backoff_period)
                backoff_period *= 2.0
                backoff_period += cloud._randomizer.uniform(-0.5, 0.5)
                if stop_time:
                    current_time = time.time()
                    if current_time + backoff_period > stop_time:
                        backoff_period = stop_time - current_time
                    if current_time > stop_time:
                        raise TimeoutError
                backoff_period = max(1.0, backoff_period)


    def __repr__(self) -> str:
        str_repr = f"PFuncOutputAddress( prefix={self.prefix} "
        if self.descriptor:
            str_repr += f", descriptor={self.descriptor} "
        str_repr += f", hash_value={self.hash_value} )"
        return str_repr


    @property
    def _cloud(self) -> P_Cloud_Implementation:
        return P_Cloud_Implementation._single_instance


    @property
    def _function_name(self) -> str:
        signature_address = PValueAddress.from_strings(
            prefix=self.prefix
            , hash_value=self.hash_value
            , descriptor=self.descriptor)
        restored_signature = signature_address.get_typed(PFunctionCallSignature)
        return restored_signature.__name__


    @property
    def _function(self) -> PCloudizedFunction:
        signature_address = PValueAddress.from_strings(
            prefix=self.prefix
            , hash_value=self.hash_value
            , descriptor=self.descriptor)
        restored_signature = signature_address.get_typed(PFunctionCallSignature)
        func_name = restored_signature.__name__
        assert (PFuncSnapshotAddress(self._cloud.cloudized_functions[func_name])
                == restored_signature.function_addr), (
                "Restored snapshot is inconsistent with the current version" +
                f" of cloudized function {func_name}" )
        return self._cloud.cloudized_functions[func_name]


    @property
    def _packed_arguments(self) -> KwArgsDict:
        signature_address = PValueAddress.from_strings(
            prefix=self.prefix
            , hash_value=self.hash_value
            , descriptor=self.descriptor)
        restored_signature = signature_address.get_typed(PFunctionCallSignature)
        arguments = restored_signature.args_addr.get_typed(KwArgsDict)
        return arguments


    @property
    def _arguments(self) -> KwArgsDict:
        return self._packed_arguments.unpack()


    @property
    def _fo_event_log(self) -> SimplePersistentDict:
        return self._cloud.event_log.get_subdict(tuple(self))


    @property
    def _fo_crash_history(self) -> SimplePersistentDict:
        return self._cloud.crash_history.get_subdict(tuple(self))


class P_Cloud(metaclass=ABCMeta):
    """A base class for all Pythagoras clouds.

    It is an interface for all objects that are implementing
    Pythagoras Abstraction Model:
    https://docs.google.com/document/d/1lgNOaRcZNGvW4wF894s7KmIWjhLX2cDVM_15a4lE02Y

    Methods:
    ----------
    cloudize_function(a_func:Callable) -> PCloudizedFunction
            Decorator that cloudizes a user-provided idempotent function.

    push_value(value:Any) -> PValueAddress
            Add a value to value_store.

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


    persistent_config_params: SimplePersistentDict
            An abstract property: a persistent dict-like object that
            stores all the configuration parameters of the cloud.


    ephemeral_config_params: Dict
            An abstract property: an in-RAM dictionary that stores
            all the ephemeral the configuration parameters of the cloud.


    python_requires: str
            An abstract property: version specifier for Python.
            Defines which Python versions are supported by a P_Loud instance
            to run. Its format follows setuptools' python_requires format.


    install_requires: Optional[str]
            An abstract property: minimally required dependencies.
            The list of packages that a P_Cloud instance minimally needs
            to run. Its format follows setuptools' install_requires format.


    shared_import_statements: Optional[str]
            An abstract property: contains import statements, which
            will be executed before running every cloudized function.
            The format of the property is a sequence of Python import statements.
    """

    def __init__(self
                , persist_config_init:Dict[str,Any] = None
                , persist_config_update:Dict[str,Any] = None
                , ephem_config:Dict[str,Any] = None
                , **kwargs):

        if ephem_config is None:
            ephem_config = self.default_ephemeral_params

        for k in ephem_config:
            self.ephemeral_config_params[k] = ephem_config[k]

        # TODO: Check the logic ^^^here^^^^ !!!!!!!!!!!

        if persist_config_init is None:
            persist_config_init = self.default_persistent_params

        crtn_tmstmp = "creation_timestamp"
        if not crtn_tmstmp in self.persistent_config_params:
            self.persistent_config_params[crtn_tmstmp] = time.time()
            for k in persist_config_init:
                self.persistent_config_params[k]=persist_config_init[k]

        if persist_config_update is not None:
            for k in persist_config_update:
                self.persistent_config_params[k] = persist_config_update[k]


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
    def persistent_config_params(self) -> SimplePersistentDict:
        """Persistent configuration parameters of the cloud.

         An abstract property: a persistent dict-like object that
        stores all the configuration parameters of the cloud.
        """
        raise NotImplementedError


    @property
    # @classmethod
    def default_persistent_params(cls) -> Dict[str,Any]:
        """Default values for persistent configuration parameters.
        """
        result = dict(
            p_idempotency_checks=0.1
            )

        return result


    @property
    @abstractmethod
    def ephemeral_config_params(self) -> Dict[str,Any]:
        """Ephemeral configuration parameters of the cloud.

        An abstract property: an in-RAM dictionary that stores
        all the ephemeral the configuration parameters of the cloud.
        """
        raise NotImplementedError


    @property
    # @classmethod
    def default_ephemeral_params(cls) -> Dict[str, Any]:
        """Default values for ephemeral parameters .
        """
        result = dict(
            install_requires=""
            ,python_requires=""
            ,shared_import_statements = ""
            )
        return result


    @property
    def python_requires(self) -> str:
        """A version specifier for Python.

        An ephemeral property that specifies Python versions,
        which are supported by a currently running P_Cloud instance.
        Its format follows setuptools' python_requires format.
        """
        return self.ephemeral_config_params["python_requires"]


    @property
    def install_requires(self) -> str:
        """Packages that a P_Cloud instance minimally needs to run.

        An ephemeral property that specifies packages
        (and their versions), needed by the currently running P-Cloud.
        The property's format follows setuptools' install_requires format.
        """
        return self.ephemeral_config_params["install_requires"]


    @property
    def shared_import_statements(self) -> str:
        """Import statements that are shared across all cloudized functions.

        An ephemeral property that contains import statements, which
        will be executed before running every cloudized function.
        The format of the property is a sequence of Python import statements.
        """
        return self.ephemeral_config_params["shared_import_statements"]


    @property
    def p_idempotency_checks(self) -> Optional[float]:
        """ Probability of stochastic idempotency checks.

        If a function's output has been stored in a cache,
        when the function is called with the same arguments the next time,
        it will reuse cached output with probability (1-p_idempotency_checks).
        With probability p_idempotency_checks the function will be
        executed once again, and its output will be compared with
        the cached one: if they differ, idempotency check will fail and
        an exception will be thrown.

        p_idempotency_checks==1 means 'never re-use cached values'.
        p_idempotency_checks==0 means 'always re-use cached values
        when possible'.

        Even when  p_idempotency_checks==0, there are possible
        scenarios when the function will be executed two or more times.
        E.g. the function takes long time to execute, so before it finishes
        (and stores its output in the cache) another instance of the same
        function with the same arguments might be launched
        on a different computer in the cloud. In such a case,
        when both function calls complete, their outputs will be compared
        even if p_idempotency_checks==0. If the outputs differ,
        an exception will be raised. To completely prevent idempotency checks,
        p_idempotency_checks must be set to None.

        p_idempotency_checks==None means 'never conduct idempotency checks'.
        """
        return self.persistent_config_params["p_idempotency_checks"]


    def push_value(self, value:Any) -> PValueAddress:
        """ Add a value to value_store"""
        key = PValueAddress(value)
        if not key in self.value_store:
            self.value_store[key] = value
        return key


    def brief_self_check(self):
        """Perform fast consistency ckeck for P-Cloud."""
        assert len(self.ephemeral_config_params) >= 0
        assert len(self.persistent_config_params) >= 0
        assert len(self.value_store) >= 0
        assert len(self.func_output_store) >= 0
        assert len(self.crash_history) >= 0
        assert len(self.event_log) >= 0
        assert isinstance(self.p_idempotency_checks, (int,float,type(None)))
        if not self.p_idempotency_checks is None:
            assert 0 <= self.p_idempotency_checks <= 1
        assert isinstance(self.install_requires, str)
        assert isinstance(self.python_requires, str)
        assert isinstance(self.shared_import_statements, str)
        for i in range(1000):
            random_int = randint(1, 1_000_000_000_000)
            random_int_addr = PValueAddress(random_int, push_to_cloud=False)
            if random_int_addr in self.value_store:
                continue
            else:
                self.push_value(random_int)
                assert random_int_addr in self.value_store
                assert random_int == self.value_store[random_int_addr]
                break
        # TODO: add more checks


    def full_self_check(self):
        """Perform comprehensive consistency check for P-Cloud."""
        self.brief_self_check()
        # TODO: add more checks


    @abstractmethod
    def cloudize_function(self, a_func:Callable) -> PCloudizedFunction:
        """Decorator which cloudizes a user-provided idempotent function"""
        raise NotImplementedError


class ExceptionInfo:
    """ Helper class for remote logging, encapsulates exception/environment info.

    This class is used by P_Cloud_Implementation objects to log information
    in P_Cloud.crash_history persistent store.
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
    cloudize_function(a_func:Callable) -> Callable
            Decorator that cloudizes a user-provided idempotent function.

    push_value(value:Any) -> PValueAddress
            Add a value to value_store.

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

    crash_history: SimplePersistentDict
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

    persistent_config_params: SimplePersistentDict
            An abstract property: a persistent dict-like object that
            stores all the configuration parameters of the cloud.

    ephemeral_config_params: dict
            An abstract property: an in-RAM dictionary that stores
            all the ephemeral the configuration parameters of the cloud.

    python_requires: str
            An abstract property: version specifier for Python.
            Defines which Python versions are supported by a P_Loud instance
            to run. Its format follows setuptools' python_requires format.

    install_requires: Optional[str]
            An abstract property: minimally required dependencies.
            The list of packages that a P_Cloud instance minimally needs
            to run. Its format follows setuptools' install_requires format.

    shared_import_statements: Optional[str]
            An abstract property: contains import statements, which
            will be executed before running every cloudized function.
            The format of the property is a sequence of Python import statements.

    p_idempotency_checks : Optional[float]
            Probability of stochastic idempotency checks. If a functions
            output has been stored on a cache, when the function is
            called with the same arguments next time, it will re-use
            cached output with probability (1-p_idempotency_checks).
            With probability p_idempotency_checks the function will be
            executed once again, and its output will be compared with
            the cached one: if they differ, idempotency check will fail.

    original_functions : dict[str, Callable]
            A dictionary with original (before application of the
            @cloudize_function decorator) versions of all cloudized
            functions in P_Cloud. Keys are the names of the
            functions.

    cloudized_functions: dict[str, PCloudizedFunction]
            A dictionary with modified (as a result of  applying
            the @cloudize_function decorator) versions of all
            cloudized functions in P_Cloud. Keys are the names
            of the functions.
    """
    _single_instance:Optional[P_Cloud_Implementation] = None

    original_functions: dict[str, Callable] = dict()
    cloudized_functions: dict[str, PCloudizedFunction] = dict()

    base_dir:str = ""

    _old_excepthook: Optional[Callable] = None
    _is_running_inside_IPython: Optional[bool] = None
    _randomizer:Random = Random()
    """We are using a new instance of Random object that does not share 
    its seed with other Random objects.
    This is done to ensure correct parallelization via randomization 
    in cases when a cloudized function explicitly sets seed value 
    for the default Random object, which it might do in order 
    to be qualified as a pure function."""

    _instance_counter:int = 0
    _init_signature_hash_address = None

    def __init__(self
                 , base_dir:str = "P_Cloud"
                 , persist_config_init: Dict[str, Any] = None
                 , persist_config_update: Dict[str, Any] = None
                 , ephem_config_init: Dict[str, Any] = None
                 , **kwargs):

        P_Cloud_Implementation._single_instance = self

        assert not os.path.isfile(base_dir)
        if not os.path.isdir(base_dir):
            os.makedirs(base_dir,exist_ok=True)
        assert os.path.isdir(base_dir)
        self.base_dir = os.path.abspath(base_dir)

        super().__init__(persist_config_init=persist_config_init
                         , persist_config_update=persist_config_update
                         , ephem_config_init=ephem_config_init
                         , **kwargs)

        self._register_exception_handlers()

    def __post__init__(self, *args, **kwargs) -> None:
        """ Enforce arguments-based singleton pattern. """
        P_Cloud_Implementation._instance_counter += 1
        persistent_params = dict()
        for k in self.persistent_config_params:
            assert len(k)==1
            k_str = k[0]
            persistent_params[k_str] = self.persistent_config_params[k_str]
        config_signature = (type(self)
            , KwArgsDict(**persistent_params)
            , KwArgsDict(**self.ephemeral_config_params))
        config_signature_hash = PValueAddress(
            data=config_signature
            , push_to_cloud=False)
        if P_Cloud_Implementation._instance_counter == 1:
            P_Cloud_Implementation._config_signature_hash_address = (
                config_signature_hash)
            P_Cloud_Implementation._single_instance = self
        else:
            assert config_signature_hash == (
                P_Cloud_Implementation._config_signature_hash_address), (
                "You can't have several P_Cloud instances with different "
                "types and/or configuration params.")


    @staticmethod
    def _reset() -> None:
        """Cleanup all data for P_Cloud_Implementation. Never use this method."""
        P_Cloud_Implementation._instance_counter = 0
        P_Cloud_Implementation._config_signature_hash_address = None
        P_Cloud_Implementation._single_instance = None
        P_Cloud_Implementation.original_functions = dict()
        P_Cloud_Implementation.cloudized_functions = dict()


    def _register_exception_handlers(self) -> None:
        """ Intersept & redirect unhandled exceptions to self.crash_history """

        P_Cloud_Implementation._old_excepthook = sys.excepthook

        def cloud_excepthook(exc_type, exc_value, trace_back):
            exc_event = ExceptionInfo(exc_type, exc_value, trace_back)
            post_log_entry(entry=exc_event, category="exception")
            P_Cloud_Implementation._old_excepthook(
                exc_type, exc_value, trace_back)
            return

        sys.excepthook = cloud_excepthook

        def cloud_excepthandler( _, exc_type, exc_value , trace_back, tb_offset=None):
            exc_event = ExceptionInfo(exc_type, exc_value, trace_back)
            post_log_entry(entry = exc_event, category = "exception")
            traceback.print_exception(exc_type, exc_value, trace_back)
            return

        try:  # if we are inside a notebook
            get_ipython().set_custom_exc(
                (BaseException,), cloud_excepthandler)
            self._is_running_inside_IPython = True
        except:
            self._is_running_inside_IPython = False


    def _process_import_statements(self
            ,import_statements: Optional[str]) -> None:
        if import_statements is None:
            return
        # TODO: find if there is a less polluting way of doing this
        for frame_info in inspect.stack():
            exec(import_statements, frame_info.frame.f_globals)


    def sync_local_inprocess_function_call(
            self
            ,fo_address:PFuncOutputAddress
            ) -> None:
        """ Perform a local synchronous call for a cloudized function.

        This method should not be called directly. Instead,
        use the traditional syntax below while calling a cloudized function:
        func_name(**kwargs)
        """

        original_function = self.original_functions[fo_address._function_name]

        if self.p_idempotency_checks == 0 or self.p_idempotency_checks is None:
            use_cached_output = True
        elif self.p_idempotency_checks >= 1:
            use_cached_output = False
        else:
            use_cached_output = (
                    self.p_idempotency_checks < self._randomizer.uniform(0, 1))

        if not (use_cached_output and fo_address in self.func_output_store):
            result = original_function(**fo_address._arguments)
            result_key = self.push_value(result)

            if (self.p_idempotency_checks is not None
                and fo_address in self.func_output_store):
                # TODO: change to a "raise" statement
                assert self.func_output_store[fo_address] == result_key, (
                    "Stochastic purity check has failed")
            else:
                self.func_output_store[fo_address] = result_key


    def async_local_subprocess_function_call(self
            ,fo_address:PFuncOutputAddress
            ) -> None:
        """ Perform an asynchronous subprocess call for a cloudized function.

        This method should not be called directly. Instead, use the syntax
        below (requires a functions first to be added to a cloud):
        func_name.async_subprocess(**kwargs)
        """
        raise NotImplementedError


    def sync_local_subprocess_function_call(self
            ,address: PFuncOutputAddress
            ) -> None:
        """ Perform a synchronous subprocess call for a cloudized function.

        This method should not be called directly. Instead, use the syntax
        below (requires a functions first to be added to a cloud):
        func_name.sync_subprocess(**kwargs)
        """
        raise NotImplementedError


    def async_incloud_function_call(self
            ,fo_address: PFuncOutputAddress
            )-> None:
        """ Perform a remote asynchronous call for a cloudized function.

        This method should not be called directly. Instead, use the syntax
        below (requires a functions first to be added to a cloud):
        func_name.async_remote(**kwargs)
        """
        raise NotImplementedError


    # def sync_parallel_function_call(self
    #         , arg_list: List[PFuncOutputAddress]
    #         ) -> None:
    #     """Synchronously execute multiple instances of a cloudized function.
    #
    #     This method should not be called directly. Instead, use the syntax
    #     below (requires a functions first to be added to a cloud):
    #     func_name.sync_parallel( kw_args(..) for .. in .. )
    #     """
    #
    #     raise NotImplementedError


    # def async_parallel_function_call(self
    #         , arg_list: List[PFuncOutputAddress]
    #         ) -> None:
    #     """Asynchronously execute multiple instances of a cloudized function.
    #
    #     This function should not be called directly. Instead, use the syntax
    #     below (requires a functions first to be added to a cloud):
    #     func_name.async_parallel( kw_args(..) for .. in .. )
    #     """
    #     raise NotImplementedError


    def check_if_ready(
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


    def cloudize_function(self, a_func:Callable) -> PCloudizedFunction:
        """Decorator which cloudizes a user-provided idempotent function."""
        assert callable(a_func)
        assert not isinstance(a_func, PCloudizedFunction), (
            "A function is not allowed to be added to the cloud twice")
        assert hasattr(a_func,"__name__"), (
            "Nameless functions can not be cloudized")
        assert a_func.__name__ != "<lambda>", (
            "Lambda functions can not be cloudized")
        assert a_func.__closure__ is None, (
            "Closures can not be cloudized")
        assert "<locals>" not in a_func.__qualname__ , (
            "Closures can not be cloudized")


        # TODO: change to custom exception
        assert a_func.__name__ not in self.original_functions, (
            f"Function {a_func.__name__} has already been added to the cloud."
            + "Can't add one more time.")

        self.original_functions[a_func.__name__] = a_func

        wrapped_function = PCloudizedFunction(a_func.__name__)

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
                 , persist_config_init: Dict[str,Any] = None
                 , persist_config_update: Dict[str,Any] = None
                 , ephem_config_init: Dict[str,Any] = None
                 , base_dir:str = "SharedStorage_P2P_Cloud"
                 , restore_from:Optional[PFuncOutputAddress]=None
                 , **kwargs
                 ):

        self._value_store = FileDirDict(
            dir_name=os.path.join(base_dir, "value_store")
            ,file_type="pkl")

        self._func_output_store = FileDirDict(
            dir_name=os.path.join(base_dir, "func_output_store")
            ,file_type="pkl")

        self._crash_history = FileDirDict(
            dir_name=os.path.join(base_dir, "exception_log")
            ,file_type="json")

        self._event_log = FileDirDict(
            dir_name=os.path.join(base_dir, "event_log")
            ,file_type="json")

        self._ephemeral_config_params = dict()

        self._persistent_config_params = FileDirDict(
            dir_name=os.path.join(base_dir, "persistent_config_params")
            , file_type="json")

        super().__init__(persist_config_init = persist_config_init
                         ,persist_config_update = persist_config_update
                         ,ephem_config_init = ephem_config_init
                         ,base_dir=base_dir
                         ,**kwargs)

        self._temp_dir = None

        if restore_from is None:
            return

        assert persist_config_init is None
        assert persist_config_update is None
        assert ephem_config_init is None

        #########################################################

        func_call_signature_addr = PValueAddress.from_strings(
            prefix = restore_from.prefix
            , descriptor = restore_from.descriptor
            , hash_value = restore_from.hash_value)

        func_call_signature = func_call_signature_addr.get()
        assert isinstance(func_call_signature,PFunctionCallSignature)
        func_snapshot = func_call_signature.function_addr.get()
        assert isinstance(func_snapshot, PCloudizedFunctionSnapshot)

        self.ephemeral_config_params["install_requires"] = (
            func_snapshot.install_requires)
        self.ephemeral_config_params["python_requires"] = (
            func_snapshot.python_requires)
        self.ephemeral_config_params["shared_import_statements"] = (
            func_snapshot.shared_import_statements)

        all_functions = func_snapshot.shared_import_statements
        all_functions += "\nimport pythagoras\n"

        for f_name in func_snapshot.source_with_dependencies:
            all_functions += "\n\n"
            all_functions +="@pythagoras.P_Cloud_Implementation"
            all_functions +="._single_instance.cloudize_function\n"
            all_functions += func_snapshot.source_with_dependencies[f_name]

        self._temp_dir = tempfile.mkdtemp()

        all_functions_b = all_functions.encode()
        hash_object = hashlib.md5(all_functions_b)
        full_digest_str = base64.b32encode(hash_object.digest()).decode()
        temp_package_name = "pythagoras_cloud_funcs_" +full_digest_str[:20]
        temp_filename = temp_package_name +".py"
        full_temp_filename = os.path.join(self._temp_dir,temp_filename)


        with open(full_temp_filename, "w") as temp_file:
            temp_file.write(all_functions)

        sys.path.append(self._temp_dir)

        # TODO: find if there is a less polluting way of doing this
        for f_name in func_snapshot.source_with_dependencies:
            for frame_info in inspect.stack():
                    f_n_code = f"from {temp_package_name} import {f_name}"
                    f_globals = frame_info.frame.f_globals
                    exec(f_n_code, f_globals)


    def __del__(self):
        if self._temp_dir is not None:
            shutil.rmtree(self._temp_dir, ignore_errors=True)


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

    @property
    def ephemeral_config_params(self) -> Dict[str,Any]:
        """Ephemeral configuration parameters of the cloud.

        An abstract property: an in-RAM dictionary that stores
        all the ephemeral the configuration parameters of the cloud.
        """
        return self._ephemeral_config_params


    @property
    def persistent_config_params(self) -> SimplePersistentDict:
        """Persistent configuration parameters of the cloud.

         An abstract property: a persistent dict-like object that
        stores all the configuration parameters of the cloud.
        """
        return self._persistent_config_params


    def async_incloud_function_call(self
                                  ,fo_address: PFuncOutputAddress
                                  ) -> None:
        """Emulate asynchronous remote execution of a function.

        Instead of actual asynchronous remote  execution,
        it performs local synchronous one.
        """
        self.sync_local_inprocess_function_call(fo_address)


    def async_local_subprocess_function_call(self
            ,address:PFuncOutputAddress
            ) -> None:
        """ Perform an asynchronous subprocess call for a cloudized function.

        This method should not be called directly. Instead, use the syntax
        below (requires a functions first to be added to a cloud):
        func_name.async_subprocess(**kwargs)
        """

        subprocess_command = [sys.executable
            , "-m"
            , "pythagoras"
            , type(self).__name__
            , self.base_dir
            , address.prefix
            , address.descriptor
            , address.hash_value]

        subprocess_results = subprocess.Popen(subprocess_command)


    def sync_local_subprocess_function_call(self
            ,address:PFuncOutputAddress
            ) -> None:
        """ Perform a synchronous subprocess call for a cloudized function.

        This method should not be called directly. Instead, use the syntax
        below (requires a functions first to be added to a cloud):
        func_name.sync_subprocess(**kwargs)
        """

        subprocess_command = [sys.executable
            , "-m"
            , "pythagoras"
            , type(self).__name__
            , self.base_dir
            , address.prefix
            , address.descriptor
            , address.hash_value]

        subprocess_results = subprocess.run(
            subprocess_command
            , capture_output=True)

        assert address.ready, (
            f"Subprocess was not able to complete successfully: {subprocess_results.stderr.decode()}")


    # def sync_parallel_function_call(self
    #         , arg_list: List[PFuncOutputAddress]
    #         ) -> None:
    #     """Emulate parallel execution of multiple instances of function.
    #
    #     Instead of actual remote parallel execution,
    #     it performs randomized local sequential execution .
    #     """
    #
    #     input_list = list(arg_list)
    #     for a in input_list:
    #         assert isinstance(a, PFuncOutputAddress)
    #
    #     shuffled_input_list = deepcopy(input_list)
    #     self._randomizer.shuffle(shuffled_input_list)
    #
    #     for a in shuffled_input_list:
    #         a.function._sync_inprocess_v(**a.arguments)
    #         # We are intentionally not using here
    #         # self.sync_local_inprocess_function_call(a)
    #         # in order to enable Pythagoras' event logging and
    #         # exception reporting mechanisms


    # def async_parallel_function_call(self
    #         ,arg_list: List[PFuncOutputAddress]
    #         ) -> None:
    #     """Emulate parallel async execution of multiple instances of function.
    #
    #     Instead of actual remote asynchronous parallel execution,
    #     it performs randomized local sequential synchronous execution.
    #     """
    #     self.sync_parallel_function_call(arg_list)


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


    def p_idempotency_checks(self) -> float:
        """ Probability of stochastic purity checks.

        If a functions output has been stored on a cache, when the function is
        called with the same arguments next time, it will re-use
        cached output with probability (1-p_idempotency_checks).
        With probability p_idempotency_checks the function will be
        executed once again, and its output will be compared with
        the cached one: if they differ, purity check will fail.
        """
        return self.base_cloud.p_idempotency_checks

    def cloudize_function(self, a_func):
        """Decorator which cloudizes a user-provided idempotent function"""
        return self.base_cloud.cloudize_function(a_func)


    def install_requires(self) -> Optional[str]:
        return self.base_cloud.install_requires


    def python_requires(self) -> str:
        return self.base_cloud.python_requires


    def shared_import_statements(self) -> str:
        return self.base_cloud.shared_import_statements


def post_log_entry(
        entry:Any
        , *
        , name_prefix:Optional[str] = None
        , category:Optional[str] = None
        , name_generator:Callable = uuid.uuid4) -> None:
    """Determine event key and post an event/exception."""

    if name_prefix is None:
        name_prefix = get_long_infoname(entry)
    assert isinstance(name_prefix, str)
    name_prefix = replace_unsafe_chars(name_prefix, "_")

    if category is None:
        if isinstance(entry,BaseException):
            category = "exception"
        else:
            category = "event"

    assert isinstance(category,str)
    category = category.lower()
    assert category in {"event","exception"}

    cloud = P_Cloud_Implementation._single_instance
    if category == "event":
        destination = cloud.event_log
    else:
        destination = cloud.crash_history

    event_key = detect_local_variable_in_callstack(
        "__fo_addr__", PFuncOutputAddress)

    if event_key is None:
        event_key = ("unattributed",)
    else:
        event_key = tuple(event_key)

    event_id = str(name_generator())
    event_id = name_prefix+"_"+event_id

    event_key = event_key+(event_id,)
    destination[event_key] = entry
