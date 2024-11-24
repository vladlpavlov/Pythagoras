from typing import Dict, Any
from pythagoras._030_data_portals.value_addresses import ValueAddr
from pythagoras._030_data_portals.data_portals import DataPortal


class SortedKwArgs(dict):
    """ A class that encapsulates keyword arguments for a function call.

    It  "normalizes" the dictionary by sorting the keys
    and replacing values with their hash addresses
    in order to always get the same hash values
    for the same lists of arguments.
    """

    def __init__(self, **kargs):
        """Sort the keys in the dictionary."""
        super().__init__()
        for k in sorted(kargs):
            value = kargs[k]
            assert not isinstance(value, SortedKwArgs)
            self[k] = value

    def unpack(self, portal:DataPortal) -> Dict[str, Any]:
        """ Restore values based on their hash addresses."""
        with portal:
            unpacked_copy = dict()
            for k,v in self.items():
                if isinstance(v, ValueAddr):
                    unpacked_copy[k] = portal.value_store[v]
                else:
                    unpacked_copy[k] = v
            return unpacked_copy

    def pack(self, portal:DataPortal) -> Dict[str, ValueAddr]:
        """ Replace values with their hash addresses."""
        with portal:
            packed_copy = dict()
            for k,v in self.items():
                packed_copy[k] = ValueAddr(v, portal = portal)
            return packed_copy

