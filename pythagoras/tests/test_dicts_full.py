import os
from tempfile import TemporaryDirectory
from pythagoras.persistent_dicts import FileDirDict, safe_chars

from hypothesis import given, strategies as st
import pytest

dict_key = st.text(alphabet=safe_chars, min_size=1)

MUTABLE_DICT_PARAMS = [
    (FileDirDict, {"dir_name": "__TMPDIR__", "file_type": "pkl"}),
    (FileDirDict, {"dir_name": "__TMPDIR__", "file_type": "json"}),
]


# TODO: Implement as contextmanager
def mkdicts(dicts_params):
    tmpdirs = []
    dicts = []
    for dict_type, dict_params in dicts_params:
        _dict_params = {}
        for key, value in dict_params.items():
            _dict_params = dict_params.copy()
            if value == "__TMPDIR__":
                _tmpdir = TemporaryDirectory()
                _dict_params[key] = _tmpdir.name
            else:
                _dict_params[key] = value
        new_dict = dict_type(**dict_params)
        new_dict.clear()
        dicts.append(new_dict)
    yield dicts
    for tmpdir in tmpdirs:
        tmpdir.cleanup()
    yield


# TODO: Try to set values of various types
@pytest.mark.parametrize("dicts_params", [MUTABLE_DICT_PARAMS])
@given(random_pairs=st.lists(st.tuples(dict_key, st.text())))
def test_set_random_values(random_pairs, dicts_params):
    """
    Write random values into the dict and ensure that it correctly stores them
    """
    dict_gen = mkdicts(dicts_params)
    dicts_to_test = next(dict_gen)
    for dict_to_test in dicts_to_test:
        model_dict = dict()
        assert dict_to_test == model_dict
        for key, value in random_pairs:
            dict_to_test[key] = value
            model_dict[key] = value
            assert key in dict_to_test

        assert len(dict_to_test) == len(model_dict)
        assert dict_to_test == model_dict
    next(dict_gen)


@pytest.mark.parametrize("dicts_params", [MUTABLE_DICT_PARAMS])
@given(random_pair=st.tuples(dict_key, st.text()))
def test_set_del(random_pair, dicts_params):
    """
    Ensure that deleting items from dict works
    """
    dict_gen = mkdicts(dicts_params)
    dicts_to_test = next(dict_gen)
    for dict_to_test in dicts_to_test:
        key, value = random_pair

        with pytest.raises(KeyError):
            del dict_to_test[key]

        dict_to_test[key] = value
        assert key in dict_to_test

        del dict_to_test[key]
        assert key not in dict_to_test
    next(dict_gen)


@pytest.mark.parametrize("dicts_params", [MUTABLE_DICT_PARAMS])
@given(random_pair=st.tuples(dict_key, st.text()), random_value=st.text())
def test_get(random_pair, random_value, dicts_params):
    """
    Ensure that .get()tting items from dict works as expected
    """
    dict_gen = mkdicts(dicts_params)
    dicts_to_test = next(dict_gen)
    for dict_to_test in dicts_to_test:
        key, init_value = random_pair

        get_value = dict_to_test.get(key, init_value)
        assert get_value == init_value

        dict_to_test[key] = random_value
        get_value = dict_to_test.get(key, init_value)
        assert get_value == random_value
    next(dict_gen)


@pytest.mark.parametrize("dicts_params", [MUTABLE_DICT_PARAMS])
@given(random_pair=st.tuples(dict_key, st.text()))
def test_setdefault(random_pair, dicts_params):
    """
    Ensure that .setdefault() works as expected
    """
    dict_gen = mkdicts(dicts_params)
    dicts_to_test = next(dict_gen)
    for dict_to_test in dicts_to_test:
        key, value = random_pair

        assert dict_to_test.setdefault(key, value) == value
        assert key in dict_to_test
    next(dict_gen)


@pytest.mark.parametrize("dicts_params", [MUTABLE_DICT_PARAMS])
@given(random_pair=st.tuples(dict_key, st.text()))
def test_pop(random_pair, dicts_params):
    """
    Ensure that .pop()ping items from dict works as expected
    """
    dict_gen = mkdicts(dicts_params)
    dicts_to_test = next(dict_gen)
    for dict_to_test in dicts_to_test:
        key, value = random_pair

        dict_to_test[key] = value
        pop_value = dict_to_test.pop(key, value)
        assert pop_value == value

        assert key not in dict_to_test
    next(dict_gen)
