import pytest
from Pythagoras import *
import time
import os
import numpy as np


class SimpleSomething:
    def slim_repr(self,_):
        return type(self).__name__

    def fingerprint_repr(self,_):
        return self.slim_repr(None)

    def no_arg_method(self):
        time.sleep(0.0001)
        return "kukareku"

    def one_arg_method(self,a1):
        time.sleep(0.0001)
        return [a1]


class StockCache:
    def __init__(self, ticker, action):
        self.ticker = ticker
        self.action = action

    def fingerprint_repr(self, _: FingerprintReprBuilder) -> str:
        fingerprint_str = type(self).__name__
        fingerprint_str += self.ticker
        fingerprint_str += self.action
        assert len(fingerprint_str), "fingerpint_repr can not return an empty string"
        return fingerprint_str

    def slim_repr(self, srepr_builder: SlimReprBuilder) -> str:
        return "Stock_"+self.ticker


def two_arg_func(a1, a2):
    time.sleep(0.0001)
    return (a1, a2)


# Fibonacci function for speed test
def fib(n):
    if n == 1 or n == 0:
        return 1
    return fib(n-1) + fib(n-2)

# Testing value
values = [12345, 678.9, True, "a string", [1, 2, 3], {1, 2, 3, 4}, (1, 2, 3, 4, 5)
          , "a very long string which should be processed differently, and reduced to a short string"]


@pytest.fixture(params=[False,True])
def sample_writing_flag(request):
    return request.param


@pytest.fixture(params=[True,False])
def sample_reading_flag(request):
    return request.param


@pytest.fixture(params=["", "SampleCacheID"])
def sample_id(request):
    return request.param


@pytest.fixture(params=values)
def sample_arg1(request):
    return request.param


@pytest.fixture(params=values[:5])
def sample_arg2(request):
    return request.param


# Argument for speed fibonacci test
@pytest.fixture(params=[('fast', 1), ('slow', 30)])
def func_speed_arg(request):
    return request.param


@pytest.fixture(params=[('small', 1), ('large', 3000000)])
def file_size_arg(request):
    return request.param


@pytest.fixture(params=[('short', 1), ('long', 230)])
def file_name_arg(request):
    return request.param


class TestPickleCache:

