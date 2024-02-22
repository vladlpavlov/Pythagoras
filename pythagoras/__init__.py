"""Pythagoras aims to democratize access to distributed serverless compute.

We make it simple and inexpensive to create, deploy and run planet-scale
massively parallel algorithms from within local Python scripts and notebooks.
Pythagoras makes data scientists' lives easier, while allowing them to
solve more complex problems in a shorter time with smaller budgets.
"""
from typing import Optional, Callable, Dict
from random import Random
from persidict import PersiDict

from pythagoras._00_basic_utils import *
from pythagoras._01_foundational_objects import *
from pythagoras._02_ordinary_functions import *
from pythagoras._03_autonomous_functions import *
from pythagoras._04_idempotent_functions import *
from pythagoras._05_mission_control import *

from pythagoras.python_utils import *

value_store:Optional[PersiDict] = None
function_garage:Optional[PersiDict] = None # ????
function_source_repository:Optional[PersiDict] = None
function_output_store:Optional[PersiDict] = None
crash_history: Optional[PersiDict] = None
swarming_requests: Optional[PersiDict] = None
cloudized_functions:Optional[Dict[str,Dict[str,IdempotentFunction]]] = None
default_island_name: Optional[str] = None
entropy_infuser: Optional[Random] = None
initialization_parameters: Optional[dict] = None


