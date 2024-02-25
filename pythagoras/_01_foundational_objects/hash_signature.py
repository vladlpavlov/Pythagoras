import sys
from typing import Any

import joblib.hashing
from pythagoras._99_misc_utils.base_16_32_convertors import (
    convert_base16_to_base32)

# TODO: split into a few files, add more unit-tests

hash_type: str = "sha256"


def get_base16_hash_signature(x:Any) -> str:
    if 'numpy' in sys.modules:
        hasher = joblib.hashing.NumpyHasher(hash_name=hash_type)
    else:
        hasher = joblib.hashing.Hasher(hash_name=hash_type)
    hash_signature = hasher.hash(x)
    return str(hash_signature)

def get_base32_hash_signature(x:Any) -> str:
    """Return base32 hash signature of an object"""
    base_16_hash = get_base16_hash_signature(x)
    base_32_hash = convert_base16_to_base32(base_16_hash)
    return base_32_hash


def get_hash_signature(x:Any) -> str:
    return get_base32_hash_signature(x)
