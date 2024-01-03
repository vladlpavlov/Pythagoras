from persidict import replace_unsafe_chars

from pythagoras.utils.hash_signature_and_random_id import (
    convert_base16_to_base32, convert_base_32_to_int, get_random_id)

def test_small_range():
    for i in range(1000):
        i_base16 = hex(i)[2:]
        i_base32 = convert_base16_to_base32(i_base16)
        assert i_base32 == replace_unsafe_chars(i_base32, replace_with="_")
        i_new = convert_base_32_to_int(i_base32)
        assert i_new == i

def test_large_range():
    max_val = 100_000_000_000_000_000_000
    max_val *= max_val * max_val
    max_val *= max_val * max_val
    max_val *= max_val * max_val
    step = max_val//1000
    for i in range(0,max_val,step):
        i_base16 = hex(i)[2:]
        i_base32 = convert_base16_to_base32(i_base16)
        assert i_base32 == replace_unsafe_chars(i_base32, replace_with="_")
        i_new = convert_base_32_to_int(i_base32)
        assert i_new == i

def test_random_id():
    all_random_ids = set()
    n_iterations = 20_000
    for i in range(n_iterations):
        random_id = get_random_id()
        assert random_id == replace_unsafe_chars(random_id, replace_with="_")
        all_random_ids.add(random_id)
    assert len(all_random_ids) == n_iterations

