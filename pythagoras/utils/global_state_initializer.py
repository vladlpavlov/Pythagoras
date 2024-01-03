import os
from persidict import FileDirDict, PersiDict
import pythagoras as pth
def initialize(cloud_type:str, base_dir:str, island_name:str) -> None:
    """ Initialize Pythagoras.
    """
    assert cloud_type in {"local","aws"}

    if cloud_type == "local":
        dict_type = FileDirDict
    else:
        assert False, "AWS not yet implemented"

    assert not os.path.isfile(base_dir)
    if not os.path.isdir(base_dir):
        os.mkdir(base_dir)
    assert os.path.isdir(base_dir)

    assert pth.value_store is None, ( #TODO? add more of these ?!?
        "You can only initialize pythagoras once.")
    value_store_dir = os.path.join(base_dir, "value_store")
    pth.value_store = dict_type(value_store_dir, digest_len=0)
    crash_history_dir = os.path.join(base_dir, "crash_history")
    pth.crash_history = dict_type(crash_history_dir, digest_len=0)
    pth.island_name = island_name
    pth.cloudized_functions = dict()

    parameters = dict(cloud_type=cloud_type
        , base_dir=base_dir, island_name=island_name)

    pth.initialization_parameters = parameters


def is_unitialized():
    """ Check if Pythagoras is uninitialized."""
    result = True
    result &= pth.value_store is None
    result &= pth.crash_history is None
    result &= pth.island_name is None
    result &= pth.cloudized_functions is None
    result &= pth.initialization_parameters is None
    return result

def is_correctly_initialized():
    """ Check if Pythagoras is correctly initialized."""
    result = True
    result &= isinstance(pth.value_store, PersiDict)
    result &= isinstance(pth.crash_history, PersiDict)
    result &= isinstance(pth.island_name, str)
    result &= isinstance(pth.cloudized_functions, dict)
    if len(pth.cloudized_functions) > 0: # TODO: rework later
        for f_name in pth.cloudized_functions:
            result &= isinstance(f_name, str)
            result &= callable(f_name)
    result &= isinstance(pth.initialization_parameters, dict)
    result &= (pth.initialization_parameters["island_name"] == pth.island_name)
    return result

def is_global_state_correct():
    """ Check if Pythagoras is in a correct state."""
    result = is_unitialized() or is_correctly_initialized()
    return result

def _clean_global_state():
    pth.value_store = None
    pth.crash_history = None
    pth.cloudized_functions = None
    pth.island_name = None
    pth.initialization_parameters = None
    assert pth.is_global_state_correct()
    assert pth.is_unitialized()

