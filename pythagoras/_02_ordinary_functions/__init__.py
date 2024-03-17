"""Decorators and utilities to work with ordinary functions.

An 'ordinary' function is just a regular Python function that accepts
only named (keyword) arguments.

Lambda functions, class methods, asynchronous functions and closures
are not ordinary functions.

Ordinary functions are not allowed to have decorators, except for ones that
are part of Pythagoras (e.g. @autonomous or @idempotent).

Pythagoras transforms source code of ordinary functions into a normalised
form: a string that represents the function's source code, with all
decorators, docstrings, and comments removed, and the resulting code
formatted according to PEP8. This way, Pythagoras can later compare the source
code of two functions to check if they are equivalent.
"""

from pythagoras._02_ordinary_functions.ordinary_funcs import (
    OrdinaryFn)

from pythagoras._02_ordinary_functions.ordinary_decorator import (
    ordinary)