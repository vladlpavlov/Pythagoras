
from pathlib import Path

from Pythagoras import SimpleDict, FileDirDict
import pandas as pd
import os


def validate_dict_object(dict_to_test):
    dict_to_test.clear()
    model_dict = dict()

    assert len(dict_to_test) == 0
    for i in range(10):
        k = ("_"+str(10*i),)
        dict_to_test[k] = i
        dict_to_test[k] = i+ 1
        model_dict[k] = i
        model_dict[k] = i + 1

        k = (i + 1) * (str(i) + "zz",)
        dict_to_test[k] = "hihi"
        model_dict[k] = "hihi"

        new_key = ("new_key", str(i))
        assert (dict_to_test.setdefault(new_key, 1) ==
                model_dict.setdefault(("new_key", str(i)), 1))

        assert (dict_to_test.setdefault(new_key, 2) ==
                model_dict.setdefault(new_key, 2))

        assert (dict_to_test.pop(new_key, 2) ==
                model_dict.pop(new_key, 2))

    assert dict_to_test == dict_to_test
    assert dict_to_test == model_dict
    for v in model_dict:
        assert v in dict_to_test

    assert (len(dict_to_test)
            == len(list(dict_to_test.keys()))
            == len(list(dict_to_test.values()))
            == len(list(dict_to_test.items())))

    for j in range(len(dict_to_test)):
        dict_to_test.popitem()
        model_dict.popitem()

    assert len(dict_to_test) == 0

    dict_to_test["z"] = pd.DataFrame({"a": [1, 2, 3, 4, 5]})
    model_dict["z"] = pd.DataFrame({"a": [1, 2, 3, 4, 5]})
    assert (dict_to_test["z"] == model_dict["z"]).sum().sum() == 5

    dict_to_test.clear()
    model_dict.clear()

    assert len(dict_to_test) == 0

def test_FileDirDict(tmpdir):
    p = FileDirDict(dir_name = tmpdir, file_type="pkl")
    validate_dict_object(p)

    p1 = FileDirDict(dir_name=tmpdir, file_type="pkl")
    validate_dict_object(p1)

    j = FileDirDict(dir_name = tmpdir, file_type="json")
    validate_dict_object(j)

