import pythagoras as pth
import pandas as pd

from pythagoras import is_idempotent, is_autonomous, is_executed_in_notebook


def islands():
    """ Get summary of currently know autonomous functions."""

    all_functions = []

    for island_name, island in pth.all_autonomous_functions.items():
        for func_name, func in island.items():
            d = dict(
                island = [island_name]
                ,function = func.fn_source_code
                , type = func.fn_type)

            all_functions.append(pd.DataFrame(d))

    if len(all_functions):
        result = pd.concat(all_functions)
        result.reset_index(drop=True, inplace=True)
        if is_executed_in_notebook():
            return result.style.set_properties(
                **{'white-space': 'pre-wrap', 'text-align': 'left'})
        else:
            return result
    else:
        return "No functions registered so far."
