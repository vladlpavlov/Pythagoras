from __future__ import annotations
import os
import sys
import traceback
import random
from typing import Optional

import pandas as pd
from persidict import PersiDict, FileDirDict

from pythagoras._010_basic_portals.foundation import BasicPortal, _persistent
from pythagoras._820_strings_signatures_converters.current_date_gmt_str import (
    current_date_gmt_string)
from pythagoras._020_logging_portals.execution_environment_summary import (
    build_execution_environment_summary)
from pythagoras._020_logging_portals.notebook_checker import is_executed_in_notebook
from pythagoras._820_strings_signatures_converters.random_signatures import (
    get_random_signature)


def pth_excepthook(exc_type, exc_value, trace_back) -> None:
    LoggingPortal._exception_logger()
    sys.__excepthook__(exc_type, exc_value, trace_back)

def pth_excepthandler(_, exc_type, exc_value
                    , trace_back, tb_offset=None) -> None:
    LoggingPortal._exception_logger()
    traceback.print_exception(exc_type, exc_value, trace_back)

_previous_excepthook = None
def register_systemwide_uncaught_exception_handlers() -> None:
    if not is_executed_in_notebook():
        _previous_excepthook = sys.excepthook
        sys.excepthook = pth_excepthook
        pass
    else:
        try:
            from IPython import get_ipython
            get_ipython().set_custom_exc((BaseException,), pth_excepthandler)
        except:
            _previous_excepthook = sys.excepthook
            sys.excepthook = pth_excepthook


def unregister_systemwide_uncaught_exception_handlers() -> None:
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


# def log_exception(exception_id=None,exception_prefix= None, **kwargs):
#     LoggingPortal.log_exception(
#         exception_id=exception_id
#         ,exception_prefix = exception_prefix
#         ,**kwargs)



def log_event(*args, **kwargs):
    if "event_id" in kwargs:
        event_id = kwargs["event_id"]
        del kwargs["event_id"]
    else:
        event_id = None
    LoggingPortal.log_event(event_id, *args, **kwargs)


# class LoggedException(Exception):
#     """An exception that is logged into the portal's crash history"""
#     def __init__(self, message:str, **kwargs):
#         super().__init__(message)
#         self.kwargs = kwargs


class NeedsRandomization(str):
    """A string that needs to be randomized"""
    pass

class AlreadyRandomized(str):
    """A string that has already been randomized"""
    pass


