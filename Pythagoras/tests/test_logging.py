import pytest
from Pythagoras import *


@pytest.fixture(params=[False, True])
def sample_writing_flag(request):
    return request.param


@pytest.fixture(params=[True, False])
def sample_reading_flag(request):
    return request.param


@pytest.fixture(params=[('fast', 1), ('slow', 30)])
def func_speed_arg(request):
    return request.param


@pytest.fixture(params=[('small', 1), ('large', 3000000)])
def file_size_arg(request):
    return request.param


# Fibonacci function for speed test
def fib(n):
    if n == 1 or n == 0:
        return 1
    return fib(n-1) + fib(n-2)


# Function returns None
def func_return_none():
    return None


class TestLogging:

    def test_function_log(self, tmpdir, func_speed_arg, caplog):
        """
            Test the caching fast and slow functions:
            1. Expect warning message when loading small files for not saving time
            2. Expect no warning message when loading large file
        """

        # Instantiate PickleCache
        my_cache = PickleCache(
            cache_dir=str(tmpdir),
            write_to_cache=True,
            read_from_cache=True
        )

        # Apply PickleCache to fibonacci function
        original_func = fib
        new_func = my_cache(original_func)

        # 1st Run
        new_func(func_speed_arg[1])

        # 2nd Run
        new_func(func_speed_arg[1])

        # Fast Function Test: expect 'Caching did not save time' warning
        if func_speed_arg[0] == 'fast':
            assert caplog.records[3].levelname == 'WARNING'
            assert 'Caching did not save time' in caplog.text

        # Slow Function Test: expect no warning
        if func_speed_arg[0] == 'slow':
            assert caplog.records[3].levelname != 'WARNING'
            assert 'Caching did not save time' not in caplog.text

    def test_none_return_function_log(self, tmpdir, caplog):
        """
            Test function returns None. Expect 2 warning messages
            1. The function returns None
            2. Cache does not save time
        """

        # Instantiate PickleCache
        my_cache = PickleCache(
            cache_dir=str(tmpdir),
            write_to_cache=True,
            read_from_cache=True)

        original_func = func_return_none
        new_func = my_cache(original_func)
        output = new_func()

        assert original_func() == new_func()
        assert not output
        assert my_cache.cache_dir_len() == 1
        assert caplog.records[2].levelname == 'WARNING'
        assert caplog.records[4].levelname == 'WARNING'
        assert 'returned None' in caplog.text
        assert 'Caching did not save time' in caplog.text

    def test_load_csv_log(self, tmpdir, file_size_arg, caplog):
        """
            Test the logging for loading small and large files.
            1. Expect warning message when loading small files for not saving time
            2. Expect no warning message when loading large file
        """

        # Create a new testing csv file
        tmp_dir = tmpdir.mkdir('original_file_temp')
        input_file = tmp_dir.join('eggs.csv')
        input_file.write('S' * file_size_arg[1])

        # Instantiate PickleCache
        my_cache = PickleCache(
            cache_dir=str(tmpdir.mkdir('cache_temp')),
            write_to_cache=sample_writing_flag,
            read_from_cache=sample_reading_flag,
            input_dir=tmp_dir
        )

        # 1st Read
        my_cache.read_csv("eggs.csv", header=None)

        # 1nd Read
        my_cache.read_csv("eggs.csv", header=None)

        # Small file test (Extreme case): expect 'Cache did not save time' warning
        if file_size_arg[0] == 'small':
            assert caplog.records[2].levelname == 'WARNING'
            assert 'Caching did not save time' in caplog.text

        # Large file test: expect no warning
        if file_size_arg[0] == 'large':
            assert caplog.records[2].levelname != 'WARNING'
            assert 'Caching did not save time' not in caplog.text

