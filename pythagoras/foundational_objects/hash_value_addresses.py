from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, Optional, Type, TypeVar, Dict, List, Callable

from persidict import SafeStrTuple, replace_unsafe_chars

import pythagoras as pth
from pythagoras.python_utils import get_long_infoname
from pythagoras.misc_utils import *

T = TypeVar("T")

class HashAddress(SafeStrTuple, ABC):
    """A globally unique hash-based address of an object.

    Two objects with exactly the same type and value will always have
    exactly the same HashAddress-es.

    A HashAddress consists of 2 strings: a prefix, and a hash.
    A prefix contains human-readable information about an object's type.
    A hash string contains the object's hash signature. It may begin with
    an optional descriptor, which provides additional human-readable
    information about the object's structure / value.
    """

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

        prfx = get_long_infoname(x).lower()

        return prfx


    @staticmethod
    def _build_hash_value(x: Any) -> str:
        """Create a URL-safe hashdigest for an object."""

        if (hasattr(x, "shape") and hasattr(x.shape, "__iter__")
                and callable(x.shape.__iter__) and not callable(x.shape)):
            descriptor, connector = "shape_", "_x_"
            for n in x.shape:
                descriptor += str(n) + connector
            descriptor = descriptor[:-len(connector)] + "_"
        elif hasattr(x, "__len__") and callable(x.__len__):
            descriptor = "len_" + str(len(x)) + "_"
        else:
            descriptor = ""

        descriptor = replace_unsafe_chars(descriptor, replace_with="_")
        raw_hash_signature = get_hash_signature(x)
        hash_value = descriptor + raw_hash_signature

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

    def __ne__(self, other) -> bool:
        """Return self!=other. """
        return not (self == other)


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

        if push_to_cloud and not (self in pth.value_store):
            pth.value_store[self] = data

    def ready(self):
        """Check if address points to a value that is ready to be retrieved."""
        return self in pth.value_store


    def get(self, timeout:Optional[int] = None) -> Any:
        """Retrieve value, referenced by the address"""
        return pth.value_store[self]

    def get_typed(self
            ,expected_type:Type[T]
            ,timeout:Optional[int]=None
            ) -> T:
        """Retrieve value with a known type """
        result = self.get(timeout)
        assert isinstance(result, expected_type)
        return result


