import uuid
from pythagoras._99_misc_utils.base_16_32_convertors import (
    convert_int_to_base32)

def get_random_safe_str() -> str:
    random_int = uuid.uuid4().int + uuid.uuid1().int
    random_str = convert_int_to_base32(random_int)
    return random_str