# ------ Start Test for Basic Function and Method ---------
    def test_demo(self):

        def one_arg_func(a1):
            time.sleep(0.0001)
            return a1

        demo_cache = PickleCache()
        original_func = one_arg_func
        demo_one_arg_func = demo_cache(one_arg_func)
        for v in values[:2]:
            assert original_func(v) == demo_one_arg_func(v)
            assert demo_one_arg_func(v) == demo_one_arg_func(v)
        for v in values[-2:]:
            assert original_func(a1=v) == demo_one_arg_func(a1=v)
            assert demo_one_arg_func(a1=v) == demo_one_arg_func(a1=v)

    def test_no_arg_func(self, tmp_path, sample_writing_flag, sample_reading_flag, sample_id):
        """
        Cache files should be created when read_from_cache is True
        """

        my_cache = PickleCache(
            cache_dir=str(tmp_path)
            , read_from_cache=sample_reading_flag
            , write_to_cache=sample_writing_flag
            , id_str=sample_id)

        def no_arg_func():
            time.sleep(0.001)
            return 123456

        original_func = no_arg_func
        new_func = my_cache(no_arg_func)

        assert original_func() == new_func()
        assert new_func() == new_func()

        if sample_writing_flag:
            assert len(my_cache.files_in_cache_dir())
        else:
            assert not len(my_cache.files_in_cache_dir())

        if len(sample_id):
            assert (len(my_cache.files_in_cache_dir()) ==
                len([name for name in my_cache.files_in_cache_dir() if sample_id in name]))

    def test_no_arg_method(self, tmp_path, sample_writing_flag, sample_reading_flag, sample_id):
        my_cache = PickleCache(
            cache_dir=str(tmp_path)
            , read_from_cache=sample_reading_flag
            , write_to_cache=sample_writing_flag
            , id_str=sample_id)

        a = SimpleSomething()

        SimpleSomething.original_method = (SimpleSomething.no_arg_method)
        SimpleSomething.new_method = my_cache(SimpleSomething.no_arg_method)

        assert a.original_method() == a.new_method()
        assert a.new_method() == a.new_method()

        if sample_writing_flag:
            assert len(my_cache.files_in_cache_dir())
        else:
            assert not len(my_cache.files_in_cache_dir())

        if len(sample_id):
            assert (len(my_cache.files_in_cache_dir()) ==
                len([name for name in my_cache.files_in_cache_dir() if sample_id in name]))

    def test_1_arg_func(self, tmp_path,sample_arg1 ,sample_writing_flag, sample_reading_flag, sample_id):
        my_cache = PickleCache(
            cache_dir=str(tmp_path)
            , read_from_cache=sample_reading_flag
            , write_to_cache=sample_writing_flag
            , id_str=sample_id)

        def one_arg_func(a1):
            time.sleep(0.0001)
            return a1

        original_func = one_arg_func
        new_one_arg_func = my_cache(original_func)

        assert original_func(sample_arg1) == new_one_arg_func(sample_arg1)
        assert new_one_arg_func(sample_arg1) == new_one_arg_func(sample_arg1)
        assert original_func(a1=sample_arg1) == new_one_arg_func(a1=sample_arg1)
        assert new_one_arg_func(a1=sample_arg1) == new_one_arg_func(a1=sample_arg1)

        if sample_writing_flag:
            assert len(my_cache.files_in_cache_dir())
        else:
            assert not len(my_cache.files_in_cache_dir())

        if len(sample_id):
            assert (len(my_cache.files_in_cache_dir()) ==
                len([name for name in my_cache.files_in_cache_dir() if sample_id in name]))

    def test_1_arg_method(self, tmp_path,sample_arg1, sample_writing_flag, sample_reading_flag, sample_id):
        my_cache = PickleCache(
            cache_dir=str(tmp_path)
            ,read_from_cache=sample_reading_flag
            ,write_to_cache=sample_writing_flag
            ,id_str=sample_id)

        a = SimpleSomething()

        SimpleSomething.original_method = (SimpleSomething.one_arg_method)
        SimpleSomething.new_one_arg_method = my_cache(SimpleSomething.original_method)

        assert a.original_method(sample_arg1) == a.new_one_arg_method(sample_arg1)
        assert a.new_one_arg_method(sample_arg1) == a.new_one_arg_method(sample_arg1)
        assert a.original_method(a1=sample_arg1) == a.new_one_arg_method(a1=sample_arg1)
        assert a.new_one_arg_method(a1=sample_arg1) == a.new_one_arg_method(a1=sample_arg1)

        if sample_writing_flag:
            assert len(my_cache.files_in_cache_dir())
        else:
            assert not len(my_cache.files_in_cache_dir())

        if len(sample_id):
            assert (len(my_cache.files_in_cache_dir()) ==
                len([name for name in my_cache.files_in_cache_dir() if sample_id in name]))

    def test_2_arg_func(self, tmp_path,sample_arg1,sample_arg2,sample_writing_flag, sample_reading_flag, sample_id):
        my_cache = PickleCache(
            cache_dir=str(tmp_path)
            , read_from_cache=sample_reading_flag
            , write_to_cache=sample_writing_flag
            , id_str=sample_id)

        original_func = two_arg_func
        new_func = my_cache(two_arg_func)

        assert original_func(sample_arg1, sample_arg2) == new_func(sample_arg1, sample_arg2)
        assert new_func(sample_arg1, sample_arg2) == new_func(sample_arg1, sample_arg2)
        assert original_func(a1=sample_arg1, a2=sample_arg2) == new_func(a1=sample_arg1, a2=sample_arg2)
        assert new_func(a1=sample_arg1, a2=sample_arg2) == new_func(a1=sample_arg1, a2=sample_arg2)

        if sample_writing_flag:
            assert len(my_cache.files_in_cache_dir())
        else:
            assert not len(my_cache.files_in_cache_dir())

        if len(sample_id):
            assert (len(my_cache.files_in_cache_dir()) ==
                len([name for name in my_cache.files_in_cache_dir() if sample_id in name]))

    def test_reading_csv_with_different_parameters(self, tmpdir, tmp_path, sample_writing_flag):
        """
        If the csv file is read with different parameters (e.g., with or without header),
        Picklecache should create two different cache files due to different content.
        """
        # Create a testing csv file
        tmp_dir = tmpdir.mkdir('tmp_1')
        p1 = tmp_dir.join('eggs.csv')
        p1.write('Spam,Spam,Spam')

        assert p1.read() == ','.join(['Spam']*3)

        # Instantiate PickleCache
        my_cache = PickleCache(
            cache_dir=str(tmpdir.mkdir('tmp_2')),
            write_to_cache=sample_writing_flag,
            input_dir=tmp_dir
        )

        # Reading csv through PickleCache with different arguments
        df_1 = my_cache.read_csv("eggs.csv", header=None)
        df_2 = my_cache.read_csv("eggs.csv", header='infer')

        # Test the writing of cache file
        if sample_writing_flag:
            assert my_cache.cache_dir_len() == 2  # should generate 2 cache files
            # Test the content for changing read_csv parameters should be different
            assert (df_1.columns != df_2.columns).all()

        if not sample_writing_flag:
            assert my_cache.cache_dir_len() == 0
            # Test the content for changing read_csv parameters should be different
            assert (df_1.columns != df_2.columns).all()

    # Test running function with different inputs/parameters
    def test_func_change_params(self, tmp_path, sample_writing_flag, sample_reading_flag):
        """
        When write_to_cache is True, running function with different parameters should generate
        separate cache files. Running functions with identical parameters should not generate new
        cache file.
        When read_from_cache is True, the output of the functions with same parameters should be
        load quickly from the cache files.
        """
        my_cache = PickleCache(
            cache_dir=str(tmp_path)
            , read_from_cache=sample_reading_flag
            , write_to_cache=sample_writing_flag
        )

        def temp_func(a, b):
            return np.random.random()*a, np.random.random()*b

        original_func = temp_func
        new_func = my_cache(original_func)

        cache_run_1 = new_func(1, 2)   # cache run #1
        cache_run_2 = new_func(1, 2)   # cache run #2: same inputs as cache run #1
        cache_run_3 = new_func(3, 4)   # cache run #3: different inputs as cache run #1

        original_run_1 = original_func(1, 2)   # original run #1
        original_run_2 = original_func(1, 2)   # original run #2: same inputs as original run #1
        original_run_3 = original_func(3, 4)   # original run #3: different inputs as original run #1

        if sample_writing_flag and sample_reading_flag:
            assert my_cache.cache_dir_len() == 2    # # of cache_file = # of cache runs with different parameters (2)

            assert cache_run_1 == cache_run_2       # same outputs for cache runs with same inputs
            assert cache_run_1 != cache_run_3       # different outputs for cache runs with different inputs

            assert original_run_1 != original_run_2   # Without PickleCache: run with same inputs will get different outputs
            assert original_run_1 != original_run_3   # Without PickleCache: run with different inputs will get different outputs

        if sample_writing_flag and not sample_reading_flag:
            assert my_cache.cache_dir_len() == 2  # # of cache_file = # of cache runs with different parameters (2)

            assert cache_run_1 != cache_run_2  # different outputs for cache runs with same inputs
            assert cache_run_1 != cache_run_3  # different outputs for cache runs with different inputs

            assert original_run_1 != original_run_2  # Without PickleCache: run with same inputs will get different outputs
            assert original_run_1 != original_run_3  # Without PickleCache: run with different inputs will get different outputs

        if not sample_writing_flag and not sample_reading_flag:
            assert my_cache.cache_dir_len() == 0  # no cache file generated

            assert cache_run_1 != cache_run_2  # different outputs for cache runs with same inputs
            assert cache_run_1 != cache_run_3  # different outputs for cache runs with different inputs

            assert original_run_1 != original_run_2  # Without PickleCache: run with same inputs will get different outputs
            assert original_run_1 != original_run_3  # Without PickleCache: run with different inputs will get different outputs

        if not sample_writing_flag and sample_reading_flag:
            assert my_cache.cache_dir_len() == 0  # no cache file generated

            assert cache_run_1 != cache_run_2  # different outputs for cache runs with same inputs
            assert cache_run_1 != cache_run_3  # different outputs for cache runs with different inputs

            assert original_run_1 != original_run_2  # Without PickleCache: run with same inputs will get different outputs
            assert original_run_1 != original_run_3  # Without PickleCache: run with different inputs will get different outputs

    def test_changing_csv_content(self, tmpdir, tmp_path, sample_writing_flag, sample_reading_flag):
        """
        When write_to_cache is True, reading csv files with different content should generate
        separate cache files. Reading csv files with identical parameters should not generate new
        cache file.
        When read_from_cache is True, the content of the csv files with same content should be
        load quickly from the cache files.
        """

        # Create a new testing csv file
        tmp_dir = tmpdir.mkdir('original_file_temp')
        input_file = tmp_dir.join('eggs.csv')

        # Instantiate PickleCache
        my_cache = PickleCache(
            cache_dir=str(tmpdir.mkdir('cache_temp')),
            write_to_cache=sample_writing_flag,
            read_from_cache=sample_reading_flag,
            input_dir=tmp_dir
        )

    # ----- File Creation, Modification, Reading, and Output ------
        # ---- 1st ver. -----

        input_file.write('Spam,Spam,Spam')
        assert input_file.read() == ','.join(['Spam']*3)
        df_1 = my_cache.read_csv("eggs.csv", header=None)
        df_1.to_csv(tmp_dir.join("eggs1.csv"), header=None, index=None)
        output_file_1 = tmp_dir.join("eggs1.csv")

        # ---- 2nd ver. ----- different content

        # Modify the existing csv file
        input_file.write('Spam,Spam,Spam,Spam,Spam')
        assert input_file.read() == ','.join(['Spam']*5)
        df_2 = my_cache.read_csv("eggs.csv", header=None)
        df_2.to_csv(tmp_dir.join("eggs2.csv"), header=None, index=None)
        output_file_2 = tmp_dir.join("eggs2.csv")

        time.sleep(1)

        # ---- 3rd ver. ----- change back to 1st ver.

        # Change the content back to version 1
        input_file.write('Spam,Spam,Spam')
        assert input_file.read() == ','.join(['Spam']*3)
        df_3 = my_cache.read_csv("eggs.csv", header=None)
        df_3.to_csv(tmp_dir.join("eggs3.csv"), header=None, index=None)
        output_file_3 = tmp_dir.join("eggs3.csv")

    # ------------ Testing Section -----------------
        # Test #1
        if sample_writing_flag and sample_reading_flag:
            # Expected Reading Outcome:
            # A cache file should be created for each different content. Therefore,
            # 1 created for 1st version, 1 created for 2nd version due to different
            # content. No file is created for 3rd version because the file name and
            # and content are same as the 1st version. Total 2 cache file created.
            assert my_cache.cache_dir_len() == 3
            # Expected Output Content
            assert input_file.read() == output_file_1.read().strip()
            assert output_file_1.read() != output_file_2.read()
            assert output_file_1.read() == output_file_3.read()

        # Test #2
        if sample_writing_flag and not sample_reading_flag:
            # Expected outcome: same as Test 1
            assert my_cache.cache_dir_len() == 3
            # Expected Output Content: Same as Test 1
            assert input_file.read() == output_file_1.read().strip()
            assert output_file_1.read() != output_file_2.read()
            assert output_file_1.read() == output_file_3.read()

        # Test #3
        if not sample_writing_flag and sample_reading_flag:
            # Expected Reading Outcome:
            # No file should be created
            assert my_cache.cache_dir_len() == 0
            # Expected Output Content: same as Test 1
            assert input_file.read() == output_file_1.read().strip()
            assert output_file_1.read() != output_file_2.read()
            assert output_file_1.read() == output_file_3.read()

    # Test #4
        if not sample_writing_flag and not sample_reading_flag:
            # Expected Reading Outcome: same as Test 3
            assert my_cache.cache_dir_len() == 0
            # Expected Output Content: same as Test 1
            assert input_file.read() == output_file_1.read().strip()
            assert output_file_1.read() != output_file_2.read()
            assert output_file_1.read() == output_file_3.read()

    def test_changing_csv_name(self, tmpdir, tmp_path, sample_writing_flag, sample_reading_flag):
        # Create a new testing csv file
        tmp_dir = tmpdir.mkdir('original_file_temp')
        input_file = tmp_dir.join('eggs.csv')

        # Instantiate PickleCache
        my_cache = PickleCache(
            cache_dir=str(tmpdir.mkdir('cache_temp')),
            write_to_cache=sample_writing_flag,
            read_from_cache=sample_reading_flag,
            input_dir=tmp_dir
        )

    # ----- File Creation, Modification, Reading, and Output ------
        # ---- 1st ver. -----

        input_file.write('Spam,Spam,Spam')
        assert input_file.read() == ','.join(['Spam'] * 3)
        df_1 = my_cache.read_csv("eggs.csv", header=None)
        df_1.to_csv(tmp_dir.join("eggs1.csv"), header=None, index=None)
        output_file_1 = tmp_dir.join("eggs1.csv")

        # ---- 2nd ver. ----- different name

        # Modify the existing csv file
        os.rename(input_file, tmp_dir.join('ham.csv'))
        input_file = tmp_dir.join('ham.csv')
        assert input_file.read() == ','.join(['Spam'] * 3)
        df_2 = my_cache.read_csv("ham.csv", header=None)
        df_2.to_csv(tmp_dir.join("ham1.csv"), header=None, index=None)
        output_file_2 = tmp_dir.join("ham1.csv")

        # ---- 3rd ver. ----- change back to 1st ver.
        time.sleep(1)

        # Change the content back to version 1
        os.rename(input_file, tmp_dir.join('eggs.csv'))
        input_file = tmp_dir.join('eggs.csv')
        assert input_file.read() == ','.join(['Spam'] * 3)
        df_3 = my_cache.read_csv("eggs.csv", header=None)
        df_3.to_csv(tmp_dir.join("eggs2.csv"), header=None, index=None)
        output_file_3 = tmp_dir.join("eggs2.csv")

    # ------------ Testing Section -----------------
        # Test #1
        if sample_writing_flag and sample_reading_flag:
            # Expected Reading Outcome:
            # A cache file should be created for each file with modified name. Therefore,
            # 1 created for 1st version, 1 created for 2nd version due to different
            # filename. No file is created for 3rd version because the file name and
            # and content are same as the 1st version. Total 2 cache file created.
            assert my_cache.cache_dir_len() == 2
            # Expected Output Content
            assert input_file.read() == output_file_1.read().strip()
            assert output_file_1.read() == output_file_2.read()
            assert output_file_1.read() == output_file_3.read()

        # Test #2
        if sample_writing_flag and not sample_reading_flag:
            # Expected outcome: same as Test 1
            assert my_cache.cache_dir_len() == 2
            # Expected Output Content: Same as Test 1
            assert input_file.read() == output_file_1.read().strip()
            assert output_file_1.read() == output_file_2.read()
            assert output_file_1.read() == output_file_3.read()

        # Test #3
        if not sample_writing_flag and sample_reading_flag:
            # Expected Reading Outcome:
            # No file should be created
            assert my_cache.cache_dir_len() == 0
            # Expected Output Content: same as Test 1
            assert input_file.read() == output_file_1.read().strip()
            assert output_file_1.read() == output_file_2.read()
            assert output_file_1.read() == output_file_3.read()

        # Test #4
        if not sample_writing_flag and not sample_reading_flag:
            # Expected Reading Outcome: same as Test 3
            assert my_cache.cache_dir_len() == 0
            # Expected Output Content: same as Test 1
            assert input_file.read() == output_file_1.read().strip()
            assert output_file_1.read() == output_file_2.read()
            assert output_file_1.read() == output_file_3.read()

