""" Foundational classes amd functions.

This module contains classes and functions to
work with hash signatures and addresses.

A hash signature is a unique identifier for an immutable value.

Pythagoras heavily relies on class HashAddr to store and retrieve data.
Two objects with exactly the same type and value will always have
exactly the same HashAddr-es.

A HashAddr consists of 2 strings: a prefix, and a hash.
A prefix contains human-readable information about an object's type.
A hash string contains the object's hash signature.
"""

from pythagoras._01_foundational_objects.hash_addresses import (
    HashAddr)

from pythagoras._01_foundational_objects.value_addresses import (
    ValueAddr)

from pythagoras._01_foundational_objects.multipersidict import (
    MultiPersiDict)
