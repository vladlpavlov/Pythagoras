import pandas as pd
from pandas import describe_option

from pythagoras import SwarmingPortal, BasicPortal, DefaultLocalPortal


def initialize(base_dir) -> pd.DataFrame: #TODO: refactor
    BasicPortal._clear_all()
    portal = SwarmingPortal(base_dir=base_dir, n_background_workers=3)
    portal.__enter__()
    return portal.describe()

def connect_to_portal(base_dir) -> pd.DataFrame:
    portal = SwarmingPortal(base_dir=base_dir, n_background_workers=3)
    return portal.describe()

def connect_to_default_portal() -> pd.DataFrame:
    portal = DefaultLocalPortal()
    return portal.describe()

def describe() -> pd.DataFrame:
    if len(BasicPortal.all_portals) == 1:
        return list(BasicPortal.all_portals.values())[0].describe()

    all_descriptions = []
    for i,portal in enumerate(BasicPortal.all_portals.values()):
        description = portal.describe()
        description.insert(0, "portal", i)
        all_descriptions.append(description)
    return pd.concat(all_descriptions, ignore_index=True)

