import pandas as pd

from pythagoras import SwarmingPortal, BasicPortal, DefaultLocalPortal


def initialize(base_dir) -> pd.DataFrame: #TODO: refactor
    BasicPortal._clear_all()
    portal = SwarmingPortal(base_dir=base_dir, n_background_workers=3)
    portal.__enter__()
    return portal.describe()

def connect_to_portal(base_dir) -> pd.DataFrame:
    portal = SwarmingPortal(base_dir=base_dir, n_background_workers=3)
    return portal.describe()

def connect_to_default_local_portal() -> pd.DataFrame:
    portal = DefaultLocalPortal()
    return portal.describe()

def describe() -> pd.DataFrame: #TODO: refactor
    return BasicPortal.entered_portals_stack[-1].describe()