from __future__ import annotations

import os

from typing import Optional

import pandas as pd
from persidict import FileDirDict


from pythagoras._010_basic_portals.foundation import BasicPortal, _persistent, _runtime
from pythagoras._020_logging_portals.logging_portals import LoggingPortal
from pythagoras._800_persidict_extensions.first_entry_dict import FirstEntryDict


class DataPortal(LoggingPortal):
    """A portal that persistently stores values.

    Values are accessible via their hash_address-es,
    which are unique identifiers of the values.

    If the current portal does not contain a specific value,
    referenced by a hash_address, but this value can be retrieved
    from another portal, the value will be automatically copied
    to the current portal.

    A portal can serve as a context manager, enabling the use of the
    'with' statement to support portal-aware code blocks. If some code is
    supposed to explicitly read anything from a portal, it should be wrapped
    in a 'with' statement that marks the portal as the current.
    """

    value_store: FirstEntryDict|None
    _p_consistency_checks: float|None

    def __init__(self
            , base_dir:str | None = None
            , dict_type:type = FileDirDict
            , p_consistency_checks: float | None = None
            ):
        super().__init__(base_dir=base_dir, dict_type=dict_type)
        assert p_consistency_checks is None or 0 <= p_consistency_checks <= 1
        if p_consistency_checks is None:
            p_consistency_checks = 0
        self._p_consistency_checks = p_consistency_checks
        value_store_dir = os.path.join(base_dir, "value_store")
        value_store = dict_type(
            dir_name = value_store_dir
            , digest_len=0
            , immutable_items=True)
        value_store = FirstEntryDict(value_store, p_consistency_checks)
        self.value_store = value_store

    def get_params(self) -> dict:
        """Get the portal's configuration parameters"""
        params = super().get_params()
        params["p_consistency_checks"] = self.p_consistency_checks
        return params

    def describe(self) -> pd.DataFrame:
        """Get a DataFrame describing the portal's current state"""
        all_params = [super().describe()]

        all_params.append(_persistent(
            "Values, total"
            , len(self.value_store)))
        all_params.append(_runtime(
            "Probability of checks"
            , self._p_consistency_checks))

        result = pd.concat(all_params)
        result.reset_index(drop=True, inplace=True)
        return result


    @property
    def p_consistency_checks(self) -> float|None:
        return self._p_consistency_checks

    @classmethod
    def get_portal(cls, suggested_portal: Optional[DataPortal] = None
                   ) -> DataPortal:
        return BasicPortal.get_portal(suggested_portal)

    @classmethod
    def get_current_portal(cls) -> DataPortal | None:
        """Get the current (default) portal object"""
        return BasicPortal._current_portal(expected_class=cls)

    @classmethod
    def get_noncurrent_portals(cls) -> list[DataPortal]:
        return BasicPortal._noncurrent_portals(expected_class=cls)

    @classmethod
    def get_active_portals(cls) -> list[DataPortal]:
        return BasicPortal._active_portals(expected_class=cls)

    def _clear(self) -> None:
        """Clear the portal's state"""
        self.value_store = None
        self._p_consistency_checks = 1
        super()._clear()