# --------------------- Test Edge Cases: File Content -------------------------------------
# Note PickleCache does not work on empty file

    def test_small_file_content_edge_case(selfs, tmpdir):
        """
        Test whether PickleCache can detect slight change of a large file
        """
        # Instantiate original file folder
        tmp_dir = tmpdir.mkdir('original_file_temp')
        input_file = tmp_dir.join('ABC.csv')

        # Instantiate PickleCache
        my_cache = PickleCache(
            cache_dir=str(tmpdir.mkdir('cache_temp')),
            write_to_cache=True,
            read_from_cache=True,
            input_dir=tmp_dir
        )

        # Add the original content
        f = open(input_file, 'w')
        f.write('A' * (2**1) + 'A')
        f.close()
        content_1 = input_file.read()
        size_1 = os.stat(input_file).st_size

        df1 = my_cache.read_csv('ABC.csv', header=None)
        df1_content = df1.to_string()

        assert my_cache.cache_dir_len() == 1

        time.sleep(5)
        # --- Note, without sleeping, PickleCache can't recognize file with different
        # --- content when File Name and Modification/Creation Time are same.
        # --- To demo. comment this out.

        # Keep the file name but change the content
        f = open(input_file, 'w')
        f.write('A' * (2**1) + 'B')
        f.close()
        content_2 = input_file.read()
        size_2 = os.stat(input_file).st_size

        df2 = my_cache.read_csv('ABC.csv', header=None)
        df2_content = df2.to_string()

        assert size_1 == size_2
        assert content_1 != content_2
        assert df1_content != df2_content
        assert my_cache.cache_dir_len() == 2

    def test_large_file_content_edge_case(self, tmpdir):
        """
        Test whether PickleCache can detect slight change of a large file
        """

        # Instantiate original file folder
        tmp_dir = tmpdir.mkdir('original_file_temp')
        input_file = tmp_dir.join('ABC.csv')

        # Instantiate PickleCache
        my_cache = PickleCache(
            cache_dir=str(tmpdir.mkdir('cache_temp')),
            write_to_cache=True,
            read_from_cache=True,
            input_dir=tmp_dir
        )

        # Load the original file
        f = open(input_file, 'w')
        f.write('A' * (2**25) + 'A')
        f.close()
        content_1 = input_file.read()
        size_1 = os.stat(input_file).st_size

        df1 = my_cache.read_csv('ABC.csv', header=None)
        df1_content = df1.to_string()

        assert my_cache.cache_dir_len() == 1

        # input_file = tmp_dir.join('eggs.csv')
        f = open(input_file, 'w')
        f.write('A' * (2**25) + 'B')
        f.close()
        content_2 = input_file.read()
        size_2 = os.stat(input_file).st_size

        df2 = my_cache.read_csv('ABC.csv', header=None)
        df2_content = df2.to_string()

        assert size_1 == size_2
        assert content_1 != content_2
        assert df1_content != df2_content
        assert my_cache.cache_dir_len() == 2

