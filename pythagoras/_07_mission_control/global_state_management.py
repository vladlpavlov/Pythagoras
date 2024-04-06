import os, random, sys, atexit

import pandas as pd
from persidict import FileDirDict, PersiDict

from pythagoras._01_foundational_objects.hash_and_random_signatures import (
    get_node_signature, get_random_signature)
from pythagoras._01_foundational_objects.multipersidict import MultiPersiDict
from pythagoras._05_events_and_exceptions.execution_environment_summary import (
    build_execution_environment_summary)
from pythagoras._05_events_and_exceptions.uncaught_exception_handlers import (
    register_exception_handlers, unregister_exception_handlers, pth_excepthook)
from pythagoras._05_events_and_exceptions.notebook_checker import (
    is_executed_in_notebook)
from pythagoras._07_mission_control.summary import summary

import pythagoras as pth


def _force_initialize(*args, **kwargs):
    _clean_global_state()
    return initialize(*args, **kwargs)

def initialize(base_dir:str
               , n_background_workers:int = 3
               , cloud_type:str = "local"
               , default_island_name:str = "Samos"
               , runtime_id: str|None = None
               , return_summary_dataframe:bool = True):
    """ Initialize Pythagoras.
    """
    assert pth.is_fully_unitialized(), (
        "You can only initialize pythagoras once.")

    cloud_type = cloud_type.lower()

    assert cloud_type in {"local","aws"}

    if cloud_type == "local":
        dict_type = FileDirDict
    else:
        assert False, "AWS support not yet implemented"

    n_background_workers = int(n_background_workers)
    assert n_background_workers >= 0
    pth.n_background_workers = n_background_workers

    pth.entropy_infuser = random.Random()

    assert not os.path.isfile(base_dir)
    if not os.path.isdir(base_dir):
        os.mkdir(base_dir)
    assert os.path.isdir(base_dir)

    pth.base_dir = os.path.abspath(base_dir)

    value_store_dir = os.path.join(base_dir, "value_store")
    pth.value_store = dict_type(
        value_store_dir, digest_len=0, immutable_items=True)

    compute_nodes_dir = os.path.join(base_dir, "compute_nodes")
    pth.compute_nodes = MultiPersiDict(
        dict_type = dict_type
        , dir_name = compute_nodes_dir
        , pkl = dict(digest_len=0, immutable_items=False)
        , json = dict(digest_len=0, immutable_items=False)
        )

    if runtime_id is None:
        node_id = get_node_signature()
        runtime_id = get_random_signature()
        pth.runtime_id = runtime_id
        pth.compute_nodes.pkl[node_id, "runtime_id"]= runtime_id
        atexit.register(clean_runtime_id)
        summary = build_execution_environment_summary()
        pth.compute_nodes.json[node_id, "execution_environment"] = summary
    else:
        pth.runtime_id = runtime_id

    crash_history_dir = os.path.join(base_dir, "crash_history")
    pth.crash_history = dict_type(
        crash_history_dir, digest_len=0
        , file_type="json", immutable_items=True)

    event_log_dir = os.path.join(base_dir, "event_log")
    pth.event_log = dict_type(
        event_log_dir, digest_len=0
        , file_type="json", immutable_items=True)

    func_output_store_dir = os.path.join(
        base_dir, "execution_results")
    pth.execution_results = dict_type(
        func_output_store_dir, digest_len=0
        , immutable_items=True)

    run_history_dir = os.path.join(
        base_dir, "run_history")
    pth.run_history = MultiPersiDict(
        dict_type = dict_type
        , dir_name = run_history_dir
        , json = dict(digest_len=0, immutable_items=True)
        , py = dict(
            base_class_for_values=str
            , digest_len=0
            , immutable_items=False)
        , txt = dict(
            base_class_for_values=str
            , digest_len=0
            , immutable_items=True)
        , pkl = dict(
            digest_len=0
            , immutable_items=True)
    )

    execution_requests_dir = os.path.join(
        base_dir, "execution_requests")
    pth.execution_requests = dict_type(
        execution_requests_dir, digest_len=0
        , immutable_items=False)

    pth.default_island_name = default_island_name
    pth.all_autonomous_functions = dict()
    pth.all_autonomous_functions[default_island_name] = dict()

    parameters = dict(base_dir=base_dir
        ,cloud_type=cloud_type
        ,n_background_workers=n_background_workers
        ,default_island_name=default_island_name
        , runtime_id=pth.runtime_id)

    pth.initialization_parameters = parameters

    register_exception_handlers()

    for n in range(n_background_workers):
        pth.launch_background_worker()

    if return_summary_dataframe:
        return PythagorasContextWithSummary()
    else:
        return PythagorasContext()


