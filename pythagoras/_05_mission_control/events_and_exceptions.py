import os
import importlib.metadata
from getpass import getuser
import socket
from typing import Any, Optional, TypeVar, Type, Dict
import inspect

import psutil

import pythagoras as pth

from datetime import datetime, timezone

from pythagoras._99_misc_utils.random_safe_str_creator import get_random_safe_str


T = TypeVar("T")
def detect_local_variable_in_callstack(
        name_to_detect:str
        , class_to_detect: Type[T]
        ) -> Optional[T]:
    """Given its name and type, find an object in outer frames.

    If the callstack contains a local object
    with name name_to_detect and type class_to_detect,
    the function will return this object,
    otherwise the return value is None.
    The search starts from the innermost frames,
    and ends once the first match is found.
    """


    assert inspect.isclass(class_to_detect)
    assert isinstance(name_to_detect, str)
    assert len(name_to_detect)

    for frame_record in inspect.stack():
        if name_to_detect not in frame_record.frame.f_locals:
            continue
        candidate = frame_record.frame.f_locals[name_to_detect]
        if isinstance(candidate, class_to_detect):
            return candidate

    return None


def get_hardware_context(file_path:str=None, time_zone=None)-> Dict:
    """Capture core information about the current execution environment.

    The function is supposed to be used to log environment information
    to help debugging distributed applications.
    """

    result = dict(
        hostname = socket.gethostname()
        ,user = getuser()
        ,pid = os.getpid()
        ,platform = platform.platform()
        ,python_implementation = platform.python_implementation()
        ,python_version = platform.python_version()
        ,processor = platform.processor()
        ,cpu_count = psutil.cpu_count()
        ,cpu_load_avg = psutil.getloadavg()
        ,disk_usage = psutil.disk_usage(file_path)
        ,virtual_memory = psutil.virtual_memory()
        )

    return result


import platform
import importlib.metadata


def get_python_context() -> dict:
    """
    Retrieves information about the current Python execution environment.

    This function returns a dictionary containing the Python version
    and a list of installed packages along with their versions.

    Returns:
        dict: A dictionary with two keys:
              - 'Python Version': A string representing the current Python version.
              - 'Installed Packages': A dictionary of installed packages where
                                      keys are package names and values are their versions.
    """

    python_version = platform.python_version()
    python_implementation = platform.python_implementation(),

    installed_packages = {
        distribution.metadata['Name']: distribution.version
            for distribution in importlib.metadata.distributions()}

    # Combine all collected data into a single dictionary
    python_context = dict(python_version=python_version,
         python_implementation = python_implementation,
         installed_packages =installed_packages )

    return python_context


class DataLogEntry:
    function:Optional[str]
    arguments:Optional[dict]
    computer:Optional[dict]
    python:Optional[dict]
    pythagoras:Optional[dict]
    timestamp:Optional[datetime]
    def __init__(self):
        try:
            self.computer = get_hardware_context()
        except:
            self.computer = None
        try:
            self.python = get_python_context()
        except:
            self.python = None

        self.timestamp = datetime.now(timezone.utc)
        #TODO: add function name, arguments and return value

class ExceptionLogEntry(DataLogEntry):
    def __init__(self, exception:Exception, output:str=None):
        self.exception = exception
        if output is not None:
            self.output = output
        super().__init__()

class FunctionCompletionLogEntry(DataLogEntry):
    def __init__(self, return_value:Any,output:str=None):
        if output is not None:
            self.output = output
        self.return_value = return_value
        super().__init__()

class EventLogEntry(DataLogEntry):
    def __init__(self, exception:Exception, output:str=None):
        if output is not None:
            self.output = output
        self.exception = exception
        super().__init__()

def get_current_date_gmt():
    """
    Returns the current date in GMT as a tuple with three strings:
    (year, month, day). Month and day are formatted with two digits.
    """

    now = datetime.now(timezone.utc)
    year = str(now.year)
    month = now.strftime('%m')
    day = now.strftime('%d')

    return [year, month, day]

def post_crash_report(exception:Any, output:str=None): #TODO: refactor
    crash_report_name = 'crash_' + get_random_safe_str()
    event_key = get_current_date_gmt() + [crash_report_name]
    pth.crash_history[event_key] = ExceptionLogEntry(exception,output)




