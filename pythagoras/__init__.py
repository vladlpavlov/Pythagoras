"""Pythagoras aims to democratize access to distributed serverless compute.

We make it simple and inexpensive to create, deploy and run
massively parallel algorithms from within local Python scripts and notebooks.
Pythagoras makes data scientists' lives easier, while allowing them to
solve more complex problems in a shorter time with smaller budgets.
"""
from typing import Optional, Dict
from random import Random
from persidict import PersiDict

from pythagoras._99_misc_utils import *
from pythagoras._01_foundational_objects import *
from pythagoras._02_ordinary_functions import *
from pythagoras._03_autonomous_functions import *
from pythagoras._04_idempotent_functions import *
from pythagoras._05_events_and_exceptions import *
from pythagoras._06_swarming import *
from pythagoras._07_mission_control import *


base_dir:Optional[str] = None

value_store:Optional[PersiDict] = None
execution_results:Optional[PersiDict] = None
execution_requests:Optional[PersiDict] = None

crash_history: Optional[PersiDict] = None
event_log: Optional[PersiDict] = None

run_history:Optional[MultiPersiDict] = None
compute_nodes:Optional[MultiPersiDict] = None

runtime_id: Optional[str] = None
all_autonomous_functions:Optional[Dict[str|None,Dict[str,AutonomousFn]]] = None
default_island_name: Optional[str] = None
entropy_infuser: Optional[Random] = None
n_background_workers: Optional[int] = None
initialization_parameters: Optional[dict] = None

primary_decorators = {d.__name__:d for d in [
    idempotent, autonomous, strictly_autonomous]}
all_decorators = {d.__name__:d for d in [
    idempotent, autonomous, strictly_autonomous, ordinary]}


