from pythagoras import ValueAddress
from pythagoras._04_idempotent_functions.kw_args import PackedKwArgs
from pythagoras._07_mission_control.global_state_management import _clean_global_state, \
    initialize


def test_packed_kwargs(tmpdir):
    """Test PackedKwArgs constructor and basic functions."""
    _clean_global_state()
    initialize(base_dir=tmpdir, n_background_workers=0)

    sampe_dict = { "e": 0, "c":1, "b":2, "a":3}
    assert list(sampe_dict.keys()) != sorted(sampe_dict.keys())

    pka = PackedKwArgs(**sampe_dict)
    assert list(pka.keys()) == sorted(pka.keys())

    for k in pka:
        assert pka[k] == ValueAddress(sampe_dict[k])

    assert pka.unpack() == sampe_dict
    assert pka == PackedKwArgs(**pka.unpack())