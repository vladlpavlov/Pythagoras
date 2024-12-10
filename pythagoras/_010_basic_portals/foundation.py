from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional
import pandas as pd
from parameterizable import ParameterizableClass

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



class BasicPortal(ParameterizableClass):
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
    entered_portals_stack: list = []
    entered_portals_counters_stack: list = []
    root_dict: PersiDict | None


    def __init__(self, root_dict:PersiDict|str|None = None):
        ParameterizableClass.__init__(self)
        if root_dict is None:
            root_dict = FileDirDict(base_dir = self.default_base_dir())
        elif not isinstance(root_dict, PersiDict):
            root_dict = FileDirDict(base_dir = str(root_dict))
        root_dict_params = root_dict.get_params()
        root_dict_params.update(digest_len=0)
        root_dict = type(root_dict)(**root_dict_params)
        self.root_dict = root_dict
        BasicPortal.all_portals[id(self)] = self

    def get_params(self) -> dict:
        """Get the portal's configuration parameters"""
        params = dict(root_dict=self.root_dict)
        return params

    def describe(self) -> pd.DataFrame:
        """Get a DataFrame describing the portal's current state"""
        all_params = []

        all_params.append(_persistent(
            "Base directory", self.root_dict.base_dir))
        all_params.append(_persistent(
            "Backend type", self.root_dict.__class__.__name__))

        result = pd.concat(all_params)
        result.reset_index(drop=True, inplace=True)

        return result


    @staticmethod
    def default_base_dir() -> str:
        """Get the base directory for the default local portal.

        The default base directory is ~/.pythagoras/.default_portal

        Pythagoras connects to the default local portal
        when no other portal is specified in the
        program which uses Pythagoras.
        """
        home_directory = Path.home()
        target_directory = home_directory / ".pythagoras" / ".default_portal"
        target_directory.mkdir(parents=True, exist_ok=True)
        target_directory_str = str(target_directory.resolve())
        return target_directory_str


    @staticmethod
    def get_most_recently_added_portal() -> BasicPortal|None:
        """Get the most recently added portal"""
        if len(BasicPortal.all_portals) == 0:
            return None
        last_key = next(reversed(BasicPortal.all_portals))
        return BasicPortal.all_portals[last_key]


    def __enter__(self):
        """Set the portal as the current one"""
        if (len(BasicPortal.entered_portals_stack) == 0 or
                id(BasicPortal.entered_portals_stack[-1]) != id(self)):
            BasicPortal.entered_portals_stack.append(self)
            BasicPortal.entered_portals_counters_stack.append(1)
        else:
            BasicPortal.entered_portals_counters_stack[-1] += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Remove the portal from the current context"""
        assert BasicPortal.entered_portals_stack[-1] == self, (
            "Inconsistent state of the portal stack. "
            + "Most probably, portal.__enter__() method was called explicitly "
            + "within a 'with' statement with another portal.")
        if BasicPortal.entered_portals_counters_stack[-1] == 1:
            BasicPortal.entered_portals_stack.pop()
            BasicPortal.entered_portals_counters_stack.pop()
        else:
            BasicPortal.entered_portals_counters_stack[-1] -= 1

    @staticmethod
    def __exit_all__() -> None:
        while len(BasicPortal.entered_portals_stack) > 0:
            portal = BasicPortal.entered_portals_stack[-1]
            portal.__exit__(None, None, None)

    @staticmethod
    def _most_recently_entered_portal(
            expected_class:Optional[type]=None
            ) -> BasicPortal | None:
        """Get the current (default) portal object"""
        if len(BasicPortal.entered_portals_stack) > 0:
            result =  BasicPortal.entered_portals_stack[-1]
            if expected_class is not None:
                assert issubclass(expected_class, BasicPortal)
                assert isinstance(result, expected_class)
            return result
        else:
            return None

    @classmethod
    def get_most_recently_entered_portal(cls) -> BasicPortal | None:
        """Get the currently used portal object"""
        portal = BasicPortal._most_recently_entered_portal(expected_class=cls)
        return portal

    @classmethod
    def get_best_portal_to_use(cls
            , suggested_portal:Optional[BasicPortal]=None
            ) -> BasicPortal:
        """Get the portal object from the parameter or find the best one"""
        if suggested_portal is None:
           suggested_portal = cls.get_most_recently_entered_portal()
        if suggested_portal is None:
            suggested_portal = cls.get_most_recently_added_portal()
        if suggested_portal is None:
            # Dirty hack to avoid circular imports
            suggested_portal = sys.modules["pythagoras"].DefaultLocalPortal()
        return suggested_portal


    @staticmethod
    def _noncurrent_portals(expected_class:Optional[type]=None) -> list[BasicPortal]:
        """Get all portals except the most recently entered one"""
        current_portal = BasicPortal._most_recently_entered_portal()
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
        """Get all portals except the most recently entered one"""
        return BasicPortal._noncurrent_portals(expected_class=cls)


    @staticmethod
    def _entered_portals(expected_class:Optional[type]=None) -> list[BasicPortal]:
        """Get all active portals"""
        entered_portals = {}
        for portal in reversed(BasicPortal.entered_portals_stack):
            entered_portals[id(portal)] = portal
        result = list(entered_portals.values())
        if len(result) and expected_class is not None:
            assert issubclass(expected_class, BasicPortal)
            assert all(isinstance(portal, expected_class) for portal in result)
        return result

    @classmethod
    def get_entered_portals(cls) -> list[BasicPortal]:
        """Get all active portals"""
        return BasicPortal._entered_portals(expected_class=cls)

    def _clear(self) -> None:
        """Clear the portal's state"""
        self.root_dict = None
        pass

    @classmethod
    def _clear_all(cls) -> None:
        """Remove all information about all the portals from the system."""
        for portal in BasicPortal.all_portals.values():
            portal._clear()
        BasicPortal.all_portals = dict()
        BasicPortal.entered_portals_stack = list()
        BasicPortal.entered_portals_counters_stack = list()

    def __getstate__(self):
        raise NotAllowedError("Portal objects cannot be pickled.")

    def __setstate__(self, state):
        raise NotAllowedError("Portal objects cannot be pickled.")