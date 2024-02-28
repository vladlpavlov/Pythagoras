from pythagoras import is_unitialized, is_correctly_initialized
import pythagoras as pth

def summary():
    """ Get summary of Pythagoras' current state ."""

    if is_unitialized():
        return "Pythagoras is not initialized."
    if not is_correctly_initialized():
        return "Pythagoras is not correctly initialized."

    divider = 40 * "=" + "\n"
    result = divider
    result += "PERSISTENT STATE: \n"
    result += f"{len(pth.value_store)=} \n"
    result += f"{len(pth.function_output_store)=} \n"

    result += divider
    result += "CURRENT SESSION: \n"
    result += f"{len(pth.all_autonomous_functions)=} \n"
    result += f"{[island for island in pth.all_autonomous_functions]=} \n"
    default_island = None
    result += f"{len(default_island:=pth.all_autonomous_functions[pth.default_island_name])=} \n"
    result += f"{[func for func in default_island]=} \n"

    return result

