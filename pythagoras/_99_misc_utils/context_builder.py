import psutil
import os
import platform
import socket
from typing import Dict
from getpass import getuser
from datetime import datetime
from pythagoras._99_misc_utils.notebook_checker import is_executed_in_notebook

def build_context()-> Dict:
    """Capture core information about execution environment.

    The function is intended to be used to log environment information
    to help debug (distributed) applications.
    """
    cwd = os.getcwd()
    is_in_notebook = is_executed_in_notebook()

    context = dict(
        hostname = socket.gethostname()
        ,user = getuser()
        ,pid = os.getpid()
        ,platform = platform.platform()
        ,python_implementation = platform.python_implementation()
        ,python_version = platform.python_version()
        ,processor = platform.processor()
        ,cpu_count = psutil.cpu_count()
        ,cpu_load_avg = psutil.getloadavg()
        ,disk_usage = psutil.disk_usage(cwd)
        ,virtual_memory = psutil.virtual_memory()
        ,cwd = os.getcwd()
        ,working_directory = cwd
        ,local_timezone = datetime.now().astimezone().tzname()
        ,is_in_notebook = is_in_notebook
        )

    return context