from __future__ import annotations

from copy import deepcopy
from typing import Any, Optional, Type, TypeVar

import pythagoras as pth
from pythagoras._01_foundational_objects.hash_addresses import HashAddress

T = TypeVar("T")

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

        if hasattr(data, "get_ValueAddress"):
            self.str_chain = deepcopy(data.get_ValueAddress().str_chain)
            return

        assert not isinstance(data,HashAddress), (
            "get_ValueAddress is the only way to "
            + "convert HashAddress into ValueAddress")

        prefix = self._build_prefix(data)
        hash_value = self._build_hash_value(data)

        super().__init__(prefix, hash_value)

        if push_to_cloud and not (self in pth.value_store):
            pth.value_store[self] = data

    def get_ValueAddress(self):
        return self

    @property
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


