from pythagoras._04_idempotent_functions.astkeywords_dict_convertors import (
    convert_astkeywords_to_dict, convert_dict_to_astkeywords)
import ast


sample_dict_1 = {'a': 1, 'b': 22, 'c': 333}
sample_dict_2 = {'aa': "hello", 'bb': None}
sample_dict_3 = {'_a': None, '__b': None, '___c': 0.123456789}

def test_astkeywords_dict_convertors():

    dict_to_test= sample_dict_1
    a = convert_dict_to_astkeywords(dict_to_test)
    b = convert_astkeywords_to_dict(a)
    assert b == dict_to_test

    dict_to_test = sample_dict_2
    a = convert_dict_to_astkeywords(dict_to_test)
    b = convert_astkeywords_to_dict(a)
    assert b == dict_to_test

    dict_to_test = sample_dict_3
    a = convert_dict_to_astkeywords(dict_to_test)
    b = convert_astkeywords_to_dict(a)
    assert b == dict_to_test

