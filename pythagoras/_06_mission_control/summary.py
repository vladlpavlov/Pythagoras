from pythagoras._06_mission_control.global_state_management import is_fully_unitialized, is_correctly_initialized
import pythagoras as pth

def summary():
    """ Get summary of Pythagoras' current state ."""

    if is_fully_unitialized():
        return "Pythagoras is not initialized."
    if not is_correctly_initialized():
        return "Pythagoras is not correctly initialized."

    divider = 60 * "~" + "\n"
    result = "\n\n"+divider
    result += "PERSISTENT STATE: \n"
    result += f"{len(pth.value_store)=} \n"
    result += f"{len(pth.execution_results)=} \n"

    result += divider
    result += "CURRENT SESSION: \n"
    result += f"{len(pth.all_autonomous_functions)=} \n"
    result += f"{[island for island in pth.all_autonomous_functions]=} \n"
    result += f"{pth.default_island_name=} \n"
    default_island = pth.all_autonomous_functions[pth.default_island_name]
    result += f"{len(default_island)=} \n"
    result += f"{[func for func in default_island]=} \n"

    result += divider + "\n\n"

    print(result)
    return result

