from pythagoras import ValueAddr
from pythagoras.___04_idempotent_functions.kw_args import SortedKwArgs
from pythagoras.___07_mission_control.global_state_management import (
    _force_initialize)

import pythagoras as pth


def test_sortedkwargs(tmpdir):
    """Test PackedKwArgs constructor and basic functionality."""

    with _force_initialize(base_dir=tmpdir, n_background_workers=0):

        sampe_dict = { "e": 0, "c":1, "b":2, "a":3}
        assert list(sampe_dict.keys()) != sorted(sampe_dict.keys())

        pka = SortedKwArgs(**sampe_dict).pack(pth.default_portal)
        assert list(pka.keys()) == sorted(pka.keys())

        for k in pka:
            assert pka[k] == ValueAddr(sampe_dict[k])

        assert SortedKwArgs(**pka).unpack(pth.default_portal) == sampe_dict