def is_fully_unitialized():
    """ Check if Pythagoras is uninitialized."""
    result = True
    result &= pth.value_store is None
    result &= pth.execution_results is None
    result &= pth.execution_requests is None
    result &= pth.run_history is None
    result &= pth.crash_history is None
    result &= pth.event_log is None
    result &= pth.default_island_name is None
    result &= pth.all_autonomous_functions is None
    result &= pth.initialization_parameters is None
    result &= pth.entropy_infuser is None
    result &= pth.n_background_workers is None
    result &= pth.runtime_id is None
    result &= pth.compute_nodes is None
    return result

def is_correctly_initialized():
    """ Check if Pythagoras is correctly initialized."""
    if not isinstance(pth.value_store, PersiDict):
        return False
    if not isinstance(pth.run_history, MultiPersiDict):
        return False
    if not isinstance(pth.execution_results, PersiDict):
        return False
    if not isinstance(pth.execution_requests, PersiDict):
        return False
    if not isinstance(pth.crash_history, PersiDict):
        return False
    if not isinstance(pth.event_log, PersiDict):
        return False
    if not isinstance(pth.compute_nodes, MultiPersiDict):
        return False
    if not isinstance(pth.default_island_name, str):
        return False
    if not isinstance(pth.all_autonomous_functions, dict):
        return False
    if not isinstance(pth.entropy_infuser, random.Random):
        return False
    if not isinstance(pth.n_background_workers, int):
        return False
    if not isinstance(pth.runtime_id, str):
        return False
    if len(pth.all_autonomous_functions) > 0: # TODO: rework later
        for island_name in pth.all_autonomous_functions:
            if not isinstance(island_name, str):
                return False
            if not isinstance(pth.all_autonomous_functions[island_name], dict):
                return False
            for function_name in pth.all_autonomous_functions[island_name]:
                if not isinstance(function_name, str):
                    return False
                if not isinstance(
                        pth.all_autonomous_functions[island_name][function_name]
                        ,pth.AutonomousFn):
                    return False
    if not isinstance(pth.initialization_parameters, dict):
        return False
    for param in pth.initialization_parameters:
        if not isinstance(param, str):
            return False
    if not (pth.initialization_parameters["default_island_name"]
               == pth.default_island_name):
        return False
    if not is_executed_in_notebook():
        if sys.excepthook != pth_excepthook:
            return False
    return True

def is_global_state_correct():
    """ Check if Pythagoras is in a correct state."""
    result = is_fully_unitialized() or is_correctly_initialized()
    return result

def clean_runtime_id():
    """ Clean runtime id."""
    try:
        node_id = get_node_signature()
        address = [node_id, "runtime_id"]
        pth.compute_nodes.pkl.delete_if_exists(address)
    except:
        pass

def _clean_global_state():
    clean_runtime_id()
    pth.value_store = None
    pth.execution_results = None
    pth.execution_requests = None
    pth.run_history = None
    pth.crash_history = None
    pth.event_log = None
    pth.compute_nodes = None
    pth.all_autonomous_functions = None
    pth.default_island_name = None
    pth.initialization_parameters = None
    pth.entropy_infuser = None
    pth.n_background_workers = None
    pth.runtime_id = None
    unregister_exception_handlers()
    assert pth.is_fully_unitialized()
    assert pth.is_global_state_correct()


class PythagorasContext:
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        _clean_global_state()

class PythagorasContextWithSummary(pd.DataFrame):

    def __init__(self):
        super().__init__(summary())

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        _clean_global_state()

    # def __str__(self):
    #     return summary(include_current_session=False)
    #
    # def __repr__(self):
    #     return summary(include_current_session=False)


def get_all_island_names() -> set[str]:
    """ Get all islands."""
    return set(pth.all_autonomous_functions.keys())

def get_all_autonomous_function_names(
        island_name:str | None = None):
    """ Get all autonomous functions."""
    if island_name is None:
        island_name = pth.default_island_name
    return list(pth.all_autonomous_functions[island_name].keys())

def get_island(island_name:str | None = None):
    if island_name is None:
        island_name = pth.default_island_name
    return pth.all_autonomous_functions[island_name]

def get_autonomous_function(function_name:str
    , island_name:str | None = None):
    """ Get cloudized function."""
    if island_name is None:
        island_name = pth.default_island_name
    return pth.all_autonomous_functions[island_name][function_name]