from pythagoras._99_misc_utils.decorator_names import get_all_decorator_names

def test_get_all_decorator_names():
    all_names = get_all_decorator_names()
    assert len(all_names) == 4
    assert "ordinary" in all_names
    assert "autonomous" in all_names
    assert "strictly_autonomous" in all_names
    assert "idempotent" in all_names
