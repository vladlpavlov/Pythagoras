from pythagoras._00_basic_utils.isinstance_txt import isinstance_txt

def test_builtins():
    assert isinstance_txt(5, "int")
    assert not isinstance_txt(5, "float")
    assert not isinstance_txt(5, "str")
    assert isinstance_txt(5.0, "float")
    assert not isinstance_txt(5.0, "int")
    assert not isinstance_txt(5.0, "str")
    assert isinstance_txt("test", "str")
    assert not isinstance_txt(True, "str")
    assert not isinstance_txt([1,2,3], "str")
    assert isinstance_txt([1,2,3], "list")
    assert not isinstance_txt([1,2,3], "tuple")
    assert isinstance_txt((1,2,3), "tuple")
    assert not isinstance_txt((1,2,3), "list")
    assert isinstance_txt({"a":1,"b":2}, "dict")

class A:
    pass

class B(A):
    pass

class C(A):
    pass

class D(B,C):
    pass


def test_classes():
    assert isinstance_txt(A(), "A")
    assert isinstance_txt(B(), "A")
    assert isinstance_txt(C(), "A")
    assert isinstance_txt(D(), "A")
    assert isinstance_txt(D(), "B")
    assert isinstance_txt(D(), "C")
    assert isinstance_txt(D(), "D")
    assert not isinstance_txt(A(), "B")
    assert not isinstance_txt(A(), "C")
    assert not isinstance_txt(A(), "D")
    assert not isinstance_txt(B(), "C")
    assert not isinstance_txt(B(), "D")
    assert not isinstance_txt(C(), "D")