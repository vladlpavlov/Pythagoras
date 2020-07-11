from Pythagoras import *

class TestNeatStr:
    def test_mem_size(self):
        assert NeatStr.mem_size(1) == "1 B"
        assert NeatStr.mem_size(10,"_") == "10_B"
        assert NeatStr.mem_size(1023,"--") == "1023--B"
        assert NeatStr.mem_size(1024,"") == "1Kb"

        assert NeatStr.mem_size(1_048_576) == "1 Mb"

        assert NeatStr.mem_size(1_073_741_824) == "1 Gb"

        assert NeatStr.mem_size(1_099_511_627_776) == "1 Tb"

