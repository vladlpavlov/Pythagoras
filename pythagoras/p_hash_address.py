import pandas as pd
import numpy as np
import sys
from typing import NamedTuple, Any, List
from joblib.hashing import NumpyHasher,Hasher


class PHashAddress:
    """A globally unique address of an immutable value. Consists of a human-readable prefix and a hash code.

    PHashAddress is a universal global identifier of any (constant) value.
    Using only the value's hash should (theoretically) be enough to uniquely address
    all possible data objects that the humanity  will create in the foreseeable future
    (see, for example ipfs.io).
    However, an address also includes a prefix. It makes it more easy for humans to interpret an address,
    and further decreases collision risk.
    """

    prefix: str
    hash_id: str
    _hash_type: str = "sha256"

    @staticmethod
    def _build_prefix(x: Any) -> str:
        prfx = str(type(x).__module__)

        if hasattr(type(x), "__qualname__"):
            prfx += "." + str(type(x).__qualname__)
        else:
            prfx += "." + str(type(x).__name__)

        if hasattr(x, "__qualname__"):
            prfx += "___" + str(x.__qualname__)
        elif hasattr(x, "__name__"):
            prfx += "___" + str(x.__name__)

        if (hasattr(x, "shape")
                and hasattr(x.shape, "__iter__")
                and callable(x.shape.__iter__)
                and not callable(x.shape)):

            prfx += "___shape_"
            for n in x.shape:
                prfx += str(n) + "_x_"
            prfx = prfx[:-3]

        elif (hasattr(x, "__len__")
              and callable(x.__len__)):
            prfx += "___len_" + str(len(x))

        return prfx

    @staticmethod
    def _build_hash_id(x: Any) -> str:
        if 'numpy' in sys.modules:
            hasher = NumpyHasher(hash_name=PHashAddress._hash_type)
        else:
            hasher = Hasher(hash_name=PHashAddress._hash_type)
        return hasher.hash(x)

    def __init__(self, x: Any):
        if isinstance(x, PHashAddress):
            self.prefix = x.prefix
            self.hash_id = x.hash_id
        else:
            self.prefix = self._build_prefix(x)
            self.hash_id = self._build_hash_id(x)

    def __iter__(self):
        def step():
            yield self.prefix
            yield self.hash_id

        return step()

    def __eq__(self, other):
        return ( isinstance(other, self.__class__)
                and self.prefix  == other.prefix
                and self.hash_id == other.hash_id )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __len__(self):
        return 2

    def __repr__(self):
        return f"PHashAddress( prefix={self.prefix} , hash_id={self.hash_id} )"