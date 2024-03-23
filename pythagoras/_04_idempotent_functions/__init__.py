"""Decorators and utilities to work with idempotent functions.

An idempotent function is an autonomous function that
always returns the same result if it is called multiple times
with the same arguments. Idempotent functions are allowed to have
side effects, but the side effects must be exactly the same regardless of
how many times the function was executed.

This module defines a decorator which is used to inform Pythagoras that
a function is intended to be idempotent: @idempotent().

Pythagoras persistently caches the results of an idempotent function, so that
if the function is called multiple times with the same arguments,
the function is executed only once, and the cached result is returned
for all the subsequent executions.

While caching the results of an idempotent function, Pythagoras also tracks
changes in the source code of the function. If the source code of an idempotent
function changes, the function is executed again on the next call.
However, the previously cached results are still available
for the old version of the function.

An idempotent function must be autonomous. Pythagoras tracks source code changes
for the idempotent function as well other autonomous functions it is using,
provided they belong to the same island. Pythagoras does not track source code
changes for functions from other islands, even if they are used
by the idempotent function. Pythagoras also does not track any other
source code changes (e.g. changes in the imported packages).

Pythagoas also provides infrastructure for remote execution of
idempotent functions in distributed environments. Pythagoras employs
an asynchronous execution model called 'swarming':
you do not know when your function will be executed,
what machine will execute it, and how many times it will be executed.
Pythagoras ensures that the function will be eventually executed
at least once, but does not offer any further guarantees.
"""

from pythagoras._04_idempotent_functions.kw_args import (
    SortedKwArgs, PackedKwArgs, UnpackedKwArgs)

from pythagoras._04_idempotent_functions.idempotent_func_address_context import (
    IdempotentFn
    , IdempotentFnExecutionResultAddr
    , IdempotentFnExecutionContext)

from pythagoras._04_idempotent_functions.idempotent_decorator import (
    idempotent)

from pythagoras._04_idempotent_functions.idempotency_checks import (
    is_idempotent)

