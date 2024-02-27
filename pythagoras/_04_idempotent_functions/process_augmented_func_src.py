import ast
from copy import deepcopy
from pythagoras._03_autonomous_functions.autonomous_decorators import (
    autonomous, strictly_autonomous)
from pythagoras._04_idempotent_functions.astkeywords_dict_convertors import (
    convert_astkeywords_to_dict)
from pythagoras._04_idempotent_functions.idempotent_decorator import (
    idempotent)

allowed_decorators = {d.__name__:d for d in [
    idempotent, autonomous, strictly_autonomous]}

def process_augmented_func_src(input_src):
    """
    Process the augmented function source code.

    :param augmented_func_src: The augmented function source code.
    :return: The processed augmented function source code.
    """
    tree = ast.parse(input_src)
    for node in tree.body:
        assert isinstance(node, ast.FunctionDef), (
            "The augmented function code can only consist of"
            " function definitions.")

        assert len(node.decorator_list)==1 , ("Each of the functions"
            + " inside augmented function code must have"
            + " exactly one decorator.")

        decorator = node.decorator_list[0]
        assert decorator.func.attr in allowed_decorators, (
            "The only allowed decorators are: "
            + ", ".join(["@pth."+ad+"()" for ad in allowed_decorators]))

        func_no_decorators = deepcopy(node)
        func_no_decorators.decorator_list = []
        decorator_name = decorator.func.attr
        decorator_kwargs = convert_astkeywords_to_dict(decorator.keywords)
        func_src = ast.unparse(func_no_decorators) # TODO: add ast passthrough
        allowed_decorators[decorator_name](**decorator_kwargs)(func_src)



