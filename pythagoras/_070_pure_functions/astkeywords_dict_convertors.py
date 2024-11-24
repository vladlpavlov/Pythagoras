import ast

def convert_astkeywords_to_dict(ast_keywords:list[ast.keyword]) -> dict:
    """
    Convert a list of ast.keyword objects into a dictionary.

    Parameters:
    - keywords: A list of ast.keyword objects.

    Returns:
    - A dictionary where keys are the argument names and values are the argument values.
    """
    result = {}
    for keyword in ast_keywords:
        assert isinstance(keyword, ast.keyword)
        key = keyword.arg
        value = ast.literal_eval(keyword.value)
        result[key] = value
    return result

def convert_dict_to_astkeywords(d:dict) -> list[ast.keyword]:
    """
    Convert a dictionary into a list of ast.keyword objects.

    Parameters:
    - d: A dictionary.

    Returns:
    - A list of ast.keyword objects.
    """
    result = []
    for key, value in d.items():
        keyword = ast.keyword(arg=key, value=ast.Str(value))
        result.append(keyword)
    return result
