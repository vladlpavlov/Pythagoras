from pythagoras import ValueAddr, DataPortal
from pythagoras import _PortalTester
from pythagoras import SortedKwArgs


def test_sortedkwargs(tmpdir):
    """Test PackedKwArgs constructor and basic functionality."""

    with _PortalTester(DataPortal, root_dict=tmpdir) as t:

        sampe_dict = { "e": 0, "c":1, "b":2, "a":3}
        assert list(sampe_dict.keys()) != sorted(sampe_dict.keys())

        pka = SortedKwArgs(**sampe_dict).pack(t.portal)
        assert list(pka.keys()) == sorted(pka.keys())

        for k in pka:
            assert pka[k] == ValueAddr(sampe_dict[k])

        assert SortedKwArgs(**pka).unpack() == sampe_dict


def test_sortedkwargs_2portals(tmpdir):
    with _PortalTester(DataPortal, root_dict=tmpdir.mkdir("t1")) as t:
        p1 = t.portal
        p2 = DataPortal(root_dict=tmpdir.mkdir("t2"))
        sampe_dict = { "e": 0, "c":1, "b":2, "a":3}
        pka = SortedKwArgs(**sampe_dict).pack(p1)
        assert len(p1.value_store) == 4
        assert len(p2.value_store) == 0

        pka = SortedKwArgs(**pka).pack(p2)
        assert len(p1.value_store) == 4
        assert len(p2.value_store) == 4

        pka = SortedKwArgs(**pka).pack(p1)
        pka = SortedKwArgs(**pka).pack(p2)

        assert len(p1.value_store) == 4
        assert len(p2.value_store) == 4


def test_sortedkwargs_save_load(tmpdir):
    """Test PackedKwArgs constructor and basic functionality."""

    with _PortalTester(DataPortal, root_dict=tmpdir) as t:
        portal = t.portal
        sampe_dict = { "e": 0, "c":1, "b":2, "a":3}
        pka = SortedKwArgs(**sampe_dict).pack(t.portal)
        portal.value_store["PKA"] = pka
        new_pka = portal.value_store["PKA"]
        assert new_pka == pka
        assert type(new_pka) == type(pka) == SortedKwArgs

