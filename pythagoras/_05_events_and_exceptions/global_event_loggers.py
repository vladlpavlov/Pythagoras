import sys

from pythagoras._05_events_and_exceptions.execution_environment_summary import (
    add_execution_environment_summary)
from pythagoras._05_events_and_exceptions.current_date_gmt_str import (
    current_date_gmt_string)
from pythagoras._01_foundational_objects.hash_and_random_signatures import (
    get_random_signature)

import pythagoras as pth



def register_exception_globally(exception_id = None, **kwargs):
    path = current_date_gmt_string()
    exc_type, exc_value, trace_back = sys.exc_info()
    if exception_id is None:
        exception_id = exc_type.__name__ + "_" + get_random_signature()
    full_path = [path, exception_id]
    pth.crash_history[full_path] = add_execution_environment_summary(
        exc_value=exc_value, **kwargs)


def register_event_globally(event_id, *args, **kwargs):
    path = current_date_gmt_string()
    if event_id is None:
        event_id = get_random_signature()
    full_path = [path, event_id]
    pth.event_log[full_path] = add_execution_environment_summary(
        *args,**kwargs)
