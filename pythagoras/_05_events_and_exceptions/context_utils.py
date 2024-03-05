import psutil
import os
import platform
import socket
from typing import Dict
from getpass import getuser
from datetime import datetime
import torch
from pythagoras._05_events_and_exceptions.notebook_checker import is_executed_in_notebook

def build_context()-> Dict:
    """Capture core information about execution environment.

    The function is intended to be used to log environment information
    to help debug (distributed) applications.
    """
    cwd = os.getcwd()

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
        ,cuda_gpu_count=torch.cuda.device_count()
        ,disk_usage = psutil.disk_usage(cwd)
        ,virtual_memory = psutil.virtual_memory()
        ,working_directory = cwd
        ,local_timezone = datetime.now().astimezone().tzname()
        ,is_in_notebook = is_executed_in_notebook()
        )

    return context


def add_context(**kwargs):
    context_param_name = "context"
    while context_param_name in kwargs:
        context_param_name += "_"
    kwargs[context_param_name] = build_context()
    return kwargs