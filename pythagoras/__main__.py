from pythagoras._05_mission_control.global_state_management import _clean_global_state
import pythagoras as pth

_clean_global_state()
pth.initialize("QQQQQQQQQQQQQQQQQQQQQQQQQQQQ")
from IPython import get_ipython
ipython = get_ipython()
print(ipython.__class__.__name__)