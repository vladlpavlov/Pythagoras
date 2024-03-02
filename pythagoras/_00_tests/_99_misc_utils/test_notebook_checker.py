from pythagoras._99_misc_utils.notebook_checker import is_executed_in_notebook

def test_is_executed_in_notebook():
    assert is_executed_in_notebook() == False
    #TODO: add test for when running inside a notebook
