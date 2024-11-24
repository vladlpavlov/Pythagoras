from __future__ import annotations

from typing import Any, Optional, Type, TypeVar

from pythagoras import BasicPortal
# from pythagoras._010_basic_portals.portal_getters import get_portal
from pythagoras._030_data_portals.hash_addresses import HashAddr
from pythagoras._030_data_portals.data_portals import (
    DataPortal)

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

    def __init__(
            self
            , data: Any
            , portal:Optional[DataPortal] = None
            , *args
            , **kwargs):
        assert len(args) == 0
        assert len(kwargs) == 0

        portal = DataPortal.get_portal(portal)

        with portal:
            if hasattr(data, "get_ValueAddr"):
                data_value_addr = data.get_ValueAddr()
                prefix = data_value_addr.prefix
                hash_value = data_value_addr.hash_value
                super().__init__(prefix, hash_value, portal=portal)
                if portal != data_value_addr.portal and (
                        not self in portal.value_store):
                    data = data_value_addr.get()
                    portal.value_store[self] = data
                self._ready = True
                return

        assert not isinstance(data, HashAddr), (
                "get_ValueAddr is the only way to "
                + "convert HashAddr into ValueAddr")

        prefix = self._build_prefix(data)
        hash_value = self._build_hash_value(data)
        super().__init__(prefix, hash_value, portal=portal)

        with portal:
            portal.value_store[self] = data
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
    def portal(self) -> DataPortal:
        return self._portal

    @property
    def _ready_in_current_portal(self) -> bool:
        if not hasattr(self, "_ready"):
            result = self in self.portal.value_store
            if result:
                self._ready = True
            return result
        assert self._ready
        return True


    @property
    def _ready_in_noncurrent_portals(self) -> bool:
        for portal in DataPortal.get_noncurrent_portals():
            with portal:
                if self in portal.value_store:
                    data = portal.value_store[self]
                    with self.portal:
                        self.portal.value_store[self] = data
                    self._ready = True
                    return True
        return False

    @property
    def ready(self) -> bool:
        """Check if address points to a value that is ready to be retrieved."""
        if hasattr(self, "_ready"):
            assert self._ready
            return True
        if self._ready_in_current_portal:
            self._ready = True
            return True
        if self._ready_in_noncurrent_portals:
            self._ready = True
            return True
        return False


    def get_from_current_portal(self, timeout:Optional[int] = None) -> Any:
        """Retrieve value, referenced by the address, from the current portal"""

        if hasattr(self, "_value"):
            return self._value

        with self.portal:
            result = self.portal.value_store[self]
            self._value = result
            return result


    def get_from_noncurrent_portals(self, timeout:Optional[int] = None) -> Any:
        """Retrieve value, referenced by the address, from noncurrent portals"""
        for portal in DataPortal.get_noncurrent_portals():
            try:
                with portal:
                    result = portal.value_store[self]
                with self.portal:
                    self.portal.value_store[self] = result
                self._value = result
                return result
            except:
                continue

        raise KeyError(f"ValueAddr {self} not found in any portal")


    def get(self, timeout:Optional[int] = None) -> Any:
        """Retrieve value, referenced by the address from any available portal"""

        if hasattr(self, "_value"):
            return self._value

        try:
            result = self.get_from_current_portal(timeout)
            return result
        except:
            result = self.get_from_noncurrent_portals(timeout)
            return result


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
        self._portal = None
        self.capture_portal()

    def __copy__(self):
        result = self.from_strings(
            prefix=self.prefix
            , hash_value=self.hash_value
            , portal=self.portal
            , assert_readiness=False)
        return result