import sys, traceback

from pythagoras._05_events_and_exceptions.notebook_checker import is_executed_in_notebook
from pythagoras._05_events_and_exceptions.global_event_loggers import (
    register_exception_globally)

import pythagoras as pth


# def log_uncaught_exception(exception: Exception, **kwargs):
#     logger = EventLogger(event_log = pth.crash_history
#         , prefix = "__none__"+ exception.__class__.__name__
#         , save_context = True)
#     logger.log_event(exception=exception, **kwargs)




def pth_excepthook(exc_type, exc_value, trace_back) -> None:
    # exception_description = traceback.format_exception(
    #     exc_type, exc_value, trace_back)
    # log_uncaught_exception(exception = exc_value
    #     , exception_description = exception_description)
    register_exception_globally()
    sys.__excepthook__(exc_type, exc_value, trace_back)

def pth_excepthandler(_, exc_type, exc_value
                    , trace_back, tb_offset=None) -> None:
    # exception_description = traceback.format_exception(
    #     exc_type, exc_value, trace_back)
    # log_uncaught_exception(exception=exc_value
    #     , exception_description=exception_description)
    register_exception_globally()
    traceback.print_exception(exc_type, exc_value, trace_back)


_previous_excepthook = None
def register_exception_handlers() -> None:
    if not is_executed_in_notebook():
        _previous_excepthook = sys.excepthook
        sys.excepthook = pth_excepthook
    else:
        try:
            from IPython import get_ipython
            get_ipython().set_custom_exc((BaseException,), pth_excepthandler)
        except:
            _previous_excepthook = sys.excepthook
            sys.excepthook = pth_excepthook

def unregister_exception_handlers() -> None:

    global _previous_excepthook
    if _previous_excepthook is not None:
        sys.excepthook = _previous_excepthook
        _previous_excepthook = None

    if is_executed_in_notebook():
        try:
            from IPython import get_ipython
            get_ipython().set_custom_exc((BaseException,), None)
        except:
            pass