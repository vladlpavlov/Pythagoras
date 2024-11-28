from __future__ import annotations

import os
from typing import Optional
import pandas as pd

from persidict import PersiDict, FileDirDict
from .exceptions import NotAllowedError

def _persistent(param, val) -> pd.DataFrame:
  d = dict(
      type="Disk"
      ,parameter = [param]
      ,value = [val])
  return pd.DataFrame(d)


def _runtime(param, val) -> pd.DataFrame:
  d = dict(
      type = "Runtime"
      ,parameter = [param]
      ,value = [val])
  return pd.DataFrame(d)



class BasicPortal:
    """A base class for portal objects that enable access to 'outside' world.

    In a Pythagoras-based application, a portal is the application's 'window'
    into the non-ephemeral world outside the current application execution
    session. It's a connector that enables a link between runtime-only
    ephemeral state and a persistent state that can be saved and loaded
    across multiple runs of the application, and across multiple computers.

    A Pythagoras-based application can have multiple portals,
    and there is usually a current (default) portal, accessible via
    get_current_portal().

    BasicPortal is a base class for all portal objects. It provides foundational
    functionality for managing the portal stack and for accessing the current
    portal. The class is not intended to be used directly. Instead, it should
    be subclassed to provide additional functionality.
    """
    all_portals: dict = {}
    portals_stack: list = []
    counters_stack: list = []
    base_dir: str | None
    dict_type:type | None

    def __init__(self, base_dir:str|None = None, dict_type:type = FileDirDict):
        """Initialize the portal object"""

        if base_dir is None:
            base_dir = self.default_base_dir
        assert not os.path.isfile(base_dir)
        if not os.path.isdir(base_dir):
            os.mkdir(base_dir)
        assert os.path.isdir(base_dir)
        base_dir = os.path.abspath(base_dir)
        self.base_dir = base_dir

        assert issubclass(dict_type, PersiDict)
        assert dict_type == FileDirDict, (
            "Currently only FileDirDict is supported as a storage_type.")
        self.dict_type = dict_type

        BasicPortal.all_portals[id(self)] = self

    def get_params(self) -> dict:
        """Get the portal's configuration parameters"""
        return dict(base_dir=self.base_dir
                    , dict_type=self.dict_type)

    def describe(self) -> pd.DataFrame:
        """Get a DataFrame describing the portal's current state"""
        all_params = []

        all_params.append(_persistent(
            "Base directory", self.base_dir))
        all_params.append(_persistent(
            "Backend type", self.dict_type.__name__))

        result = pd.concat(all_params)
        result.reset_index(drop=True, inplace=True)

        return result

    @property
    def default_base_dir(self) -> str:
        """Get the default base directory for the portal"""
        # TODO: Implement a better way to determine the default base directory
        return "Q-Q-Q"

    def __enter__(self):
        """Set the portal as the current one"""
        if (len(BasicPortal.portals_stack) == 0 or
                id(BasicPortal.portals_stack[-1]) != id(self)):
            BasicPortal.portals_stack.append(self)
            BasicPortal.counters_stack.append(1)
        else:
            BasicPortal.counters_stack[-1] += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Remove the portal from the current context"""
        assert BasicPortal.portals_stack[-1] == self, (
            "Inconsistent state of the portal stack. "
            + "Most probably, portal.__enter__() method was called explicitly "
            + "within a 'with' statement with another portal.")
        if BasicPortal.counters_stack[-1] == 1:
            BasicPortal.portals_stack.pop()
            BasicPortal.counters_stack.pop()
        else:
            BasicPortal.counters_stack[-1] -= 1

    @staticmethod
    def __exit_all__() -> None:
        while len(BasicPortal.portals_stack) > 0:
            portal = BasicPortal.portals_stack[-1]
            portal.__exit__(None, None, None)

    @staticmethod
    def _current_portal(
            expected_class:Optional[type]=None
            ) -> BasicPortal | None:
        """Get the current (default) portal object"""
        if len(BasicPortal.portals_stack) > 0:
            result =  BasicPortal.portals_stack[-1]
            if expected_class is not None:
                assert issubclass(expected_class, BasicPortal)
                assert isinstance(result, expected_class)
            return result
        else:
            return None

    @classmethod
    def get_current_portal(cls) -> BasicPortal | None:
        """Get the current (default) portal object"""
        portal = BasicPortal._current_portal(expected_class=cls)
        return portal

    @classmethod
    def get_portal(cls, suggested_portal:Optional[BasicPortal]=None
               ) -> BasicPortal:
        """Get the portal object from the parameter or the default one"""
        if suggested_portal is None:
           suggested_portal = cls.get_current_portal()
        assert suggested_portal is not None, (
            "No portal was found in the current context. ")
        assert isinstance(suggested_portal, cls)
        return suggested_portal


    @staticmethod
    def _noncurrent_portals(expected_class:Optional[type]=None) -> list[BasicPortal]:
        """Get all portals except the current one"""
        current_portal = BasicPortal._current_portal()
        all_portals = BasicPortal.all_portals

        if current_portal is None:
            result = [all_portals[portal_id] for portal_id in all_portals]
        else:
            current_portal_id = id(current_portal)
            result = [all_portals[portal_id] for portal_id in all_portals
                    if portal_id != current_portal_id]

        if expected_class is not None:
            assert issubclass(expected_class, BasicPortal)
            assert all(isinstance(portal, expected_class) for portal in result)

        return result

    @classmethod
    def get_noncurrent_portals(cls) -> list[BasicPortal]:
        """Get all portals except the current one"""
        return BasicPortal._noncurrent_portals(expected_class=cls)


    @staticmethod
    def _active_portals(expected_class:Optional[type]=None) -> list[BasicPortal]:
        """Get all active portals"""
        active_portals = {}
        for portal in reversed(BasicPortal.portals_stack):
            active_portals[id(portal)] = portal
        result = list(active_portals.values())
        if len(result) and expected_class is not None:
            assert issubclass(expected_class, BasicPortal)
            assert all(isinstance(portal, expected_class) for portal in result)
        return result

    @classmethod
    def get_active_portals(cls) -> list[BasicPortal]:
        """Get all active portals"""
        return BasicPortal._active_portals(expected_class=cls)

    def _clear(self) -> None:
        """Clear the portal's state"""
        pass

    @classmethod
    def _clear_all(cls) -> None:
        """Remove all information about all the portals from the system."""
        for portal in BasicPortal.all_portals.values():
            portal._clear()
        BasicPortal.all_portals = dict()
        BasicPortal.portals_stack = list()
        BasicPortal.counters_stack = list()

    def __getstate__(self):
        raise NotAllowedError("Portal objects cannot be pickled.")

    def __setstate__(self, state):
        raise NotAllowedError("Portal objects cannot be pickled.")