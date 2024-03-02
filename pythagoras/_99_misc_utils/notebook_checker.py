def is_executed_in_notebook() -> bool:
    """ Return True if running inside a Jupyter notebook. """
    try:
        from IPython import get_ipython
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True
        else:
            return False
    except:
        return False