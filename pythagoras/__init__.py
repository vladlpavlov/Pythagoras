"""Pythagoras aims to democratize access to distributed serverless compute.

We make it simple and inexpensive to create, deploy and run
massively parallel algorithms from within local Python scripts and notebooks.
Pythagoras makes data scientists' lives easier, while allowing them to
solve more complex problems in a shorter time with smaller budgets.
"""
from typing import Optional, Dict
from random import Random
from persidict import PersiDict

from pythagoras._800_persidict_extensions import *
from pythagoras._810_output_manipulators import *
from pythagoras._820_strings_signatures_converters import *

from pythagoras._010_basic_portals import *
from pythagoras._010_basic_portals import _PortalTester
from pythagoras._020_logging_portals import *
from pythagoras._030_data_portals import *
from pythagoras._040_ordinary_functions import *
from pythagoras._050_safe_functions import *
from pythagoras._060_autonomous_functions import *
from pythagoras._070_pure_functions import *
from pythagoras._080_compatibility_validators import *
from pythagoras._090_swarming_portals import *
from pythagoras._100_top_level_API import *



# default_portal:Optional[AutonomousCodePortal] = None ## CodeAndDataPortal
#
# base_dir:Optional[str] = None ## DataPortal
#
# value_store:Optional[PersiDict] = None ## DataPortaportall
# execution_results:Optional[PersiDict] = None ## CodeAndDataPortal
# execution_requests:Optional[PersiDict] = None ## CodeAndDataPortal
#
# crash_history: Optional[PersiDict] = None ## CodeAndDataPortal
# event_log: Optional[PersiDict] = None ## CodeAndDataPortal
#
# run_history:Optional[OverlappingMultiDict] = None ## CodeAndDataPortal
# compute_nodes:Optional[OverlappingMultiDict] = None ## CodeAndDataPortal
#
# runtime_id: Optional[str] = None
# all_autonomous_functions:Optional[Dict[str|None,Dict[str,AutonomousFn]]] = None
# default_island_name: Optional[str] = None ## CodeAndDataPortal
# entropy_infuser: Optional[Random] = None ## DataPortal
# n_background_workers: Optional[int] = None ## CodeAndDataPortal
# initialization_parameters: Optional[dict] = None

primary_decorators = {d.__name__:d for d in [
    autonomous
    , strictly_autonomous
    , pure
    ]}
all_decorators = {d.__name__:d for d in [
    ordinary
    , autonomous
    , strictly_autonomous
    , pure
]}


