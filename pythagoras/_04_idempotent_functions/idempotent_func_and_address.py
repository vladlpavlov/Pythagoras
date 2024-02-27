from __future__ import annotations

from typing import Callable, Optional, Any

import pythagoras as pth

from pythagoras._03_autonomous_functions.autonomous_funcs import (
    AutonomousFunction, register_autonomous_function)

from pythagoras._02_ordinary_functions.ordinary_funcs import (
    OrdinaryFunction)

from pythagoras._03_autonomous_functions.default_island_singleton import (
    DefaultIslandType, DefaultIsland)

from pythagoras._04_idempotent_functions.kw_args import UnpackedKwArgs
from pythagoras._04_idempotent_functions.process_augmented_func_src import (
    process_augmented_func_src)

class IdempotentFunction(AutonomousFunction):
    augmented_code_checked: bool
    def __init__(self, a_func: Callable | str | OrdinaryFunction
            , island_name:str | None | DefaultIslandType = DefaultIsland):
        super().__init__(a_func, island_name)
        self.augmented_code_checked = False
        register_idempotent_function(self)

    @property
    def decorator(self) -> str:
        decorator_str = "@pth.idempotent("
        decorator_str += f"island_name='{self.island_name}'"
        decorator_str += ")"
        return decorator_str

    def runtime_checks(self):
        super().runtime_checks()
        island_name = self.island_name
        island = pth.all_autonomous_functions[island_name]

        if not self.augmented_code_checked:
            augmented_code = ""
            for f_name in self.dependencies:
                f = island[f_name]
                augmented_code += f.decorator + "\n"
                augmented_code += f.naked_source_code + "\n"
                augmented_code += "\n"

            name = self.name
            if (not hasattr(island[name], "_augmented_source_code")
                or island[name]._augmented_source_code is None):
                island[name]._augmented_source_code = augmented_code
            else:
                assert island[name]._augmented_source_code == augmented_code

            self.augmented_code_checked = True

        return True


    @property
    def augmented_source_code(self) -> str:
        island_name = self.island_name
        island = pth.all_autonomous_functions[island_name]
        assert hasattr(island[self.name], "_augmented_source_code")
        assert island[self.name]._augmented_source_code is not None
        assert self.augmented_code_checked
        return island[self.name]._augmented_source_code


    def __getstate__(self):
        assert self.runtime_checks()
        draft_state = dict(name=self.name
            , naked_source_code=self.naked_source_code
            , island_name=self.island_name
            , augmented_source_code=self.augmented_source_code
            , class_name=self.__class__.__name__)
        state = dict()
        for key in sorted(draft_state):
            state[key] = draft_state[key]
        return state

    def __setstate__(self, state):
        assert len(state) == 5
        assert state["class_name"] == IdempotentFunction.__name__
        self.name = state["name"]
        self.naked_source_code = state["naked_source_code"]
        self.island_name = state["island_name"]
        self.augmented_code_checked = False
        register_idempotent_function(self)

        island_name = self.island_name
        island = pth.all_autonomous_functions[island_name]
        name = self.name
        if island[name]._augmented_source_code is None:
            island[name]._augmented_source_code = state["augmented_source_code"]
            process_augmented_func_src(state["augmented_source_code"])
        else:
            assert state["augmented_source_code"] == (
                island[name]._augmented_source_code)

        self.augmented_code_checked = True


def register_idempotent_function(f: IdempotentFunction) -> None:
    """Register an idempotent function in the Pythagoras system."""
    assert isinstance(f, IdempotentFunction)
    register_autonomous_function(f)
    island_name = f.island_name
    island = pth.all_autonomous_functions[island_name]
    name = f.name
    if not hasattr(island[name], "_augmented_source_code"):
        island[name]._augmented_source_code = None

