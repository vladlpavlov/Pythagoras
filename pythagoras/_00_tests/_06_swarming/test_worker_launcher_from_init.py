import pythagoras as pth

def test_launch_background_worker_from_init(tmpdir):

    with pth.initialize(tmpdir, n_background_workers=1):

        @pth.idempotent()
        def sample_f(s:str) -> str:
            return 2*s

        address = sample_f.swarm(s="hello")
        assert address.get() == "hellohello"

