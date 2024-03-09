from __future__ import annotations

import sys
from abc import abstractmethod
from copy import deepcopy
from typing import Optional, Any, Type, TypeVar, Dict

from joblib.hashing import NumpyHasher, Hasher
from persidict import SafeStrTuple, PersiDict, replace_unsafe_chars

from pythagoras.python_utils import get_long_infoname

T = TypeVar("T")

# value_store:Optional[PersiDict] = None

def set_value_store(store:PersiDict) -> None:
    """Set a global value store."""
    global value_store
    value_store = store

class HashAddress(SafeStrTuple):
    """A globally unique hash-based address.

    Consists of 2 strings. Includes a human-readable prefix, and a hash.
    A hash string may begin an optional descriptor,
    which provides additional human-readable information about the object.
    """

    _hash_type: str = "sha256"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def prefix(self) -> str:
        return self.str_chain[0]

    @property
    def hash_value(self) -> str:
        return self.str_chain[1]

    @staticmethod
    def _build_prefix(x: Any) -> str:
        """Create a short human-readable summary of an object."""

        prfx = get_long_infoname(x)

        return prfx

    @staticmethod
    def _build_descriptor(x: Any) -> Optional[str]:
        """Create a short summary of object's length/shape."""

        dscrptr = ""

        #### FROM OLD CODE #############################
        # if isinstance(x,PFunctionCallSignature):
        #     # TODO: replace with proper OOP approach
        #     dscrptr = x.get_snpsht_id()
        ################################################

        if (hasattr(x, "shape")
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

        return replace_unsafe_chars(dscrptr, replace_with="_")


    @staticmethod
    def _build_hash_value(x: Any) -> str:
        """Create a URL-safe hashdigest for an object."""

        if 'numpy' in sys.modules:
            hasher = NumpyHasher(hash_name=HashAddress._hash_type)
        else:
            hasher = Hasher(hash_name=HashAddress._hash_type)
        raw_hash_value = hasher.hash(x) #TODO: switch to Base32

        descriptor = HashAddress._build_descriptor(x)
        hash_value = descriptor + "_" + raw_hash_value

        return hash_value


    @classmethod
    def from_strings(cls, *
                     , prefix:str
                     , hash_value:str
                     , assert_readiness:bool=True
                     ) -> HashAddress:
        """(Re)construct address from text representations of prefix and hash"""

        assert prefix, "prefix must be a non-empty string"
        assert hash_value, "hash_value must be a non-empty string"

        address = cls.__new__(cls)
        super(cls, address).__init__(prefix, hash_value)
        if assert_readiness:
            assert address.ready()
        return address


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
        return type(self) == type(other) and self.str_chain == other.str_chain


class ValueAddress(HashAddress):
    """A globally unique address of an immutable value.

    ValueAddress is a universal global identifier of any (constant) value.
    Using only the value's hash should (theoretically) be enough to
    uniquely address all possible data objects that the humanity  will create
    in the foreseeable future (see, for example ipfs.io).

    However, an address also includes a prefix and an optional descriptor.
    It makes it easier for humans to interpret an address,
    and further decreases collision risk.
    """

    def __init__(self, data: Any, push_to_cloud:bool=True, *args, **kwargs):
        global value_store
        assert len(args) == 0
        assert len(kwargs) == 0

        if isinstance(data, ValueAddress):
            self.str_chain = deepcopy(data.str_chain)
            return

        assert not isinstance(data,HashAddress), (
            "ValueAddress is the only HashAddress which is allowed "
            + "to be converted to ValueAddress")

        prefix = self._build_prefix(data)
        hash_value = self._build_hash_value(data)

        super().__init__(prefix, hash_value)

        if push_to_cloud and not (self in value_store):
            value_store[self] = data

    def ready(self):
        """Check if address points to a value that is ready to be retrieved."""
        return self in value_store


    def get(self, timeout:Optional[int] = None) -> Any:
        """Retrieve value, referenced by the address"""
        return value_store[self]

    def get_typed(self
            ,expected_type:Type[T]
            ,timeout:Optional[int]=None
            ) -> T:
        """Retrieve value with a known type """
        result = self.get(timeout)
        assert isinstance(result, expected_type)
        return result


class PackedKwArgs(dict):
    """ A class that encapsulates keyword arguments for a function call."""

    def __init__(self, **kargs):
        """ Replace values in a dict with their hash addresses.

        The constructor  "normalizes" the dictionary by sorting the keys
        and replacing values with their hash addresses
        in order to always get the same hash values
        for the same lists of arguments.
        """
        super().__init__()
        for k in sorted(kargs):
            value = kargs[k]
            if isinstance(value, ValueAddress):
                self[k] = value
            else:
                key = ValueAddress(value)
                self[k] = key

    def unpack(self) -> Dict[str, Any]:
        """ Restore values based on their hash addresses."""
        unpacked_copy = dict()
        for k,v in self.items():
            unpacked_copy[k] = value_store[v]
        return unpacked_copy
