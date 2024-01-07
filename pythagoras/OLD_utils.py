"""Miscellaneous supporting classes and functions."""

from __future__ import annotations

import ast
import astor
from abc import ABCMeta
import datetime
import math
import os
import platform
import socket
from getpass import getuser
import inspect
from inspect import FrameInfo, isclass
import numbers, time
from random import Random
from typing import Any, Dict, Callable, TypeVar, Type, Optional, Tuple
import pkg_resources
import psutil
import gc
import string
from ast import Module, FunctionDef


def get_safe_chars():
    """ Get set of URL/filename-safe characters.

     A set of characters allowed in Persistent Dict keys,
     filenames / S3 object names, and hash addresses.
     """
    chars = set(string.ascii_letters + string.digits + "()_-~.=")
    return chars


def replace_unsafe_chars(a_str:str, replace_with:str) -> str :
    """ Replace unsafe (special) characters with allowed (safe) ones."""
    safe_chars = get_safe_chars()
    result_list = [(c if c in safe_chars else replace_with) for c in a_str]
    result_str = "".join(result_list)
    return result_str


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


    assert isclass(class_to_detect)
    assert isinstance(name_to_detect, str)
    assert len(name_to_detect)

    for frame_record in inspect.stack():
        if name_to_detect not in frame_record.frame.f_locals:
            continue
        candidate = frame_record.frame.f_locals[name_to_detect]
        if isinstance(candidate, class_to_detect):
            return candidate

    return None

class ABC_PostInitializable(ABCMeta):
    """ Metaclass that enables __post__init__() method for abstract classes. """
    def __call__(cls, *args, **kwargs):
        obj = ABCMeta.__call__(cls, *args, **kwargs)
        obj.__post__init__(*args, **kwargs)
        return obj


