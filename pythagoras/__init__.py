"""Pythagoras aims to democratize access to distributed serverless compute.

We make it simple and inexpensive to create, deploy and run planet-scale
massively parallel algorithms from within local Python scripts and notebooks.
Pythagoras makes data scientists' lives easier, while allowing them to
solve more complex problems in a shorter time with smaller budgets.
"""
from typing import Optional, Callable, Dict
from persidict import PersiDict

from pythagoras.utils import *
from pythagoras.foundational_objects import *
from pythagoras.function_decorators import *

value_store:Optional[PersiDict] = None
crash_history: Optional[PersiDict] = None
cloudized_functions:Optional[Dict[str,Callable]] = None
island_name: Optional[str] = None
initialization_parameters: Optional[dict] = None