# -------------------------- Test File Name Edge Cases ---------------------------------------

    def test_filename_edge_case(self, tmpdir):
        '''
        Testing two files with same content and different filename
        filename length: short (1) and long (230)
        Note: the maximum length of file name is 255.
        '''

        # Instantiate original file folder
        tmp_dir = tmpdir.mkdir('original_file_temp')

        # Instantiate PickleCache
        my_cache = PickleCache(
            cache_dir=str(tmpdir.mkdir('cache_temp')),
            write_to_cache=True,
            read_from_cache=True,
            input_dir=tmp_dir
        )
        filename_1 = 'A' * file_name_arg[1] + 'A.csv'
        input_file = tmp_dir.join(filename_1)
        input_file.write('A'*(2**20))

        df1 = my_cache.read_csv(filename_1, header=None)

        filename_2 = 'A' * file_name_arg[1] + 'B.csv'
        input_file = tmp_dir.join(filename_2)
        input_file.write('A'*(2**20))

        df2 = my_cache.read_csv(filename_2, header=None)

        assert filename_1 != filename_2
        assert my_cache.cache_dir_len() == 2

# -------------------------- Test Function Argument Edge Case -----------------------------------

    def test_function_change_output_only(self, tmpdir):
        """
        Real case: if user find a mistake in the function output and correct the fuction
        without changing the name and input parameter of the function, PickleCache will
        not help.

        This is not the problem to be solved by CACHE but need to provide PRECAUTION message to
        the users that they need to make sure the function itself is correct.
        """
        # Instantiate PickleCache
        my_cache = PickleCache(
            cache_dir=str(tmpdir),
            write_to_cache=True,
            read_from_cache=True)

        def temp_func(a, b):
            return a*b + 1

        original_func = temp_func
        new_func = my_cache(original_func)
        output_1 = new_func(2, 3)

        def temp_func(a, b):
            return a*b

        original_func = temp_func
        new_func = my_cache(original_func)
        output_2 = new_func(2, 3)

        assert output_1 != output_2

    def test_function_tiny_change(self, tmpdir):
        """
        Test small changes to the input parameter for a one-arg function
        """
        # Instantiate PickleCache
        my_cache = PickleCache(
            cache_dir=str(tmpdir),
            write_to_cache=True,
            read_from_cache=True)

        def temp_func(data):
            return data

        original_func = temp_func
        new_func = my_cache(original_func)
        output_1 = new_func('A'*(2**20)+'A')
        output_2 = new_func('A'*(2**20)+'B')

        assert output_1 != output_2
        assert my_cache.cache_dir_len() == 2

    def test_function_multiple_data_type(self, tmpdir):
        """
        Test a function with three arguments:
        1. change 1 argument
        2. change 2 argument
        3. change 3 argument
        The argument are complex combination of different data types.
        For the edge case, test small change
        """

        # Instantiate PickleCache
        my_cache = PickleCache(
            cache_dir=str(tmpdir),
            write_to_cache=True,
            read_from_cache=True)

        arg_1 = dict(zip([i for i in range(1, 1001)],
                         [(i*2, ['A', i]) for i in range(1, 1000)] + [(2000, 1)]))
        arg_2 = dict(zip([i for i in range(1, 1001)],
                         [(i*2, ['A', i]) for i in range(1, 1000)] + [(2000, 1.0001)]))

        def temp_func(a, b, c):
            return 1

        original_func = temp_func
        new_func = my_cache(original_func)
        run_1 = new_func(arg_1, arg_1, arg_1)
        assert my_cache.cache_dir_len() == 1

        run_2 = new_func(arg_2, arg_1, arg_1)
        assert run_1 == run_2
        assert my_cache.cache_dir_len() == 2

        run_3 = new_func(arg_2, arg_2, arg_1)
        assert run_1 == run_3
        assert my_cache.cache_dir_len() == 3

        run_4 = new_func(arg_2, arg_2, arg_2)
        assert run_1 == run_4
        assert my_cache.cache_dir_len() == 4

