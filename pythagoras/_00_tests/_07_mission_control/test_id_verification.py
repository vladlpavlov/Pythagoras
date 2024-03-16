import pytest
import pythagoras as pth
from pythagoras._03_autonomous_functions.names_usage_analyzer import *

def good_f(a,b,s):
    return a+b+s

def bad_f_1(a,_pth_b,c):
    return a+_pth_b+c

def bad_f_2(a,b,c):
    return a+b._pth_some_attribute__+c

def _pth_bad_f_3(a,b,c):
    return a+b+c


def test_id_verification_names_analyzer():
    analyze_names_in_function(good_f)
    with pytest.raises(Exception):
        analyze_names_in_function(bad_f_1)
    with pytest.raises(Exception):
        analyze_names_in_function(bad_f_2)
    with pytest.raises(Exception):
        analyze_names_in_function(_pth_bad_f_3)