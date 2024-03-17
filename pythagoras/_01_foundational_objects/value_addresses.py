from __future__ import annotations

from copy import deepcopy
from typing import Any, Optional, Type, TypeVar

import pythagoras as pth
from pythagoras._01_foundational_objects.hash_addresses import HashAddr

T = TypeVar("T")

class ValueAddr(HashAddr):
    """A globally unique address of an immutable value.

    ValueAddr is a universal global identifier of any (constant) value.
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

        if hasattr(data, "get_ValueAddr"):
            self.str_chain = deepcopy(data.get_ValueAddr().str_chain)
            return

        assert not isinstance(data, HashAddr), (
            "get_ValueAddr is the only way to "
            + "convert HashAddr into ValueAddr")

        prefix = self._build_prefix(data)
        hash_value = self._build_hash_value(data)

        super().__init__(prefix, hash_value)

        if push_to_cloud and not (self in pth.value_store):
            pth.value_store[self] = data

        self._value = data
        self._ready = True

    def _invalidate_cache(self):
        if hasattr(self, "_value"):
            del self._value
        if hasattr(self, "_ready"):
            del self._ready

    def get_ValueAddr(self):
        return self

    @property
    def ready(self):
        """Check if address points to a value that is ready to be retrieved."""
        if not hasattr(self, "_ready"):
            self._ready = self in pth.value_store
        return self._ready


    def get(self, timeout:Optional[int] = None) -> Any:
        """Retrieve value, referenced by the address"""
        if not hasattr(self, "_value"):
            self._value = pth.value_store[self]
        return self._value

    def get_typed(self
            ,expected_type:Type[T]
            ,timeout:Optional[int]=None
            ) -> T:
        """Retrieve value with a known type """
        result = self.get(timeout)
        assert isinstance(result, expected_type)
        return result

    def __getstate__(self):
        state = dict(str_chain=self.str_chain)
        return state

    def __setstate__(self, state):
        self.str_chain = state["str_chain"]