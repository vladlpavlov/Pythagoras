from pythagoras._99_misc_utils.id_examiner import is_reserved_identifier

def test_is_reserved_identifier():
    assert is_reserved_identifier("__pth_") == True
    assert is_reserved_identifier("__pth_abc") == True
    assert is_reserved_identifier("pth_") == False
    assert is_reserved_identifier("pth_abc") == False
    assert is_reserved_identifier("__pth") == False
    assert is_reserved_identifier("__PTH__") == False
    assert is_reserved_identifier("__pth_abc__") == True
    assert is_reserved_identifier("pth") == False
    assert is_reserved_identifier("pth__") == False
    assert is_reserved_identifier("pth_abc__") == False
    assert is_reserved_identifier("__pth__abc") == True
    assert is_reserved_identifier("__init__") == False