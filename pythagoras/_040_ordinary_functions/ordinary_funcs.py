from __future__ import annotations

import sys
from typing import Callable, Any

from pythagoras import LoggingPortal
from pythagoras._820_strings_signatures_converters.hash_signatures import get_hash_signature
from pythagoras._020_logging_portals.logging_portals import NeedsRandomization
from pythagoras._040_ordinary_functions.function_name import (
    get_function_name_from_source)
from pythagoras._040_ordinary_functions.code_normalizer_implementation import (
    __get_normalized_function_source__)

import pythagoras as pth


class OrdinaryFn:
    """A wrapper around an ordinary function that allows calling it.

    An ordinary function is a regular function. Async functions,
    class/object method, closures, and lambda functions
    are not considered ordinary.

    An ordinary function can only be called with keyword arguments.
    It can't be called with positional arguments.

    An OrdinaryFn object stores the source code of the function
    in a normalized form: without comments, docstrings, type annotations,
    and empty lines. The source code is formatted according to PEP 8.
    This way, Pythagoras can later compare the source
    code of two functions to check if they are equivalent.
    """
    fn_source_code:str
    fn_name:str
    _fn_fully_registered:bool
    _fn_bytecode:Any
    _fn_hash_id:str
    _fn_file_name:str
    _kwargs_var_name:str
    _result_var_name:str
    _tmp_fn_name:str

    def __init__(self, a_func: Callable | str | OrdinaryFn, **_):
        self._fn_fully_registered = False
        if isinstance(a_func, OrdinaryFn):
            self.update(a_func)
        else:
            assert callable(a_func) or isinstance(a_func, str)
            self.fn_source_code = __get_normalized_function_source__(
                a_func, drop_pth_decorators=True)
            self.fn_name = get_function_name_from_source(self.fn_source_code)

    def update(self, other: OrdinaryFn) -> None:
        self.fn_source_code = other.fn_source_code
        self.fn_name = other.fn_name
        if other._fn_fully_registered:
            self._fn_bytecode = other._fn_bytecode
            self._fn_hash_id = other._fn_hash_id
            self._fn_file_name = other._fn_file_name
            self._kwargs_var_name = other._kwargs_var_name
            self._result_var_name = other._result_var_name
            self._tmp_fn_name = other._tmp_fn_name
            self._fn_fully_registered = True


    @classmethod
    def _compile(cls,*args, **kwargs) -> Any:
        return compile(*args, **kwargs)

    def _complete_fn_registration(self) -> None:
        if self._fn_fully_registered:
            return

        source_to_exec = self.fn_source_code
        fn_hash_id = get_hash_signature(source_to_exec)
        self._fn_hash_id = fn_hash_id
        fn_file_name = self.fn_name+ "_"+fn_hash_id+".py"
        self._fn_file_name = fn_file_name
        self._kwargs_var_name = "kwargs_"+self.fn_name+fn_hash_id
        self._result_var_name = "result"+self.fn_name+fn_hash_id
        self._tmp_fn_name = "tmp_func_"+self.fn_name+fn_hash_id
        source_to_exec = source_to_exec.replace(
            " " + self.fn_name + "(", " " + self._tmp_fn_name + "(", 1)
        source_to_exec += f"\n\n{self._result_var_name} = "
        source_to_exec += f"{self._tmp_fn_name}(**{self._kwargs_var_name})"
        self._fn_bytecode = self._compile(
            source_to_exec, fn_file_name, "exec")
        if type(self) == OrdinaryFn:
            self._fn_fully_registered = True

    def __call__(self,* args, **kwargs) -> Any:
        assert len(args) == 0, (f"Function {self.fn_name} can't"
            + " be called with positional arguments,"
            + " only keyword arguments are allowed.")
        return self.execute(**kwargs)


    def _available_names(self):
        """Returns a dictionary with the names, available inside the function."""
        names= dict(globals())
        names[self.fn_name] = self
        names["self"] = self
        names["pth"] = pth
        return names

    def _exception_prefixes(self) -> list[list[str]]:
        return [[f"{self.fn_name}_ORD"]
            ] + LoggingPortal._exception_prefixes()

    def _exception_id(self, exc_value) -> str:
        return NeedsRandomization(
            LoggingPortal._exception_id(exc_value)
            + f"_{self.fn_name}")

    def _extra_exception_data(self) -> dict:
        result = dict(
            function_name = self.fn_name
            ,decorator = self.decorator.replace("\t",4*" ").split("\n")
            ,source_code = self.fn_source_code.replace("\t",4*" ").split("\n")
            ,virtual_file_name = self._fn_file_name
            ,avaialble_names = list(self._available_names())
            )
        result |= LoggingPortal._extra_exception_data()
        return result

    def _persist_exception_information(self
           , exc_value, exc_type, trace_back
           , exception_id, exception_prefixes
           , exception_extra_data_to_persist) -> dict|None:
        return LoggingPortal._persist_exception_information(
            exc_value=exc_value
            , exc_type=exc_type
            , trace_back=trace_back
            , exception_id=exception_id
            , exception_prefixes=exception_prefixes
            , exception_extra_data_to_persist=exception_extra_data_to_persist)

    def execute(self,**kwargs):
        try:
            self._complete_fn_registration()
            names_dict = self._available_names()
            names_dict[self._kwargs_var_name] = kwargs
            exec(self._fn_bytecode, names_dict, names_dict)
            result = names_dict[self._result_var_name]
            return result
        except:
            exc_type, exc_value, trace_back = sys.exc_info()
            exception_id = self._exception_id(exc_value)
            exception_prefixes = self._exception_prefixes()
            extra_data = self._extra_exception_data()
            extra_data["kwargs"] = kwargs # TODO: refactor to support large objects
            self._persist_exception_information(
                exc_value=exc_value
                , exc_type=exc_type
                , trace_back=trace_back
                , exception_id=exception_id
                , exception_prefixes=exception_prefixes
                , exception_extra_data_to_persist=extra_data)
            raise


    @property
    def decorator(self):
        return "@pth.ordinary()"

    def __getstate__(self):
        raise NotImplementedError("OrdinaryFn objects are not pickable.")

    def __setstate__(self, state):
        raise NotImplementedError("OrdinaryFn objects are not pickable.")