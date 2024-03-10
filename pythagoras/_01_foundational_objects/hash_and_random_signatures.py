import platform, getpass, sys, uuid
from typing import Any

import joblib.hashing

from pythagoras._01_foundational_objects.base_16_32_convertors import (
    convert_int_to_base32, convert_base16_to_base32)

# TODO: split into a few files, add more unit-tests

hash_type: str = "sha256"
max_signature_length: int = 22

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
    return get_base32_hash_signature(x)[:max_signature_length]


def get_node_signature() -> str:
    mac = uuid.getnode()
    system = platform.system()
    release = platform.release()
    version = platform.version()
    machine = platform.machine()
    processor = platform.processor()
    user = getpass.getuser()
    id_string = f"{mac}{system}{release}{version}"
    id_string += f"{machine}{processor}{user}"
    return get_hash_signature(id_string)


def get_random_signature() -> str:
    random_int = uuid.uuid4().int + uuid.uuid1().int
    random_str = convert_int_to_base32(random_int)
    return random_str[:max_signature_length]
