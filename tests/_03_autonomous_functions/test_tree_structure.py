from pythagoras import autonomous


@autonomous("kuku")
def f_1():
    return 0

@autonomous("kuku")
def f_2():
    return 0

@autonomous("kuku")
def f_3():
    return 0

@autonomous("kuku")
def f_4():
    return 0

@autonomous("kuku")
def f_5():
    return 0

@autonomous("kuku")
def f_6():
    return 0

@autonomous("kuku")
def f_1_2():
    return f_1() + f_2()

@autonomous("kuku")
def f_2_3():
    return f_2() + f_3()

@autonomous("kuku")
def f_3_4():
    return f_3() + f_4()

@autonomous("kuku")
def f_4_5():
    return f_4() + f_5()

@autonomous("kuku")
def f_5_6():
    return f_5() + f_6()

@autonomous("kuku")
def f_1_2_3():
    return f_1_2() + f_2_3()

@autonomous("kuku")
def f_2_3_4():
    return f_2_3() + f_3_4()

@autonomous("kuku")
def f_3_4_5():
    return f_3_4() + f_4_5()

@autonomous("kuku")
def f_4_5_6():
    return f_4_5() + f_5_6()

@autonomous("kuku")
def total():
    return f_1_2_3() + f_2_3_4() + f_3_4_5() + f_4_5_6()


def test_tree():
    assert total() == 0

