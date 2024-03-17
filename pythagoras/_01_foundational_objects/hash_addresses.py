from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional, Type, TypeVar

from persidict import SafeStrTuple, replace_unsafe_chars

from pythagoras._01_foundational_objects.hash_and_random_signatures import (
    get_hash_signature)

T = TypeVar("T")

class HashAddr(SafeStrTuple, ABC):
    """A globally unique hash-based address of an object.

    Two objects with exactly the same type and value will always have
    exactly the same HashAddr-es.

    A HashAddr consists of 2 strings: a prefix, and a hash.
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

        prfx = x.__class__.__name__.lower()

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
                     ) -> HashAddr:
        """(Re)construct address from text representations of prefix and hash"""

        assert prefix, "prefix must be a non-empty string"
        assert hash_value, "hash_value must be a non-empty string"

        address = cls.__new__(cls)
        super(cls, address).__init__(prefix, hash_value)
        if assert_readiness:
            assert address.ready
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
        return type(self) == type(other) and self.str_chain == other.str_chain

    def __ne__(self, other) -> bool:
        """Return self!=other. """
        return not (self == other)