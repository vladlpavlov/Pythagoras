import pandas as pd

from pythagoras import SwarmingPortal, BasicPortal


def initialize(base_dir) -> pd.DataFrame: #TODO: refactor
    portal = SwarmingPortal(base_dir=base_dir, n_background_workers=3)
    portal.__enter__()
    return portal.describe()

def describe() -> pd.DataFrame: #TODO: refactor
    return BasicPortal().portals_stack[-1].describe()