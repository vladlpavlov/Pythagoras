import os
from tempfile import TemporaryDirectory
# from pythagoras.persistent_dicts import FileDirDict, safe_chars
from pythagoras.persidicts import FileDirDict, safe_chars

from hypothesis import given, strategies as st
import pytest

dict_key = st.text(alphabet=safe_chars, min_size=1)

MUTABLE_DICT_PARAMS = [
    (FileDirDict, {"dir_name": "__TMPDIR__", "file_type": "pkl"}),
    (FileDirDict, {"dir_name": "__TMPDIR__", "file_type": "json"}),
]



class DictGenerator():
    def __init__(self, dicts_params):
        self.dicts_params = dicts_params
        self.tmpdirs = []

    def __enter__(self):
        return [
            self._gen_dict(dict_type, dict_params)
            for dict_type, dict_params in self.dicts_params
        ]

    def __exit__(self, exc_type, exc_value, exc_traceback):
        for tmpdir in self.tmpdirs:
            tmpdir.cleanup()

    def _gen_dict(self, dict_type, dict_params):
        new_params = {}
        for key, value in dict_params.items():
            if value == "__TMPDIR__":
                tmpdir = TemporaryDirectory(prefix='dictgen')
                self.tmpdirs.append(tmpdir)
                new_params[key] = tmpdir.name
            else:
                new_params[key] = value
        return dict_type(**new_params)


# TODO: Try to set values of various types
@pytest.mark.parametrize("dicts_params", [MUTABLE_DICT_PARAMS])
@given(random_pairs=st.lists(st.tuples(dict_key, st.text())))
def test_set_random_values(random_pairs, dicts_params):
    """
    Write random values into the dict and ensure that it correctly stores them
    """
    with DictGenerator(dicts_params) as dicts_to_test:
        for dict_to_test in dicts_to_test:
            model_dict = dict()
            assert dict_to_test == model_dict
            for key, value in random_pairs:
                dict_to_test[key] = value
                model_dict[key] = value
                assert key in dict_to_test

            assert len(dict_to_test) == len(model_dict)
            assert dict_to_test == model_dict


@pytest.mark.parametrize("dicts_params", [MUTABLE_DICT_PARAMS])
@given(random_pair=st.tuples(dict_key, st.text()))
def test_set_del(random_pair, dicts_params):
    """
    Ensure that deleting items from dict works
    """
    with DictGenerator(dicts_params) as dicts_to_test:
        for dict_to_test in dicts_to_test:
            key, value = random_pair

            with pytest.raises(KeyError):
                del dict_to_test[key]

            dict_to_test[key] = value
            assert key in dict_to_test

            del dict_to_test[key]
            assert key not in dict_to_test


@pytest.mark.parametrize("dicts_params", [MUTABLE_DICT_PARAMS])
@given(random_pair=st.tuples(dict_key, st.text()), random_value=st.text())
def test_get(random_pair, random_value, dicts_params):
    """
    Ensure that .get()tting items from dict works as expected
    """
    with DictGenerator(dicts_params) as dicts_to_test:
        for dict_to_test in dicts_to_test:
            key, init_value = random_pair

            get_value = dict_to_test.get(key, init_value)
            assert get_value == init_value

            dict_to_test[key] = random_value
            get_value = dict_to_test.get(key, init_value)
            assert get_value == random_value


@pytest.mark.parametrize("dicts_params", [MUTABLE_DICT_PARAMS])
@given(random_pair=st.tuples(dict_key, st.text()))
def test_setdefault(random_pair, dicts_params):
    """
    Ensure that .setdefault() works as expected
    """
    with DictGenerator(dicts_params) as dicts_to_test:
        for dict_to_test in dicts_to_test:
            key, value = random_pair

            assert dict_to_test.setdefault(key, value) == value
            assert key in dict_to_test


@pytest.mark.parametrize("dicts_params", [MUTABLE_DICT_PARAMS])
@given(random_pair=st.tuples(dict_key, st.text()))
def test_pop(random_pair, dicts_params):
    """
    Ensure that .pop()ping items from dict works as expected
    """
    with DictGenerator(dicts_params) as dicts_to_test:
        for dict_to_test in dicts_to_test:
            key, value = random_pair

            dict_to_test[key] = value
            pop_value = dict_to_test.pop(key, value)
            assert pop_value == value

            assert key not in dict_to_test
