from pythagoras import *

class TestNeatStr:
    def test_mem_size(self):
        assert NeatStr.mem_size(1) == "1 B"
        assert NeatStr.mem_size(10,"_") == "10_B"
        assert NeatStr.mem_size(1023,"--") == "1023--B"
        assert NeatStr.mem_size(1024,"") == "1Kb"
        assert NeatStr.mem_size(1_048_576) == "1 Mb"
        assert NeatStr.mem_size(1_073_741_824,"") == "1Gb"
        assert NeatStr.mem_size(1_099_511_627_776) == "1 Tb"

def test_get_long_infoname():
    assert "int" in get_long_infoname(10)
    assert "str" in get_long_infoname("QWERTY")
    assert get_long_infoname(FileDirDict())  == "pythagoras.persistent_dicts.FileDirDict"
    self_name = get_long_infoname(get_long_infoname)
    assert "function" in self_name
    assert "get_long_infoname" in self_name