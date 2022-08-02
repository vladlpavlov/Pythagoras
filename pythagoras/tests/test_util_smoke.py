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


def test_get_normalized_function_source():
    def fff():
        pass

    fff_source_1 = get_normalized_function_source(fff)

    def fff():
        #some comment

        pass #another comment

    fff_source_2 = get_normalized_function_source(fff)

    assert fff_source_1 == fff_source_2

    def fff():
        return

    fff_source_3 = get_normalized_function_source(fff)

    assert fff_source_3 != fff_source_2

    def ggg(a):
        for i in range(10):pass
        return a * a

    ggg_source_1 = get_normalized_function_source(ggg)

    def ggg(a):
        for i in range(10):
            pass ###########
        return a*a # qwerty

    ggg_source_2 = get_normalized_function_source(ggg)

    assert ggg_source_1==ggg_source_2

    def ggg(a):
        for i in range(10):pass
        return a ** 2

    ggg_source_3 = get_normalized_function_source(ggg)

    assert ggg_source_3 != ggg_source_2



class MMM:
    pass

def check2_subfunction():
    assert detect_instance_method_in_callstack(TTT)[0] is t
    assert detect_instance_method_in_callstack(MMM) is None

class TTT:
    def check(self):
        assert detect_instance_method_in_callstack(TTT)[0] is t

    def check2(self):
        check2_subfunction()

t = TTT()

def test_detect_instance_method_in_callstack():
    assert detect_instance_method_in_callstack(TTT) is None
    t.check()
    t.check2()






