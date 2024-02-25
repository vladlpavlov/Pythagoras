

def get_all_decorator_names() -> set[str]:
    all_decorators = {"ordinary"}
    all_decorators |= {"autonomous", "strictly_autonomous"}
    all_decorators |= {"idempotent"}
    return all_decorators