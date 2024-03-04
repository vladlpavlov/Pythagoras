from pythagoras._05_events_and_exceptions.notebook_checker import is_executed_in_notebook

def test_is_executed_in_notebook():
    assert is_executed_in_notebook() == False
    #TODO: add test for when running inside a notebook
