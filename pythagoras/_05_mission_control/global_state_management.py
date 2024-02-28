import os
import random


from persidict import FileDirDict, PersiDict
import pythagoras as pth
from pythagoras._03_autonomous_functions.default_island_singleton import (
    DefaultIslandType, DefaultIsland)


def initialize(base_dir:str
               , cloud_type:str = "local"
               , default_island_name:str = "Samos") -> None:
    """ Initialize Pythagoras.
    """
    assert pth.is_unitialized(), "You can only initialize pythagoras once."

    cloud_type = cloud_type.lower()

    assert cloud_type in {"local","aws"}

    if cloud_type == "local":
        dict_type = FileDirDict
    else:
        assert False, "AWS support not yet implemented"

    pth.entropy_infuser = random.Random()

    assert not os.path.isfile(base_dir)
    if not os.path.isdir(base_dir):
        os.mkdir(base_dir)
    assert os.path.isdir(base_dir)

    value_store_dir = os.path.join(base_dir, "value_store")
    pth.value_store = dict_type(value_store_dir, digest_len=0)
    func_garage_dir = os.path.join(base_dir, "func_garage")
    pth.function_garage = dict_type(func_garage_dir, digest_len=0)
    pth.function_source_repository = dict_type(
        func_garage_dir, digest_len=0, file_type="py",base_class_for_values=str)
    # crash_history_dir = os.path.join(base_dir, "crash_history")
    # pth.crash_history = dict_type(crash_history_dir
    #     , digest_len=0, file_type="json")
    func_output_store_dir = os.path.join(base_dir, "func_output_store")
    pth.function_output_store = dict_type(func_output_store_dir, digest_len=0)
    swarming_requests_dir = os.path.join(base_dir, "swarming_requests")
    pth.swarming_requests = dict_type(swarming_requests_dir, digest_len=0)
    pth.default_island_name = default_island_name
    pth.all_autonomous_functions = dict()
    pth.all_autonomous_functions[default_island_name] = dict()
    pth.all_autonomous_functions[None] = dict()

    parameters = dict(cloud_type=cloud_type
        , base_dir=base_dir, default_island_name=default_island_name)

    pth.initialization_parameters = parameters


def is_unitialized():
    """ Check if Pythagoras is uninitialized."""
    result = True
    result &= pth.value_store is None
    result &= pth.function_garage is None
    result &= pth.function_source_repository is None
    result &= pth.function_output_store is None
    # result &= pth.crash_history is None
    result &= pth.default_island_name is None
    result &= pth.all_autonomous_functions is None
    result &= pth.initialization_parameters is None
    result &= pth.entropy_infuser is None
    return result

def is_correctly_initialized():
    """ Check if Pythagoras is correctly initialized."""
    if not isinstance(pth.value_store, PersiDict):
        return False
    if not isinstance(pth.function_garage, PersiDict):
        return False
    if not isinstance(pth.function_source_repository, PersiDict):
        return False
    if not isinstance(pth.function_output_store, PersiDict):
        return False
    # if not isinstance(pth.crash_history, PersiDict):
    #     return False
    if not isinstance(pth.default_island_name, str):
        return False
    if not isinstance(pth.all_autonomous_functions, dict):
        return False
    if not isinstance(pth.entropy_infuser, random.Random):
        return False
    if len(pth.all_autonomous_functions) > 0: # TODO: rework later
        for island_name in pth.all_autonomous_functions:
            if not isinstance(island_name, (str, type(None))):
                return False
            if not isinstance(pth.all_autonomous_functions[island_name], dict):
                return False
            for function_name in pth.all_autonomous_functions[island_name]:
                if not isinstance(function_name, str):
                    return False
                if not isinstance(
                        pth.all_autonomous_functions[island_name][function_name]
                        ,pth.AutonomousFunction):
                    return False
    if not isinstance(pth.initialization_parameters, dict):
        return False
    for param in pth.initialization_parameters:
        if not isinstance(param, str):
            return False
    if not (pth.initialization_parameters["default_island_name"]
               == pth.default_island_name):
        return False
    return True

def is_global_state_correct():
    """ Check if Pythagoras is in a correct state."""
    result = is_unitialized() or is_correctly_initialized()
    return result

def _clean_global_state():
    pth.value_store = None
    pth.function_garage = None #???
    pth.function_source_repository = None
    pth.function_output_store = None
    # pth.crash_history = None
    pth.all_autonomous_functions = None
    pth.default_island_name = None
    pth.initialization_parameters = None
    pth.entropy_infuser = None
    assert pth.is_unitialized()
    assert pth.is_global_state_correct()


def get_all_island_names() -> set[str]:
    """ Get all islands."""
    return set(pth.all_autonomous_functions.keys())

def get_all_autonomous_function_names(
        island_name:str | None | DefaultIslandType = DefaultIsland):
    """ Get all autonomous functions."""
    if island_name is DefaultIsland:
        island_name = pth.default_island_name
    return list(pth.all_autonomous_functions[island_name].keys())

def get_island(island_name:str | None | DefaultIslandType = DefaultIsland):
    if island_name is DefaultIsland:
        island_name = pth.default_island_name
    return pth.all_autonomous_functions[island_name]

def get_autonomous_function(function_name:str
    , island_name:str | None | DefaultIslandType = DefaultIsland):
    """ Get cloudized function."""
    if island_name is DefaultIsland:
        island_name = pth.default_island_name
    return pth.all_autonomous_functions[island_name][function_name]


# def register_idempotent_function(function:Callable):
#     # TODO: Redfactor. Maybe use pth.IdempotentFunction
#     assert isinstance_txt(function, "IdempotentFunction") # !!!
#     island_name = function.island_name
#     function_name = function.function_name
#     if island_name not in pth.idempotent_functions:
#         pth.idempotent_functions[island_name] = dict()
#     ## TODO: find better way to handle this vvvvvvvvv
#     assert function_name not in pth.idempotent_functions[island_name]
#     ## TODO: find better way to handle this ^^^^^^^^^
#     pth.idempotent_functions[island_name][function_name] = function
