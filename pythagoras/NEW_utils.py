import ast
import inspect
from typing import Any, Callable

import astor
import autopep8
from persidict import replace_unsafe_chars


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
        name = replace_unsafe_chars(name, replace_with="_")

    return name


def get_normalized_function_source(a_func:Callable) -> str:
    """Return function's source code in a 'canonical' form.

    Remove all decorators, comments, docstrings and empty lines;
    standardize code formatting based on PEP 8.
    """

    assert callable(a_func)

    code = inspect.getsource(a_func)
    code_lines = code.split("\n")

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
    code_ast = ast.parse(code_clean_version)

    assert isinstance(code_ast, ast.Module)
    assert isinstance(code_ast.body[0], ast.FunctionDef)
    #TODO: add support for multiple decorators
    assert len(code_ast.body[0].decorator_list) <= 1, (
        "Currently supported functions can't have multiple decorators")
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

    # Convert back from AST to text and format it according to PEP 8.
    if hasattr(ast,"unparse"):
        result = ast.unparse(code_ast)
    else: # ast.unparse() is only available starting from Python 3.9
        result = astor.to_source(code_ast)
    result = autopep8.fix_code(result)

    return result
