from typing import Dict, Any
from pythagoras._01_foundational_objects.value_addresses import ValueAddr
import pythagoras as pth


class SortedKwArgs(dict):
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
            assert not isinstance(value, SortedKwArgs)
            self[k] = value

    def unpack(self) -> Dict[str, Any]:
        """ Restore values based on their hash addresses."""
        unpacked_copy = dict()
        for k,v in self.items():
            if isinstance(v, ValueAddr):
                unpacked_copy[k] = pth.value_store[v]
            else:
                unpacked_copy[k] = v
        return unpacked_copy

    def pack(self) -> Dict[str, ValueAddr]:
        """ Replace values with their hash addresses."""
        packed_copy = dict()
        for k,v in self.items():
            packed_copy[k] = ValueAddr(v)
        return packed_copy


class PackedKwArgs(SortedKwArgs):
    """ A class that encapsulates keyword arguments for a function call."""

    def __init__(self, **kargs):
        """ Replace values in a dict with their hash addresses.

        The constructor  "normalizes" the dictionary by sorting the keys
        and replacing values with their hash addresses
        in order to always get the same hash values
        for the same lists of arguments.
        """
        super().__init__()
        packed_copy = SortedKwArgs(**kargs).pack()
        for k in packed_copy:
            self[k] = packed_copy[k]


class UnpackedKwArgs(SortedKwArgs):
    """ A class that encapsulates keyword arguments for a function call."""

    def __init__(self, **kargs):
        """ Ensures that all values are unpacked.
        """
        super().__init__()
        unpacked_copy = SortedKwArgs(**kargs).unpack()
        for k in unpacked_copy:
            self[k] = unpacked_copy[k]

