
_is_in_notebook: bool|None = None
def is_executed_in_notebook() -> bool:
    """ Return True if running inside a Jupyter notebook. """
    global _is_in_notebook
    if _is_in_notebook is not None:
        return _is_in_notebook
    _is_in_notebook = False
    try:
        from IPython import get_ipython
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            _is_in_notebook = True
            return True
        else:
            return False
    except:
        return False