import sys
import traceback
from copy import copy

from pythagoras._05_events_and_exceptions.context_utils import add_context
from pythagoras._05_events_and_exceptions.current_date_gmt_str import (
    current_date_gmt_string)
from pythagoras._05_events_and_exceptions.find_in_callstack import (
    find_local_var_in_callstack)
from pythagoras._05_events_and_exceptions.type_retrievers import (
    retrieve_AutonomousFunction_class, retrieve_FuncOutputAddress_class)
from pythagoras import get_random_signature

from persidict import PersiDict
import pythagoras as pth


def log_one_entry(event_log_dict:PersiDict
        , path:list[str] | None
        , prefixes: list[str] | None
        , name:str
        , event:any):
    if prefixes is not None and len(prefixes) > 0:
        name = "_".join(prefixes + [name])
    if path is None or len(path) == 0:
        address = [name]
    else:
        address = path + [name]
    event_log_dict[address] = event

def log_two_mirrored_entries(
        global_event_log_dict:PersiDict | None
        , local_event_log_dict:PersiDict | None
        , prefix: str | None
        , event: any):

    func_addrs = find_local_var_in_callstack(name_to_find="_pth_f_addr_"
            , class_to_find = retrieve_FuncOutputAddress_class())

    island_name = None
    function_name = None
    local_path = None

    if len(func_addrs) > 0:
        func_pointer = func_addrs[0]
        local_path = list(func_pointer)
        island_name = func_pointer.island_name
        function_name = func_pointer.f_name
    else:
        funcs = find_local_var_in_callstack(name_to_find="self"
            , class_to_find=retrieve_AutonomousFunction_class())
        if len(funcs) > 0:
            func_pointer = funcs[0]
            island_name = func_pointer.island_name
            function_name = func_pointer.f_name

    event_name = get_random_signature()

    if prefix is not None:
        prefixes = [prefix]
    else:
        prefixes = []

    if global_event_log_dict is not None:
        if island_name is not None:
            global_prefixes = [island_name] + prefixes
        else:
            global_prefixes = copy(prefixes)
        if function_name is not None:
            global_prefixes = [function_name] + global_prefixes
        global_path = [current_date_gmt_string()]
        log_one_entry(global_event_log_dict
            , global_path, global_prefixes, event_name, event)

    if local_event_log_dict is not None and local_path is not None:
        local_prefixes = copy(prefixes)
        log_one_entry(local_event_log_dict
            , local_path, local_prefixes, event_name, event)


def log_exception(**kwargs):
    (exc_type, exc_value, trace_back) = sys.exc_info()
    description = traceback.format_exception(
        exc_type, exc_value, trace_back)
    event = add_context(
        exception_description=description
        ,exception=exc_value
        ,trace_back= trace_back)
    event.update(kwargs)
    log_two_mirrored_entries(
        global_event_log_dict=pth.global_crash_history
        , local_event_log_dict=pth.function_crash_history
        , prefix=exc_type.__name__
        , event=event)