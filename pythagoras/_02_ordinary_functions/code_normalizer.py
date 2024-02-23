"""
This module provides functionality for normalizing function source codes.
Normalization consists of removing decorators, comments, docstrings,
and empty lines, and then formatting according to PEP 8 guidelines.

The module's primary function, `get_normalized_function_source`, takes a callable
as input and returns its source code in a 'canonical' form. The function only
works with regular functions, a method, a lambda function, or an async function
can not be passed as an argument to get_normalized_function_source.
The module also defines `FunctionSourceNormalizationError`, a custom
exception for errors specific to function normalization.

External libraries `ast`, and `autopep8` are used for
parsing and formatting. Internal utilities from `pythagoras` are also utilized.
"""
import re
import ast
import inspect
from typing import Callable, Union
import autopep8

from pythagoras import get_function_name_from_source
from pythagoras._00_basic_utils import get_long_infoname
from pythagoras._01_foundational_objects import PythagorasException
from pythagoras._02_ordinary_functions import assert_ordinarity


class FunctionSourceNormalizationError(PythagorasException):
    """Custom class for exceptions in this module."""
    pass



def get_normalized_function_source(
        a_func:Callable|str
        , drop_pth_decorators:bool = False
        ) -> str:
    """Return function's source code in a 'canonical' form.

    Remove all comments, docstrings and empty lines;
    standardize code formatting based on PEP 8.
    If drop_pth_decorators == True, remove Pythogaras decorators.

    Only regular functions are supported; methods and lambdas are not supported.
    """
    a_func_name, code = None, ""
    if callable(a_func):
        assert_ordinarity(a_func)
        a_func_name = get_long_infoname(a_func)
        code = inspect.getsource(a_func)
    elif isinstance(a_func, str):
        code = a_func
    else:
        assert callable(a_func) or isinstance(a_func, str)

    code_lines = code.splitlines()

    code_no_empty_lines = []
    for line in code_lines:
        if set(line)<=set(" \t"):
            continue
        code_no_empty_lines.append(line)

    # Fix indent for functions that are defined within other functions;
    # most frequently it is used for tests.
    first_line_no_indent = code_no_empty_lines[0].lstrip()
    n_chars_to_remove = len(code_no_empty_lines[0]) - len(first_line_no_indent)
    chars_to_remove = code_no_empty_lines[0][:n_chars_to_remove]
    code_clean_version = []
    for line in code_no_empty_lines:
        assert line.startswith(chars_to_remove)
        cleaned_line = line[n_chars_to_remove:]
        code_clean_version.append(cleaned_line)

    code_clean_version = "\n".join(code_clean_version)
    if a_func_name is None:
        a_func_name = get_function_name_from_source(code_clean_version)
    code_ast = ast.parse(code_clean_version)

    assert isinstance(code_ast, ast.Module)
    assert isinstance(code_ast.body[0], ast.FunctionDef),(
        f"{type(code_ast.body[0])=}"
    )
    #TODO: add support for multiple decorators
    decorator_list = code_ast.body[0].decorator_list
    if len(decorator_list) > 1:
        raise FunctionSourceNormalizationError(
            f"Function {a_func_name} can't have multiple decorators,"
            + " only one decorator is allowed.")
    if drop_pth_decorators and len(decorator_list):
        assert decorator_list[0].func.id in {
            "autonomous", "idempotent", "strictly_autonomous"}
        code_ast.body[0].decorator_list = []

    # Remove docstrings.
    for node in ast.walk(code_ast):
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


    result = ast.unparse(code_ast)
    result = autopep8.fix_code(result)

    lines, line_num = result.splitlines(), 0
    while lines[line_num].startswith("@"):
        line_num+=1

    if not lines[line_num].startswith("def "):
        raise FunctionSourceNormalizationError(
            f"Function {a_func_name} must be a regular functions ")

    return result