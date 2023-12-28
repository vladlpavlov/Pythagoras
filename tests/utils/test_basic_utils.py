from pythagoras._utils.basic_utils import *
from persidict import FileDirDict


def test_get_long_infoname(tmpdir):
    print("\n\n")
    assert ".int" in get_long_infoname(10)
    assert ".str" in get_long_infoname("QWERTY")
    dict_name = get_long_infoname(FileDirDict(dir_name=tmpdir))
    assert ".FileDirDict" in dict_name
    assert "persidict" in dict_name
