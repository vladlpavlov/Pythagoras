from pythagoras._06_mission_control.global_state_management import _clean_global_state
import pythagoras as pth

_clean_global_state()
pth.initialize("QQQQQQQQQQQQQQQQQQQQQQQQQQQQ")

@pth.idempotent()
def fff():
    print("Hello from fff")
    assert False

fff()