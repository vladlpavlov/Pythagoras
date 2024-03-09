import sys
import traceback
import uuid
from typing import Optional, Callable

from IPython import get_ipython
from persidict import PersiDict

from pythagoras._source_code_processing.basic_utils import get_long_infoname

# TODO: add unit tests for this module

_old_excepthook: Optional[Callable] = None
_is_running_inside_IPython: Optional[bool] = None

crash_history: Optional[PersiDict] = None

class ExceptionInfo:
    """ Helper class for remote logging, encapsulates exception/environment info.

    This class is used to log information to crash_history persistent store.
    """

    def __init__(self, exc_type, exc_value, trace_back):
        assert isinstance(exc_value, BaseException)
        self.__name__ = get_long_infoname(exc_value)
        self.exception = exc_value
        self.exception_description = traceback.format_exception(
            exc_type, exc_value, trace_back)

def log_exception(entry:ExceptionInfo) -> None:
    global crash_history
    if not isinstance(crash_history, PersiDict):
        print("crash_history is not initialized with a PersiDict,"
              ," skipping exception logging")
        return
    entry_name = get_long_infoname(entry)
    entry_name += " "
    entry_name += str(uuid.uuid4())
    crash_history[entry_name] = entry

def cloud_excepthook(exc_type, exc_value, trace_back):
    exc_event = ExceptionInfo(exc_type, exc_value, trace_back)
    log_exception(exc_event)
    _old_excepthook(exc_type, exc_value, trace_back)
    return

def cloud_excepthandler(_, exc_type, exc_value, trace_back, tb_offset=None):
    exc_event = ExceptionInfo(exc_type, exc_value, trace_back)
    log_exception(exc_event)
    traceback.print_exception(exc_type, exc_value, trace_back)
    return

def register_exception_handlers() -> None:
    """ Intercept & redirect unhandled exceptions to crash_history """

    global _old_excepthook, _is_running_inside_IPython
    _old_excepthook = sys.excepthook
    sys.excepthook = cloud_excepthook

    try:  # if we are inside a notebook
        get_ipython().set_custom_exc(
            (BaseException,), cloud_excepthandler)
        _is_running_inside_IPython = True
    except:
        _is_running_inside_IPython = False