# --------- Test PickleCache extension: User Class, 3rd Party Class ---------------------

    def test_user_class_1(self, tmpdir, sample_writing_flag):
        # Test PickleCache on Class Method of User Created Class
        # Instantiate PickleCache
        my_cache = PickleCache(
            cache_dir=str(tmpdir),
            write_to_cache=sample_writing_flag,
            read_from_cache=True)

        def if_tsla(stock: StockCache):
            return True if stock.ticker.upper() == 'TSLA' else False

        cache_if_tsla = my_cache(if_tsla)
        stock1 = StockCache(ticker='TSLA', action='BUY')
        stock2 = StockCache(ticker='AAPL', action='BUY')
        if_tsla(stock1)
        if_tsla(stock2)
        # Original function should not generate cache
        assert my_cache.cache_dir_len() == 0
        if sample_writing_flag:
            cache_if_tsla(stock1)
            cache_if_tsla(stock2)
            # Cached function should generate 2 cache file for TSLA and AAPL
            assert my_cache.cache_dir_len() == 2
            assert cache_if_tsla(stock1) == if_tsla(stock1)
            assert cache_if_tsla(stock2) == if_tsla(stock2)
            assert cache_if_tsla(stock1) != if_tsla(stock2)
            # No new cache file should be generated since stock2 == stock2
            stock2 = StockCache(ticker='TSLA', action='BUY')
            assert my_cache.cache_dir_len() == 2
        elif not sample_writing_flag:
            cache_if_tsla(stock1)
            cache_if_tsla(stock2)
            assert my_cache.cache_dir_len() == 0

    def test_user_class_2(self, tmpdir):
        # Test PickleCache on Instance Method of User Created Class
        # Instantiate PickleCache
        my_cache = PickleCache(
            cache_dir=str(tmpdir),
            write_to_cache=False,
            read_from_cache=False)

        def if_tsla(stock: StockCache):
            return True if stock.ticker.upper() == 'TSLA' else False

        stock1 = StockCache(ticker='TSLA', action='BUY')
        stock2 = StockCache(ticker='AAPL', action='BUY')

        cache_if_tsla = my_cache(if_tsla)
        cache_if_tsla(stock1)
        cache_if_tsla(stock2)
        # No Cache file should be generated since the default for
        # write_to_cache and read_from_cache are False
        assert my_cache.cache_dir_len() == 0

        # Update the cache argument with my_cache instance
        my_cache.write_to_cache = True
        my_cache.read_from_cache = True
        cache_if_tsla = my_cache(if_tsla)
        cache_if_tsla(stock1)
        cache_if_tsla(stock2)
        # Now two cache file should be generated
        assert my_cache.cache_dir_len() == 2

    def test_user_class_static_method(self, tmpdir, sample_writing_flag):
        # Instantiate PickleCache
        my_cache = PickleCache(
            cache_dir=str(tmpdir),
            write_to_cache=sample_writing_flag,
            read_from_cache=True)

        class StockCache2:
            def __init__(self, ticker, action):
                self.ticker = ticker
                self.action = action

            def fingerprint_repr(self, _: FingerprintReprBuilder) -> str:
                fingerprint_str = type(self).__name__
                fingerprint_str += self.ticker
                fingerprint_str += self.action
                assert len(fingerprint_str), "fingerpint_repr can not return an empty string"
                return fingerprint_str

            def slim_repr(self, srepr_builder: SlimReprBuilder) -> str:
                return "Stock_" + self.ticker

            @my_cache
            def stock_return_1(self, year):
                time.sleep(2)
                return 1.5

            @my_cache
            def stock_return_2(self, ticker):
                time.sleep(2)
                return 1.5

        stock1 = StockCache2('TSLA', 'BUY')
        stock2 = StockCache2('AAPL', 'BUY')

        stock1.stock_return_1(2019)
        if sample_writing_flag:
            assert my_cache.cache_dir_len() == 1
        else:
            assert my_cache.cache_dir_len() == 0

        stock2.stock_return_1(2019)
        if sample_writing_flag:
            assert my_cache.cache_dir_len() == 2
        else:
            assert my_cache.cache_dir_len() == 0

        stock1.stock_return_2('TSLA')
        if sample_writing_flag:
            assert my_cache.cache_dir_len() == 3
        else:
            assert my_cache.cache_dir_len() == 0

        # Now Stock2 == Stock1 No new cache should be created
        stock2 = StockCache2('TSLA', 'BUY')
        stock2.stock_return_1(2019)
        if sample_writing_flag:
            assert my_cache.cache_dir_len() == 3
        else:
            assert my_cache.cache_dir_len() == 0

        stock2.stock_return_2('TSLA')
        if sample_writing_flag:
            assert my_cache.cache_dir_len() == 3
        else:
            assert my_cache.cache_dir_len() == 0

    def test_user_class_class_method(self, tmpdir):
        # Testing manually activating cache at the class level
        # Added a class argument whether to cache
        # Instantiate PickleCache
        my_cache = PickleCache(
            cache_dir=str(tmpdir),
            write_to_cache=False,
            read_from_cache=False)

        class StockCache2:
            def __init__(self, ticker, action, cache=False):
                self.ticker = ticker
                self.action = action
                self.write_to_cache=cache
                self.read_from_cache=cache

            def fingerprint_repr(self, _: FingerprintReprBuilder) -> str:
                fingerprint_str = type(self).__name__
                fingerprint_str += self.ticker
                fingerprint_str += self.action
                assert len(fingerprint_str), "fingerpint_repr can not return an empty string"
                return fingerprint_str

            def slim_repr(self, srepr_builder: SlimReprBuilder) -> str:
                return "Stock_" + self.ticker

            @my_cache
            def stock_return(self, year):
                time.sleep(2)
                return 1.5

        stock1 = StockCache2('TSLA', 'BUY')
        stock1.stock_return(2019)
        assert my_cache.cache_dir_len() == 0

        stock2 = StockCache2('TSLA', 'BUY', True)
        stock2.stock_return(2019)
        assert my_cache.cache_dir_len() == 1

    def test_user_class_instance_method(self, tmpdir):
        # Manually update read and write cache at instance level
        # The default value of reading and writing cache files are
        # Set to False
        # Instantiate PickleCache
        my_cache = PickleCache(
            cache_dir=str(tmpdir),
            write_to_cache=False,
            read_from_cache=False)

        class StockCache3:
            def __init__(self, ticker, action):
                self.ticker = ticker
                self.action = action

            def fingerprint_repr(self, _: FingerprintReprBuilder) -> str:
                fingerprint_str = type(self).__name__
                fingerprint_str += self.ticker
                fingerprint_str += self.action
                assert len(fingerprint_str), "fingerpint_repr can not return an empty string"
                return fingerprint_str

            def slim_repr(self, srepr_builder: SlimReprBuilder) -> str:
                return "Stock_" + self.ticker

            @my_cache
            def stock_return(self, year):
                time.sleep(1)
                return 1.5

        stock1 = StockCache3('TSLA', 'BUY')
        stock2 = StockCache3('AAPL', 'BUY')

        stock1.stock_return(2019)
        assert my_cache.cache_dir_len() == 0

        stock2.stock_return(2019)
        assert my_cache.cache_dir_len() == 0

        stock1.write_to_cache = True
        stock1.read_from_cache = True
        stock1.stock_return(2019)
        assert my_cache.cache_dir_len() == 1

        stock2.stock_return(2019)
        assert my_cache.cache_dir_len() == 1

        stock2.write_to_cache = True
        stock2.read_from_cache = True
        stock1.stock_return(2019)
        assert my_cache.cache_dir_len() == 1

        stock2.stock_return(2019)
        assert my_cache.cache_dir_len() == 2
















