

def get_function_name_from_source(a_func: str) -> str:
    lines = a_func.split('\n')
    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith('def '):
            func_name_end = stripped_line.find('(')
            func_name = stripped_line[3:func_name_end]
            return func_name.strip()
    raise ValueError(f"Can't find function name in {a_func=}")
