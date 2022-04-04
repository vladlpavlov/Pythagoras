import time
from tempfile import TemporaryDirectory
from pythagoras import FileDirDict
from pythagoras import allowed_key_chars
from hypothesis import given, strategies as st
import pytest

dict_key = st.text(alphabet=allowed_key_chars, min_size=1)


# TODO: Try to set values of various types

@given(random_pairs=st.lists(st.tuples(dict_key, st.text())))
def test_set_random_values(random_pairs):
    """
    Write random values into the dict and ensure that it correctly stores them
    """
    with TemporaryDirectory() as tmpdir:
        dict_to_test = FileDirDict(dir_name=tmpdir, file_type="pkl")
        model_dict = dict()

        assert dict_to_test == model_dict

        for key, value in random_pairs:
            dict_to_test[key] = value
            model_dict[key] = value
            assert key in dict_to_test

        assert len(dict_to_test) == len(model_dict)
        assert dict_to_test == model_dict



@given(random_pair=st.tuples(dict_key, st.text()))
def test_set_del(random_pair):
    """
    Ensure that deleting items from dict works
    """
    with TemporaryDirectory() as tmpdir:
        dict_to_test = FileDirDict(dir_name=tmpdir, file_type="pkl")
        key, value = random_pair

        with pytest.raises(KeyError):
            del dict_to_test[key]

        dict_to_test[key] = value
        assert key in dict_to_test

        del dict_to_test[key]
        assert key not in dict_to_test


@given(random_pair=st.tuples(dict_key, st.text()), random_value=st.text())
def test_get(random_pair, random_value):
    """
    Ensure that .get()tting items from dict works as expected
    """
    with TemporaryDirectory() as tmpdir:
        dict_to_test = FileDirDict(dir_name=tmpdir, file_type="pkl")
        key, init_value = random_pair

        get_value = dict_to_test.get(key, init_value)
        assert get_value == init_value

        dict_to_test[key] = random_value
        get_value = dict_to_test.get(key, init_value)
        assert get_value == random_value


@given(random_pair=st.tuples(dict_key, st.text()))
def test_setdefault(random_pair):
    """
    Ensure that .setdefault() works as expected
    """
    with TemporaryDirectory() as tmpdir:
        dict_to_test = FileDirDict(dir_name=tmpdir, file_type="pkl")
        key, value = random_pair

        assert dict_to_test.setdefault(key, value) == value
        assert key in dict_to_test


@given(random_pair=st.tuples(dict_key, st.text()))
def test_pop(random_pair):
    """
    Ensure that .pop()ping items from dict works as expected
    """
    with TemporaryDirectory() as tmpdir:
        dict_to_test = FileDirDict(dir_name=tmpdir, file_type="pkl")
        key, value = random_pair

        dict_to_test[key] = value
        pop_value = dict_to_test.pop(key, value)
        assert pop_value == value

        assert key not in dict_to_test
