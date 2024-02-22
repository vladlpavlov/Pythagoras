from persidict import replace_unsafe_chars

from pythagoras._00_basic_utils.random_safe_str_creator import get_random_safe_str

def test_random_id():
    all_random_ids = set()
    n_iterations = 20_000
    for i in range(n_iterations):
        random_id = get_random_safe_str()
        assert random_id == replace_unsafe_chars(random_id, replace_with="_")
        all_random_ids.add(random_id)
    assert len(all_random_ids) == n_iterations

