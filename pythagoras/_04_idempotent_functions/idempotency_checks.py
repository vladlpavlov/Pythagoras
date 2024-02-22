import pythagoras as pth


def is_idempotent(a_func):
    assert isinstance(a_func, type(is_idempotent))
    if not hasattr(a_func, "__pth_cloudized_function__"):
        return False
    if not isinstance(a_func.__pth_cloudized_function__, pth.IdempotentFunction):
        return False
    return True