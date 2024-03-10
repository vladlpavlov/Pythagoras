# from pythagoras._07_mission_control.global_state_management import (
#   is_fully_unitialized, is_correctly_initialized)
import pythagoras as pth

def summary(include_current_session:bool = True, print_result:bool = False):
    """ Get summary of Pythagoras' current state ."""

    # if is_fully_unitialized():
    #     return "Pythagoras is not initialized."
    # if not is_correctly_initialized():
    #     return "Pythagoras is not correctly initialized."


    result = "\n"
    result += 20*"~" + " PERSISTENT STATE: " + 20*"~" + "\n"
    result += f"{pth.base_dir=} \n"
    result += f"{len(pth.value_store)=} \n"
    result += f"{len(pth.execution_results)=} \n"
    result += f"{len(pth.crash_history)=} \n"
    result += f"{len(pth.event_log)=} \n"
    result += f"{len(pth.execution_requests)=} \n"
    result += f"{len(pth.compute_nodes.pkl)=} \n"


    if include_current_session:

        result += 21*"~" +  " CURRENT SESSION: " + 21*"~" + "\n"
        result += f"{len(pth.all_autonomous_functions)=} \n"
        result += f"{[island for island in pth.all_autonomous_functions]=} \n"
        result += f"{pth.default_island_name=} \n"
        default_island = pth.all_autonomous_functions[pth.default_island_name]
        result += f"{len(default_island)=} \n"
        result += f"{[func for func in default_island]=} \n"

    result += 60*"~" + "\n\n"

    if print_result:
        print(result)

    return result

