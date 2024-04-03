# from pythagoras._07_mission_control.global_state_management import (
#   is_fully_unitialized, is_correctly_initialized)
import pythagoras as pth
import pandas as pd

def persistent(param, val) -> pd.DataFrame:
  d = dict(
      parameter = [param]
      ,value = [val]
      ,type = "persistent")
  return pd.DataFrame(d)


def runtime(param, val) -> pd.DataFrame:
  d = dict(
      parameter = [param]
      ,value = [val]
      ,type = "runtime")
  return pd.DataFrame(d)

def summary(include_current_session:bool = True, print_result:bool = False):
    """ Get summary of Pythagoras' current state ."""

    # if is_fully_unitialized():
    #     return "Pythagoras is not initialized."
    # if not is_correctly_initialized():
    #     return "Pythagoras is not correctly initialized."

    all_params = []

    all_params.append(persistent(
        "Base directory", pth.base_dir))
    all_params.append(persistent(
        "Total # of values stored", len(pth.value_store)))
    all_params.append(persistent(
        "Total # of function execution results cached"
        ,len(pth.execution_results)))
    all_params.append(persistent(
        "Total # of exceptions recorded", len(pth.crash_history)))
    all_params.append(persistent(
        "Total # of events recorded", len(pth.event_log)))
    all_params.append(persistent(
        "Execution queue size", len(pth.execution_requests)))
    all_params.append(persistent(
        "# of currently active nodes", len(pth.compute_nodes.pkl)))


    result = pd.concat(all_params)
    result.set_index("parameter", inplace=True)
    result.index.name = None


    #
    # if include_current_session:
    #
    #     result += 21*"~" +  " CURRENT SESSION: " + 21*"~" + "\n"
    #     result += f"{len(pth.all_autonomous_functions)=} \n"
    #     result += f"{[island for island in pth.all_autonomous_functions]=} \n"
    #     result += f"{pth.default_island_name=} \n"
    #     default_island = pth.all_autonomous_functions[pth.default_island_name]
    #     result += f"{len(default_island)=} \n"
    #     result += f"{[func for func in default_island]=} \n"
    #
    # result += 60*"~" + "\n\n"

    if print_result:
        print(result)

    return result

