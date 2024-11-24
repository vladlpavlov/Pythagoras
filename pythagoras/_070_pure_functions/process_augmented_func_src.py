import ast
from copy import deepcopy

from pythagoras._030_data_portals.data_portals import DataPortal
from pythagoras._070_pure_functions.astkeywords_dict_convertors import (
    convert_astkeywords_to_dict)

import pythagoras as pth


NO_PORTAL = "NO PORTAL"

def process_augmented_func_src(
        input_src: str
        , portal: DataPortal|None = None
        ) -> None:
    """ Process all functions from the augmented function source code.

    This function takes a string input_src, containing the source code of
    one or more autonomous and/or idempotent functions.
    It processes each function in the source code by parsing it and
    applying the appropriate decorator to the function. This results in
    registering all the functions in the portal.

    This function is intended to be used only by PureFn.__setstate__() to
    simultaneously "bring to life" the full list of inter-dependent functions
    belonging to the same island.
    """
    assert isinstance(input_src,str), (
        "The input_src parameter must be a string with the source code of"
        + " one or more autonomous and/or idempotent functions.")

    assert isinstance(portal, DataPortal) or portal is None

    portal = DataPortal.get_portal(portal)

    tree = ast.parse(input_src)
    for node in tree.body:
        assert isinstance(node, ast.FunctionDef), (
            "The augmented function code can only consist of"
            " function definitions.")

        assert len(node.decorator_list)==1 , ("Each of the functions"
            + " inside augmented function code must have"
            + " exactly one decorator.")

        decorator = node.decorator_list[0]
        assert decorator.func.attr in pth.primary_decorators, (
            "The only allowed decorators are: "
            + ", ".join(["@pth." + d +"()" for d in pth.primary_decorators]))

        func_no_decorators = deepcopy(node)
        func_no_decorators.decorator_list = []
        decorator_name = decorator.func.attr
        decorator_kwargs = convert_astkeywords_to_dict(decorator.keywords)
        assert "portal" not in decorator_kwargs
        if portal is not NO_PORTAL:
            decorator_kwargs["portal"] = portal

        func_src = ast.unparse(func_no_decorators) # TODO: add ast passthrough
        pth.primary_decorators[decorator_name](**decorator_kwargs)(func_src)