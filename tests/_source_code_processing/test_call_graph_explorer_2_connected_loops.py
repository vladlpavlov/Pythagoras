from pythagoras._function_src_code_processing.call_graph_explorer import *

def a(*args
        , return_name:bool = False
        , return_shallow:bool=False
        , return_deep:bool=False)-> Set[str]:
    assert return_name + return_shallow + return_deep == 1
    nested_calls = [all_together]
    nested_calls = set(nested_calls)
    my_name = inspect.stack()[0].function
    result = {my_name}
    args = set(args)
    if return_name:
        return result
    elif return_shallow:
        result |= {f.__name__ for f in nested_calls}
        return result
    else: # return_deep == True
        if my_name in args:
            return args
        else:
            for f in nested_calls:
                result |= f(*args, my_name, return_deep=True)
            return result

def b(*args
        , return_name:bool = False
        , return_shallow:bool=False
        , return_deep:bool=False)-> Set[str]:
    assert return_name + return_shallow + return_deep == 1
    nested_calls = [a]
    nested_calls = set(nested_calls)
    my_name = inspect.stack()[0].function
    result = {my_name}
    args = set(args)
    if return_name:
        return result
    elif return_shallow:
        result |= {f.__name__ for f in nested_calls}
        return result
    else: # return_deep == True
        if my_name in args:
            return args
        else:
            for f in nested_calls:
                result |= f(*args, my_name, return_deep=True)
            return result


def c(*args
        , return_name:bool = False
        , return_shallow:bool=False
        , return_deep:bool=False)-> Set[str]:
    assert return_name + return_shallow + return_deep == 1
    nested_calls = [b]
    nested_calls = set(nested_calls)
    my_name = inspect.stack()[0].function
    result = {my_name}
    args = set(args)
    if return_name:
        return result
    elif return_shallow:
        result |= {f.__name__ for f in nested_calls}
        return result
    else: # return_deep == True
        if my_name in args:
            return args
        else:
            for f in nested_calls:
                result |= f(*args, my_name, return_deep=True)
            return result


def d(*args
        , return_name:bool = False
        , return_shallow:bool=False
        , return_deep:bool=False)-> Set[str]:
    assert return_name + return_shallow + return_deep == 1
    nested_calls = [c]
    nested_calls = set(nested_calls)
    my_name = inspect.stack()[0].function
    result = {my_name}
    args = set(args)
    if return_name:
        return result
    elif return_shallow:
        result |= {f.__name__ for f in nested_calls}
        return result
    else: # return_deep == True
        if my_name in args:
            return args
        else:
            for f in nested_calls:
                result |= f(*args, my_name, return_deep=True)
            return result


def e(*args
        , return_name:bool = False
        , return_shallow:bool=False
        , return_deep:bool=False)-> Set[str]:
    assert return_name + return_shallow + return_deep == 1
    nested_calls = [d]
    nested_calls = set(nested_calls)
    my_name = inspect.stack()[0].function
    result = {my_name}
    args = set(args)
    if return_name:
        return result
    elif return_shallow:
        result |= {f.__name__ for f in nested_calls}
        return result
    else: # return_deep == True
        if my_name in args:
            return args
        else:
            for f in nested_calls:
                result |= f(*args, my_name, return_deep=True)
            return result


def aa(*args
        , return_name:bool = False
        , return_shallow:bool=False
        , return_deep:bool=False)-> Set[str]:
    assert return_name + return_shallow + return_deep == 1
    nested_calls = [all_together]
    nested_calls = set(nested_calls)
    my_name = inspect.stack()[0].function
    result = {my_name}
    args = set(args)
    if return_name:
        return result
    elif return_shallow:
        result |= {f.__name__ for f in nested_calls}
        return result
    else: # return_deep == True
        if my_name in args:
            return args
        else:
            for f in nested_calls:
                result |= f(*args, my_name, return_deep=True)
            return result

def bb(*args
        , return_name:bool = False
        , return_shallow:bool=False
        , return_deep:bool=False)-> Set[str]:
    assert return_name + return_shallow + return_deep == 1
    nested_calls = [aa]
    nested_calls = set(nested_calls)
    my_name = inspect.stack()[0].function
    result = {my_name}
    args = set(args)
    if return_name:
        return result
    elif return_shallow:
        result |= {f.__name__ for f in nested_calls}
        return result
    else: # return_deep == True
        if my_name in args:
            return args
        else:
            for f in nested_calls:
                result |= f(*args, my_name, return_deep=True)
            return result


def cc(*args
        , return_name:bool = False
        , return_shallow:bool=False
        , return_deep:bool=False)-> Set[str]:
    assert return_name + return_shallow + return_deep == 1
    nested_calls = [bb]
    nested_calls = set(nested_calls)
    my_name = inspect.stack()[0].function
    result = {my_name}
    args = set(args)
    if return_name:
        return result
    elif return_shallow:
        result |= {f.__name__ for f in nested_calls}
        return result
    else: # return_deep == True
        if my_name in args:
            return args
        else:
            for f in nested_calls:
                result |= f(*args, my_name, return_deep=True)
            return result


def dd(*args
        , return_name:bool = False
        , return_shallow:bool=False
        , return_deep:bool=False)-> Set[str]:
    assert return_name + return_shallow + return_deep == 1
    nested_calls = [cc]
    nested_calls = set(nested_calls)
    my_name = inspect.stack()[0].function
    result = {my_name}
    args = set(args)
    if return_name:
        return result
    elif return_shallow:
        result |= {f.__name__ for f in nested_calls}
        return result
    else: # return_deep == True
        if my_name in args:
            return args
        else:
            for f in nested_calls:
                result |= f(*args, my_name, return_deep=True)
            return result


def ee(*args
        , return_name:bool = False
        , return_shallow:bool=False
        , return_deep:bool=False)-> Set[str]:
    assert return_name + return_shallow + return_deep == 1
    nested_calls = [dd]
    nested_calls = set(nested_calls)
    my_name = inspect.stack()[0].function
    result = {my_name}
    args = set(args)
    if return_name:
        return result
    elif return_shallow:
        result |= {f.__name__ for f in nested_calls}
        return result
    else: # return_deep == True
        if my_name in args:
            return args
        else:
            for f in nested_calls:
                result |= f(*args, my_name, return_deep=True)
            return result

def all_together(*args
       , return_name: bool = False
       , return_shallow: bool = False
       , return_deep: bool = False) -> Set[str]:
    assert return_name + return_shallow + return_deep == 1
    nested_calls = [e,ee]
    nested_calls = set(nested_calls)
    my_name = inspect.stack()[0].function
    result = {my_name}
    args = set(args)
    if return_name:
        return result
    elif return_shallow:
        result |= {f.__name__ for f in nested_calls}
        return result
    else:  # return_deep == True
        if my_name in args:
            return args
        else:
            for f in nested_calls:
                result |= f(*args, my_name, return_deep=True)
            return result


def test_long_chain():
    all_funcs = [a,b,c,d,e,aa,bb,cc,dd,ee,all_together]
    assert (explore_call_graph_shallow(all_funcs) ==
            {f.__name__: f(return_shallow=True) for f in all_funcs})
    assert (explore_call_graph_deep(all_funcs) ==
            {f.__name__: f(return_deep=True) for f in all_funcs})