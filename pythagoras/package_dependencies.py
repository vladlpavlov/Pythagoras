""" PckgDependencies class that stores Python environment requirements.

PckgDependencies is a dict-like object: it groups together required packages,
with package names as keys and related requirements as values.

The class serves two purposes: (1) to define/store dependency requirements
for cloudized functions, and (2) to make it easy to write / read / change
lists of package requirements inside Python code in a Python-native style.

The class allows to define requirements in a variety of ways:

my_reqs = PckgDependencies(pandas=2.1, sklearn=1.3)

reqs_definition = '''
requests
numpy
pytorch~=1.0
'''

my_new_reqs = PckgDependencies(reqs_definition)

The class also allows to easily manipulate lists of requirements:

assert my_reqs != my_new_reqs
my_new_reqs += "tensorflow>=2.0"
my_new_reqs += my_reqs
del my_new_reqs["sklearn"]

Keys are always stored and returned in alphabetical order. This way
two equal groups of requirements always have the
same string representation and hash value.

Requirements are stored as packaging.requirements.Requirement objects.
For every requirement, the name of the package is always equal to its key:
pckg_dependencies_object[key].name == key
for every key in pckg_dependencies_object:PckgDependencies

This way, it is easy to check if a package is in the list of required ones:

if "pandas" in my_reqs:
    print("pandas is required")
"""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Dict, Any

from packaging.requirements import Requirement


class PckgDependencies(Mapping):
    _required_packages: Dict[str,Requirement]

    def __init__(self, *args, **kwargs):
        super().__init__()
        packages = {}

        for arg in args:
            if isinstance(arg, str):
                for s in arg.splitlines():
                    s = s.strip()
                    if not s:
                        continue
                    req = Requirement(s)
                    packages[req.name] = req
            elif isinstance(arg, PckgDependencies):
                packages.update(arg)
            elif isinstance(arg, dict):
                packages.update(PckgDependencies(**arg))
            elif isinstance(arg, list):
                packages.update(PckgDependencies(*arg))
            else:
                assert False, "Incorrect requirements definition"

        for name, req_candidate in kwargs.items():
            req = self._build_requirement(name, req_candidate)
            packages[name] = req

        self._required_packages = {p:packages[p] for p in sorted(packages)}

        for p, req in self._required_packages.items():
            assert p == req.name, "Inconsistent state detected"

            
    @staticmethod
    def _build_requirement(key:str, value:Any) -> Requirement:
        assert isinstance(key, str)
        if isinstance(value, Requirement):
            req = value
        else:
            try:
                req = Requirement(value)
                assert req.name == key, "Incorrect requirements definition"
            except:
                try:
                    req = Requirement(key + value)
                    assert req.name == key, "Incorrect requirements definition"
                except:
                    try:
                        req = Requirement(key + "==" + str(value))
                        assert req.name == key, "Incorrect requirements definition"
                    except:
                        raise
        return req

    def __getitem__(self, key):
        """ Return a package from the list of required packages."""
        return self._required_packages[key]


    def __setitem__(self, key, value):
        """ Add a package to the list of required packages."""
        packages = deepcopy(self._required_packages)
        packages[key] = self._build_requirement(key, value)
        self._required_packages = {p:packages[p] for p in sorted(packages)}


    def __delitem__(self, key):
        """ Remove a package from the list of required packages."""
        packages = deepcopy(self._required_packages)
        del packages[key]
        self._required_packages = {p:packages[p] for p in sorted(packages)}


    def __iter__(self):
        """ Return an iterator over the required packages."""
        return iter(self._required_packages)

    def __len__(self):
        """ Return the number of required packages."""
        return len(self._required_packages)


    def __contains__(self, key):
        """ Check if a package is in the list of required packages."""
        return key in self._required_packages


    def __str__(self):
        """ Return a string representation of the entire list of required packages."""
        str_repr = [str(self._required_packages[p])
            for p in self._required_packages]
        str_repr = "\n".join(str_repr)
        return str_repr


    def __eq__(self, other):
        """ Check if two lists of required packages are identical."""
        if not isinstance(other, PckgDependencies):
            return False
        if len(self) != len(other):
            return False
        for p in self:
            if p not in other:
                return False
            if str(self[p]) != str(other[p]):
                return False
        assert sorted(self) == sorted(other)
        return True


    def __add__(self, other):
        """ Merge two lists of required packages."""
        other = PckgDependencies(other)
        packages = deepcopy(self._required_packages)
        packages.update(other._required_packages)
        return PckgDependencies(packages)


    def __radd__(self, other):
        """ Merge two lists of required packages."""
        return self.__add__(other)