import sys
import traceback

# from pythagoras._03_autonomous_functions.autonomous_funcs import AutonomousFunction
#
# from pythagoras._99_misc_utils.find_in_callstack import find_in_callstack
from pythagoras._99_misc_utils.current_date_gmt_str import (
    current_date_gmt_string)
from pythagoras._99_misc_utils.random_safe_str_creator import (
    get_random_safe_str)
from pythagoras._99_misc_utils.context_builder import build_context

import pythagoras as pth

from persidict import PersiDict

class EventLogger:
    def __init__(self
                 , event_log: PersiDict
                 , prefix: str = None
                 , save_context:bool = False):
        assert isinstance(event_log, PersiDict)
        assert prefix is None or isinstance(prefix, str)
        assert isinstance(save_context, bool)
        self.event_log = event_log
        self.prefix = prefix
        self.save_context = save_context

    def log_event(self, **kwargs):
        if self.save_context:
            context_param_name = "context"
            while context_param_name in kwargs:
                context_param_name += "_"
            kwargs[context_param_name] = build_context()

        name_part_1 = current_date_gmt_string()
        name_part_2 = get_random_safe_str()
        if self.prefix is not None:
            name_part_2 = self.prefix + "_" + name_part_2

        self.event_log[name_part_1, name_part_2] = kwargs

def log_uncaught_exception(**kwargs):
    # callers = find_in_callstack("self", AutonomousFunction)
    # caller_name = ""
    # if len(callers) > 0:
    #     caller_name = callers[0].name + "_"
    logger = EventLogger(event_log = pth.crash_history
        # , prefix = caller_name + "CRASH_"
        , save_context = True)
    logger.log_event(**kwargs)

# def log(**kwargs):
#     callers = find_in_callstack("self", AutonomousFunction)
#     caller_name = ""
#     if len(callers) > 0:
#         caller_name = callers[0].name + "_"
#     logger = EventLogger(event_log = pth.crash_history
#         , prefix = caller_name + "LOG_"
#         , save_context = False)
#     logger.log_event(**kwargs)


def pth_excepthook(exc_type, exc_value, trace_back) -> None:
    exception_description = traceback.format_exception(
        exc_type, exc_value, trace_back)
    log_uncaught_exception(exception = exc_value
        , exception_description = exception_description)
    sys.__excepthook__(exc_type, exc_value, trace_back)

def pth_excepthandler(_, exc_type, exc_value
                    , trace_back, tb_offset=None) -> None:
    exception_description = traceback.format_exception(
        exc_type, exc_value, trace_back)
    log_uncaught_exception(exception=exc_value
        , exception_description=exception_description)
    traceback.print_exception(exc_type, exc_value, trace_back)

def register_exception_handlers() -> None:
    sys.excepthook = pth_excepthook
    try:
        from IPython import get_ipython
        get_ipython().set_custom_exc((BaseException,), pth_excepthandler)
    except:
        pass

def unregister_exception_handlers() -> None:
    sys.excepthook = sys.__excepthook__
    try:
        from IPython import get_ipython
        get_ipython().set_custom_exc((BaseException,), None)
    except:
        pass