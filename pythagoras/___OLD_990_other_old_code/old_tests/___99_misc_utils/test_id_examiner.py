from pythagoras.___99_misc_utils.id_examiner import is_reserved_identifier

def test_is_reserved_identifier():
    assert is_reserved_identifier("_pth_") == True
    assert is_reserved_identifier("_pth_abc") == True
    assert is_reserved_identifier("pth_") == False
    assert is_reserved_identifier("pth_abc") == False
    assert is_reserved_identifier("_pth") == False
    assert is_reserved_identifier("_PTH__") == False
    assert is_reserved_identifier("_pth_abc__") == True
    assert is_reserved_identifier("pth") == False
    assert is_reserved_identifier("__pth__") == False
    assert is_reserved_identifier("pth_abc__") == False
    assert is_reserved_identifier("_pth__abc") == True
    assert is_reserved_identifier("__init__") == False