class LoggingPortal(BasicPortal):
    """A portal that supports app-level logging for events and exceptions.

    This class extends BasicPortal to provide application-level logging
    capabilities for events and exceptions. 'Application-level' means that
    the events and exceptions are logged into location(s) that is(are) the same
    across the entire application, and does not depend on the specific function
    from which the even or exception is raised.

    The class provides two dictionaries, `crash_history` and `event_log`,
    to store the exceptions history and event log respectively.

    Static methods `log_exception` and `log_event` are provided to log
    exceptions and events. These methods are designed to be
    called from anywhere in the application, and they will log the exception
    or event into all the active LoggingPortals. 'Active' LoggingPortals are
    those that have been registered with the current
    stack of nested 'with' statements.

    The class also supports logging uncaught exceptions globally.
    """

    exception_handlers_registered: bool = False
    entropy_infuser: random.Random | None = random.Random()

    crash_history: PersiDict | None
    event_log: PersiDict | None

    def __init__(self
            , base_dir:str | None = None
            , dict_type:type = FileDirDict
            ):
        super().__init__(base_dir, dict_type)

        crash_history_dir = os.path.join(base_dir, "crash_history")
        crash_history = dict_type(
            crash_history_dir, digest_len=0
            , file_type="json", immutable_items=True)
        self.crash_history = crash_history

        event_log_dir = os.path.join(base_dir, "event_log")
        event_log = dict_type(
            event_log_dir, digest_len=0
            , file_type="json", immutable_items=True)
        self.event_log = event_log

        if not LoggingPortal.exception_handlers_registered:
            register_systemwide_uncaught_exception_handlers()
        LoggingPortal.exception_handlers_registered = True


    def _clear(self) -> None:
        """Clear the portal's state"""
        self.crash_history = None
        self.event_log = None
        super()._clear()

    def describe(self) -> pd.DataFrame:
        """Get a DataFrame describing the portal's current state"""
        all_params = [super().describe()]
        all_excpt_path = ("__CATCH_ALL__",)
        todays_excpt_path = ("__CATCH_ALL__", current_date_gmt_string())
        all_params.append(_persistent(
            "Exceptions, total"
            , len(self.crash_history.get_subdict(all_excpt_path))))
        all_params.append(_persistent(
            "Exceptions, today"
            , len(self.crash_history.get_subdict(todays_excpt_path))))

        result = pd.concat(all_params)
        result.reset_index(drop=True, inplace=True)

        return result

    @classmethod
    def get_portal(cls, suggested_portal:Optional[LoggingPortal]=None
               ) -> LoggingPortal:
        return BasicPortal.get_portal(suggested_portal)


    @classmethod
    def get_current_portal(cls) -> LoggingPortal | None:
        return BasicPortal._current_portal(expected_class=LoggingPortal)

    @classmethod
    def get_noncurrent_portals(cls) -> list[LoggingPortal]:
        return BasicPortal._noncurrent_portals(expected_class=cls)

    @classmethod
    def get_active_portals(cls) -> list[LoggingPortal]:
        return BasicPortal._active_portals(expected_class=cls)

    @classmethod
    def _clear_all(cls) -> None:
        """Remove all information about all the portals from the system."""
        if LoggingPortal.exception_handlers_registered:
            unregister_systemwide_uncaught_exception_handlers()
        LoggingPortal.exception_handlers_registered = False
        # LoggingPortal.processed_exceptions = deque(maxlen=100)
        LoggingPortal.entropy_infuser = random.Random()
        super()._clear_all()


    @staticmethod
    def make_unique_name(desired_name:str, existing_names) -> str:
        """Make a name unique by adding a random suffix to it."""
        candidate = desired_name
        entropy_infuser = LoggingPortal.entropy_infuser
        while candidate in existing_names:
            candidate = desired_name + "_"
            random_number = entropy_infuser.randint(1,10_000_000_000)
            candidate += str(random_number)
        return candidate

    @staticmethod
    def add_execution_environment_summary(*args, **kwargs):
        """Add execution environment summary to kwargs. """
        context_param_name = "execution_environment_summary"
        context_param_name = LoggingPortal.make_unique_name(
            desired_name=context_param_name, existing_names=kwargs)
        kwargs[context_param_name] = build_execution_environment_summary()
        if len(args):
            message_param_name = "message_list"
            message_param_name = LoggingPortal.make_unique_name(
                desired_name=message_param_name, existing_names=kwargs)
            kwargs[message_param_name] = args
        return kwargs


    @staticmethod
    def _persist_exception_information(
            exc_type, exc_value, trace_back
            , exception_prefixes:list[list[str]]
            , exception_id:str
            , exception_extra_data_to_persist:dict
            ) -> dict|None:

        if exc_type is None:
            return None

        if not LoggingPortal._exception_needs_to_be_processed(
                exc_type, exc_value, trace_back):
            return None

        assert isinstance(exception_id, NeedsRandomization) or isinstance(
            exception_id, AlreadyRandomized)

        traceback_long_str = "".join(traceback.format_exception(
            exc_type, exc_value, trace_back))
        traceback_list_of_str = traceback_long_str.split("\n")

        exception_data_to_persist = dict(exception=exc_value
            , exception_traceback=traceback_list_of_str)
        exception_data_to_persist |= exception_extra_data_to_persist

        if isinstance(exception_id, NeedsRandomization):
            exception_id += "_"+get_random_signature()

        for prefix in exception_prefixes:
            full_path = prefix + [exception_id]
            for portal in LoggingPortal.get_active_portals():
                portal.crash_history[full_path] = exception_data_to_persist

        LoggingPortal._mark_exception_as_processed(
            exc_type, exc_value, trace_back)

        return exception_data_to_persist

    # @staticmethod
    # def _exception_signature(exc_value, exc_type, trace_back) -> tuple:
    #     return (id(exc_value), id(exc_type), trace_back.tb_lineno)
    #             # , id(trace_back), trace_back.tb_lineno)

    @staticmethod
    def _mark_exception_as_processed(exc_type, exc_value, trace_back) -> None:
        # exception_signature = LoggingPortal._exception_signature(
        #     exc_value, exc_type, trace_back)
        # LoggingPortal.processed_exceptions.append(exception_signature)
        if hasattr(exc_value, "add_note"):
            exc_value.add_note(
                "__suppress_logging__")
        else:
            exc_value.__suppress_logging__ = True

    @staticmethod
    def _exception_needs_to_be_processed(exc_type, exc_value, trace_back) -> bool:
        if exc_type is None:
            return False

        if hasattr(exc_value, "__notes__"):
            if "__suppress_logging__" in exc_value.__notes__:
                return False
            else:
                return True

        if hasattr(exc_value, "__suppress_logging__"):
            return False

        return True
        # exception_signature = LoggingPortal._exception_signature(
        #     exc_value, exc_type, trace_back)
        # return exception_signature not in LoggingPortal.processed_exceptions


    @staticmethod
    def _exception_prefixes() -> list[list[str]]:
        return [["__CATCH_ALL__", current_date_gmt_string()]]

    @staticmethod
    def _exception_id(exc_value) -> str:
        return NeedsRandomization(exc_value.__class__.__name__)

    @staticmethod
    def _extra_exception_data() -> dict:
        return build_execution_environment_summary()

    @staticmethod
    def _exception_logger():
        exc_type, exc_value, trace_back = sys.exc_info()

        if not LoggingPortal._exception_needs_to_be_processed(
                exc_type, exc_value, trace_back):
            return

        exception_prefixes = LoggingPortal._exception_prefixes()
        exception_id = LoggingPortal._exception_id(exc_value)
        extra_exception_data = LoggingPortal._extra_exception_data()

        LoggingPortal._persist_exception_information(
            exc_type, exc_value, trace_back
            , exception_prefixes, exception_id, extra_exception_data)


    def __exit__(self, exc_type, exc_val, exc_tb):
        LoggingPortal._exception_logger()
        super().__exit__(exc_type, exc_val, exc_tb)
        return False

    @staticmethod
    def log_event(event_id:str|None=None, *args, **kwargs):
        #TODO: refuctor to mimic log_exception
        path = current_date_gmt_string()
        if event_id is None:
            event_id = get_random_signature()
        full_path = [path, event_id]

        event_to_log = LoggingPortal.add_execution_environment_summary(
            *args, **kwargs)

        for portal in LoggingPortal.get_active_portals():
            portal.event_log[full_path] = event_to_log