def buid_context(file_path:str=None, time_zone=None)-> Dict:
    """Capture core information about execution environment.

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


def get_long_infoname(x:Any, drop_unsafe_chars:bool = True) -> str:
    """Build a string with extended information about an object and its type"""

    name = str(type(x).__module__)

    if hasattr(type(x), "__qualname__"):
        name += "." + str(type(x).__qualname__)
    else:
        name += "." + str(type(x).__name__)

    if hasattr(x, "__qualname__"):
        name += "_" + str(x.__qualname__)
    elif hasattr(x, "__name__"):
        name += "_" + str(x.__name__)

    if drop_unsafe_chars:
        name = replace_unsafe_chars(name, "_")

    return name


class NeatStr:
    """Nice short human-readable str depictions of popular numeric values.

    Insignificant details are dropped:
    - exact # of seconds is not shown if we are talking about hours,
    - exact # of bytes is dropped if we are talking about gigabytes, etc.
    """

    @staticmethod
    def mem_size(size_in_B:int, div_ch:str = ' ') -> str:
        """Convert an integer number of bytes into a string like '7 Mb' """

        assert isinstance(size_in_B, numbers.Number)
        assert size_in_B >= 0

        size_in_K = size_in_B / 1024
        if size_in_K < 1: return (str(math.ceil(size_in_B))) + div_ch + "B"

        size_in_M = size_in_K / 1024
        if size_in_M < 1: return (str(math.ceil(size_in_K))) + div_ch + "Kb"

        size_in_G = size_in_M / 1024
        if size_in_G < 1: return (str(math.ceil(size_in_M))) + div_ch + "Mb"

        size_in_T = size_in_G / 1024
        if size_in_T < 1: return (str(math.ceil(size_in_G))) + div_ch + "Gb"

        size_in_P = size_in_T / 1024
        if size_in_P < 1: return (str(math.ceil(size_in_T))) + div_ch + "Tb"

        return (str(math.ceil(size_in_P))) + div_ch + "Pb"

    @staticmethod
    def time_diff(time_in_seconds: float, div_ch: str = ' ') -> str:
        """Convert a float number of seconds into a string like '5 hours' """

        t = time_in_seconds
        t_str = ""

        h = t / (60 * 60)
        if h >= 1:
            t_str += str(math.floor(h)) + div_ch + "hours" + div_ch
            t = t - h * (60 * 60)

        m = t / 60
        if m >= 1:
            t_str += str(math.floor(m)) + div_ch + "minutes" + div_ch
            t = t - m * 60

        if h < 1:
            if m > 1:
                t_str += str(math.ceil(t))
            elif t >= 10:
                t_str += f"{t:.1f}"
            elif t >= 1:
                t_str += f"{t:.2f}"
            else:
                t_str += f"{t:.3g}"

            t_str += div_ch + "seconds" + div_ch

        t_str = t_str.rstrip(div_ch)
        return t_str

    @staticmethod
    def object_names(
            an_object: Any
            , div_ch: str = '.'
            , stacks_to_skip:int = 0) -> str:
        """ Find the name(s) of variable(s) that are aliases for an_object.

        The function uses a naive but fast approach,
        it does not always find all the names
        """
        all_names = []

        for f in reversed(inspect.stack()[stacks_to_skip+1:]):
            local_vars = f.frame.f_locals
            names = [name for name in local_vars if
                     local_vars[name] is an_object]
            if "self" in names:
                names.remove("self")
            all_names += names

        all_names = list(dict.fromkeys(all_names))  # dedup but keep the order

        return div_ch.join(all_names)

    @staticmethod
    def object_info(
            an_object: Any
            , div_ch: str = '.'
            , stacks_to_skip: int = 0) -> str:
        """ Create a string with debug information about an object"""

        names_str = NeatStr.object_names(
            an_object, div_ch=" / ",stacks_to_skip = stacks_to_skip+1)

        if names_str.count("/"):
            text_info = "An object with names < " + names_str + " >"
        elif len(names_str):
            text_info = "An object with name < " + names_str + " >"
        else:
            text_info = "An anonymous object"

        text_info += " has type < "
        if hasattr(type(an_object),"__qualname__"):
            text_info += type(an_object).__qualname__
        else:
            text_info += type(an_object).__name__
        text_info += " > and repr_value < "
        text_info += repr(an_object)
        text_info += " >"

        text_info = text_info.replace("  ", " ")
        text_info = text_info.replace("< <", "< ")
        text_info = text_info.replace("> >", " >")

        return text_info

def free_RAM(print_info:bool=True, collect_garbage:bool=True) -> int:
    """ Force garbage collection and return/print size of fee memory. """

    if collect_garbage:
        gc.collect()

    free_memory = psutil.virtual_memory().free

    if print_info:
        print(f"Free memory: {NeatStr.mem_size(free_memory)} ")

    return free_memory


def get_normalized_function_source(a_func:Callable) -> str:
    """Return function's source code in a 'canonical' form.

    Remove all decorators, comments, docstrings and empty lines;
    standardize code formatting.
    """

    assert callable(a_func)

    code = inspect.getsource(a_func)
    code_lines = code.split("\n")

    code_no_empty_lines = []
    for line in code_lines:
        if set(line)<=set(" \t"):
            continue
        code_no_empty_lines.append(line)

    first_line_no_indent = code_no_empty_lines[0].lstrip()
    n_chars_to_remove = len(code_no_empty_lines[0]) - len(first_line_no_indent)
    chars_to_remove = code_no_empty_lines[0][:n_chars_to_remove]

    code_clean_version = []
    for line in code_no_empty_lines:
        assert line.startswith(chars_to_remove)
        cleaned_line = line[n_chars_to_remove:]
        code_clean_version.append(cleaned_line)

    code_clean_version = "\n".join(code_clean_version)
    code_ast = ast.parse(code_clean_version)

    assert isinstance(code_ast, Module)
    assert isinstance(code_ast.body[0], FunctionDef)
    #TODO: add support for multiple decorators
    assert len(code_ast.body[0].decorator_list) <= 1, (
        "Currently cloudized functions can not have multiple decorators")
    code_ast.body[0].decorator_list = []

    for node in ast.walk(code_ast): #remove docstrings
        if not isinstance(node
                , (ast.FunctionDef, ast.ClassDef
                   , ast.AsyncFunctionDef, ast.Module)):
            continue
        if not len(node.body):
            continue
        if not isinstance(node.body[0], ast.Expr):
            continue
        if not hasattr(node.body[0], 'value'):
            continue
        if not isinstance(node.body[0].value, ast.Str):
            continue

        node.body = node.body[1:]
        if len(node.body) < 1:
            node.body.append(ast.Pass())
        # TODO: compare with the source for ast.candidate_docstring()

    if hasattr(ast,"unparse"):
        result = ast.unparse(code_ast)
    else: # ast.unparse() is only available starting from Python 3.9
        result = astor.to_source(code_ast)

    return result


def uuid8andhalf():
    """ Generate UUID ver. 8 1/2

    A human-readable unique ID that can guarantee
    uniqueness across space and time, and contains textual information
    that helps to debug distributed applications.

    Version 8 1/2 is a reference to Federico Fellini's movie
    and is not supposed to make sense.
    """
    self = uuid8andhalf

    if not hasattr(self,"counter"):
        self.counter = 0
    else:
        self.counter += 1
        if self.counter >= 1_000_000_000_000:
            self.counter = 1

    if not hasattr(self, "randomizer"):
        self.randomizer = Random()

    random_int = self.randomizer.randint(1, 1_000_000_000_000)

    new_uuid = f"user-{getuser()}"
    new_uuid += f"-pid-{os.getpid()}"
    new_uuid += f"-time-{time.time()}"
    new_uuid += f"-host-{socket.gethostname()}"
    new_uuid += f"-platform-{platform.platform()}"
    new_uuid += f"-counter-{self.counter}"
    new_uuid += f"-random-{random_int}"

    return new_uuid
